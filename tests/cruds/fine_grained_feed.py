import asyncio

from dotenv import load_dotenv

load_dotenv()

from src.database.enums import FineGrainedFeedConfidence, FineGrainedFeedDimension
from src.services.fine_grained_feed import (
    addFineGrainedFeed,
    addFineGrainedFeedConflict,
    addOriginalSource,
    deleteFineGrainedFeed,
    deleteOriginalSource,
    getAllFineGrainedFeed,
    getAllFineGrainedFeedConflict,
    getAllOriginalSource,
    getFineGrainedFeed,
    getFineGrainedFeedConflict,
    getOriginalSource,
    hardDeleteFineGrainedFeedConflict,
    resolveFineGrainedFeedConflict,
    updateFineGrainedFeed,
)


def testAddOriginalSource(fr_id: int):
    res = addOriginalSource(
        user_id=1,
        fr_id=fr_id,
        confidence=FineGrainedFeedConfidence.VERBATIM,
        included_dimensions=[
            FineGrainedFeedDimension.PERSONALITY,
            FineGrainedFeedDimension.MEMORY,
        ],
        content="她在团队讨论里非常理性，也会主动照顾新成员。",
        approx_date="2026-01-20",
    )
    return res


def testDeleteOriginalSource(fr_id: int, original_source_id: int):
    res = deleteOriginalSource(
        user_id=1,
        fr_id=fr_id,
        original_source_id=original_source_id,
    )
    return res


def testGetOriginalSource(fr_id: int, original_source_id: int):
    res = getOriginalSource(
        user_id=1,
        fr_id=fr_id,
        original_source_id=original_source_id,
    )
    return res


def testGetAllOriginalSource(fr_id: int):
    res = getAllOriginalSource(
        user_id=1,
        fr_id=fr_id,
    )
    return res


async def testAddFineGrainedFeed(fr_id: int, original_source_id: int):
    res = await addFineGrainedFeed(
        user_id=1,
        fr_id=fr_id,
        original_source_id=original_source_id,
        dimension=FineGrainedFeedDimension.INTERACTION_STYLE,
        confidence=FineGrainedFeedConfidence.IMPRESSION,
        content="她通常先倾听，再用很温和的方式给建议。",
        sub_dimension="沟通偏好",
    )
    return res


def testDeleteFineGrainedFeed(fr_id: int, fine_grained_feed_id: int):
    res = deleteFineGrainedFeed(
        user_id=1,
        fr_id=fr_id,
        fine_grained_feed_id=fine_grained_feed_id,
    )
    return res


async def testUpdateFineGrainedFeed(
    fr_id: int,
    fine_grained_feed_id: int,
    new_original_source_id: int,
):
    res = await updateFineGrainedFeed(
        user_id=1,
        fr_id=fr_id,
        fine_grained_feed_id=fine_grained_feed_id,
        new_original_source_id=new_original_source_id,
        new_content="她会在冲突出现前先确认彼此目标，避免误解。",
        new_sub_dimension="冲突处理",
    )
    return res


def testGetFineGrainedFeed(fr_id: int, fine_grained_feed_id: int):
    res = getFineGrainedFeed(
        user_id=1,
        fr_id=fr_id,
        fine_grained_feed_id=fine_grained_feed_id,
    )
    return res


def testGetAllFineGrainedFeed(fr_id: int):
    res = getAllFineGrainedFeed(
        user_id=1,
        fr_id=fr_id,
    )
    return res


def testAddFineGrainedFeedConflict(fr_id: int, feed_ids: list[int]):
    res = addFineGrainedFeedConflict(
        user_id=1,
        fr_id=fr_id,
        dimension=FineGrainedFeedDimension.PERSONALITY,
        feed_ids=feed_ids,
        description="同一人物在不同时间表现出外向与内向两种明显特征。",
        resolved=False,
    )
    return res


def testHardDeleteFineGrainedFeedConflict(fr_id: int, fine_grained_feed_conflict_id: int):
    res = hardDeleteFineGrainedFeedConflict(
        user_id=1,
        fr_id=fr_id,
        fine_grained_feed_conflict_id=fine_grained_feed_conflict_id,
    )
    return res


def testResolveFineGrainedFeedConflict(fr_id: int, fine_grained_feed_conflict_id: int):
    res = resolveFineGrainedFeedConflict(
        user_id=1,
        fr_id=fr_id,
        fine_grained_feed_conflict_id=fine_grained_feed_conflict_id,
    )
    return res


def testGetFineGrainedFeedConflict(fr_id: int, fine_grained_feed_conflict_id: int):
    res = getFineGrainedFeedConflict(
        user_id=1,
        fr_id=fr_id,
        fine_grained_feed_conflict_id=fine_grained_feed_conflict_id,
    )
    return res


def testGetAllFineGrainedFeedConflict(
    fr_id: int,
    scope: str = "unresolved",
):
    res = getAllFineGrainedFeedConflict(
        user_id=1,
        fr_id=fr_id,
        scope=scope,
    )
    return res


if __name__ == "__main__":
    # print(testAddOriginalSource(fr_id=1))
    # print(asyncio.run(testAddFineGrainedFeed(fr_id=1, original_source_id=1)))
    print(testDeleteFineGrainedFeed(fr_id=1, fine_grained_feed_id=1))
    print(testDeleteOriginalSource(fr_id=1, original_source_id=1))
   
