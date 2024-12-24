from file_manager import File
from pydantic import BaseModel, Field


class AnswerAppealDCScheme(BaseModel):
    text: str = Field(
        title="Комментарий",
    )


class AnswerAppealDUScheme(BaseModel):
    text: str = Field(
        title="Комментарий",
    )
    files: list[File] = Field(
        default_factory=list,
        title="Файлы вложения",
    )
