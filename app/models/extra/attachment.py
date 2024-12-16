"""
Модуль с дополнительным классом для заявки - вложения
"""

from file_manager import File
from pydantic import BaseModel, Field


class Attachment(BaseModel):
    """
    Класс вложения
    """

    files: list[File] = Field(
        default_factory=list,
        title="Файлы вложения",
    )
    comment: str = Field(
        default="",
        title="Комментарий",
    )
