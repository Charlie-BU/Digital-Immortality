from datetime import datetime, timezone
import math
import os
from sqlalchemy.orm import Session

from src.database.models import FigureAndRelation, OriginalSource


def cleanList(items: list):
    """
    清理列表中的重复字符串项，保留首次出现的项。
    参数:
    items (list): 包含字符串的列表。
    返回:
    list: 清理后的列表，仅包含唯一的非空字符串项。
    """
    if not items:
        return []
    result = []
    seen = set()
    for item in items:
        if not isinstance(item, str):
            continue
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def timeDecay(created_at: datetime) -> float:
    """
    时间衰减函数
    """
    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    delta_days = (now - created_at).days

    return math.exp(-delta_days / int(os.getenv("HALF_LIFE_DAYS")))


def checkFigureAndRelationOwnership(
    db: Session, user_id: int, fr_id: int
) -> FigureAndRelation | None:
    """
    FigureAndRelation 归属校验
    """
    return (
        db.query(FigureAndRelation)
        .filter(
            FigureAndRelation.id == fr_id,
            FigureAndRelation.user_id == user_id,
            FigureAndRelation.is_deleted == False,
        )
        .first()
    )


def checkOriginalSourceOwnership(
    db,
    user_id: int,
    fr_id: int,
    original_source_id: int,
) -> OriginalSource | None:
    """
    OriginalSource 归属校验
    """
    original_source: OriginalSource | None = (
        db.query(OriginalSource)
        .filter(
            OriginalSource.id == original_source_id,
            OriginalSource.fr_id == fr_id,
            OriginalSource.is_deleted == False,
        )
        .first()
    )
    if original_source is None:
        return None
    if original_source.figure_and_relation.user_id != user_id:
        return None
    return original_source
