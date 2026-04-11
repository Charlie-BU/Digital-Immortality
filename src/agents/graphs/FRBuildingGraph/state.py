from typing import TypedDict


class Request(TypedDict, total=False):
    user_id: int
    fr_id: int
    raw_content: str    # 原始文本内容
    raw_images: list[str] | None    # 原始图片url

