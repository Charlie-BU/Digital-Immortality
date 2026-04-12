import json
import logging
import os
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.graphs.FRBuildingGraph.state import FRBuildingGraphState
from src.agents.llm import prepareLLM
from src.agents.prompt import getPrompt
from src.database.enums import (
    FigureRole,
    FineGrainedFeedConfidence,
    FineGrainedFeedDimension,
    OriginalSourceType,
    parseEnum,
)
from src.database.index import session
from src.database.models import OriginalSource
from src.services.fine_grained_feed import addOriginalSource
from src.utils.index import checkFigureAndRelationOwnership

logger = logging.getLogger(__name__)


def nodeLoadFR(state: FRBuildingGraphState) -> dict:
    """
    加载当前 figure_and_relation 和 figure_role
    """
    request = state["request"]
    with session() as db:
        figure_and_relation = checkFigureAndRelationOwnership(
            db=db, user_id=request["user_id"], fr_id=request["fr_id"]
        )
        if figure_and_relation is None:
            logger.error("Figure and relation not found")
            raise ValueError("Figure and relation not found")

        return {
            "figure_and_relation": figure_and_relation.toJson(),
            "figure_role": parseEnum(FigureRole, figure_and_relation.figure_role),
        }


async def nodePreprocessInput(state: FRBuildingGraphState) -> dict:
    """
    预处理 raw_content 和 raw_images（如有）
    """
    request = state["request"]
    raw_content = (request.get("raw_content") or "").strip()
    raw_images = request.get("raw_images") or []

    # 空判定
    if raw_content == "" and len(raw_images) == 0:
        logger.error("raw_content and raw_images cannot be both empty")
        raise ValueError("raw_content and raw_images cannot be both empty")
    # 内容过短
    if raw_content and len(raw_content) < 10:
        logger.warning(
            "raw_content is too short, it may not contain enough information"
        )
        raise ValueError(
            "raw_content is too short, it may not contain enough information"
        )

    # LLM 预处理
    llm = prepareLLM(
        "DOUBAO_2_0_MINI", options={"temperature": 0, "reasoning_effort": "low"}
    )
    FR_BUILDING_PREPROCESS_SYSTEM_PROMPT = await getPrompt(
        os.getenv("FR_BUILDING_PREPROCESS_SYSTEM_PROMPT")
    )
    FR_BUILDING_PREPROCESS_INPUT = await getPrompt(
        os.getenv("FR_BUILDING_PREPROCESS_INPUT"),
        {"figure_role": state["figure_role"].value, "raw_content": raw_content},
    )
    user_prompt = FR_BUILDING_PREPROCESS_INPUT
    if raw_images:
        user_prompt = [{"type": "text", "text": FR_BUILDING_PREPROCESS_INPUT}] + [
            {"type": "image_url", "image_url": {"url": url}} for url in raw_images
        ]

    messages = [
        SystemMessage(content=FR_BUILDING_PREPROCESS_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]
    response = await llm.ainvoke(messages)
    try:
        parsed_res = json.loads(response.content)
    except json.JSONDecodeError:
        logger.error("LLM response is not valid JSON")
        raise ValueError("LLM response is not valid JSON")

    # logger.info(json.dumps(parsed_res, ensure_ascii=False, indent=2))
    cleaned_content = parsed_res.get("cleaned_content", "")
    metadata = parsed_res.get("metadata", {})
    original_source_draft = {
        "content": cleaned_content,
        "type": parseEnum(OriginalSourceType, metadata.get("original_source_type")),
        "confidence": parseEnum(
            FineGrainedFeedConfidence, metadata.get("confidence", "")
        ),
        "included_dimensions": [
            parseEnum(FineGrainedFeedDimension, dim)
            for dim in metadata.get("included_dimensions", [])
        ],
        "approx_date": metadata.get("approx_date"),
    }

    return {
        "original_source_draft": original_source_draft,
    }


def nodePersistOriginalSource(state: FRBuildingGraphState) -> dict:
    """
    original_source 落库
    """
    original_source_draft = state["original_source_draft"]
    res = addOriginalSource(
        user_id=state["request"]["user_id"],
        fr_id=state["request"]["fr_id"],
        **original_source_draft
    )
    if res["status"] != 200:
        logger.error(res.get("message", "Add original source failed"))
        raise ValueError("Add original source failed")
    
    return {
        "original_source_id": res.get("original_source_id"),
    }
