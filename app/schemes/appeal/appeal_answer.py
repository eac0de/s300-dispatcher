from file_manager import File
from pydantic import BaseModel, Field


class AnswerAppealDCScheme(BaseModel):
    text: str = Field(
        default="",
        title="Комментарий",
    )


class AnswerAppealDUScheme(BaseModel):
    files: list[File] = Field(
        default_factory=list,
        title="Файлы вложения",
    )
