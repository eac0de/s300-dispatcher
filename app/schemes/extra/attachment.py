"""
Модуль с дополнительным классом для заявки - вложения
"""

from file_manager import File
from pydantic import BaseModel, Field


class ExpandedAttachmentCScheme(BaseModel):
    comment: str = Field(
        default="",
        title="Комментарий",
    )


class ExpandedAttachmentUScheme(BaseModel):
    comment: str = Field(
        default="",
        title="Комментарий",
    )
    files: list[File] = Field(
        default_factory=list,
        title="Файлы вложения",
    )


class ExpandedAttachmentUWithoutCommentScheme(BaseModel):
    files: list[File] = Field(
        default_factory=list,
        title="Файлы вложения",
    )
