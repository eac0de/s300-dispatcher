"""
Модуль с дополнительным классом для заявки - вложения
"""

from pydantic import BaseModel, Field

from utils.grid_fs.file import File


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
