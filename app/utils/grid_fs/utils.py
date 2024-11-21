"""
Модуль с дополнительными утилитами для работы с файлами
"""

from fastapi import HTTPException
from starlette import status

from utils.grid_fs.constants import ContentType, FileExtensionGroup


def get_content_type_by_filename(
    filename: str,
    allowed_file_extensions: FileExtensionGroup = FileExtensionGroup.ALL,
    with_default: bool = False,
) -> ContentType:
    """
    Функция для определения заголовка Content-Type по расширению файла

    Args:
        filename (str): Название файла
    """
    filename_split = filename.split(".")
    if len(filename_split) < 2:
        if with_default:
            return ContentType.DEFAULT
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension",
        )
    extension = filename_split[-1].lower()
    content_type = allowed_file_extensions.content_type_map.get(extension, ContentType.DEFAULT if with_default else None)
    if not content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension",
        )
    return content_type
