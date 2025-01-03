from file_manager import File
from pydantic import BaseModel, Field


class AnswerAppealDCScheme(BaseModel):
    text: str = Field(
        title="Комментарий",
    )


class AnswerAppealDUScheme(BaseModel):
    text: str | None = Field(
        default=None,
        title="Комментарий",
    )
    files: list[File] | None = Field(
        default=None,
        title="Файлы вложения",
    )
