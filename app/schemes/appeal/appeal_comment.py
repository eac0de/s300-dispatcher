from beanie import Document
from file_manager import File
from pydantic import BaseModel, Field


class AppealCommentDCScheme(Document):
    text: str = Field(
        title="Текст комментария",
    )


class AppealCommentDUScheme(BaseModel):
    files: list[File] = Field(
        default_factory=list,
        title="Файлы вложения",
    )
