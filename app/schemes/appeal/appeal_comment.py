from file_manager import File
from pydantic import BaseModel, Field


class AppealCommentDCScheme(BaseModel):
    text: str = Field(
        title="Текст комментария",
    )


class AppealCommentDUScheme(BaseModel):
    text: str | None = Field(
        title="Текст комментария",
    )
    files: list[File] | None = Field(
        default=None,
        title="Файлы вложения",
    )
