"""
Модуль модели файла.

Этот модуль содержит класс `File`, который предоставляет методы для работы с файлами,
сохраняемыми в GridFS. Он позволяет загружать, загружать на диск, удалять файлы
и взаимодействовать с ними.

Классы:
    - File: Модель для работы с файлами в GridFS.
"""

import logging
import os
from typing import Self

import aiofiles
import gridfs
from beanie import PydanticObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorGridOut
from pydantic import BaseModel, Field
from starlette import status

from utils.grid_fs.constants import ContentType, FileEncoding, FileExtensionGroup
from utils.grid_fs.grid_fs import grid_fs_service
from utils.grid_fs.utils import get_content_type_by_filename

UNKNOWN_FILE_TAG = "unknown"


class File(BaseModel):
    """Модель с методами для работы с файлами в GridFS."""

    id: PydanticObjectId = Field(
        alias="_id",
        title="id файла",
    )
    name: str = Field(
        title="Название файла",
    )
    content_type: ContentType = Field(
        default=ContentType.DEFAULT,
        title="Тип файла для заголовка Content-Type",
    )
    tag: str = Field(
        default=UNKNOWN_FILE_TAG,
        title="Тег файла",
    )
    encoding: FileEncoding = Field(
        default=FileEncoding.UTF_8,
        title="Кодировка файла",
    )

    async def read(self) -> bytes:
        """
        Чтение файла из GridFS.

        Returns:
            bytes: Содержимое файла в виде байтов.

        Notes:
            - Может возникнуть ошибка от библиотеки motor во время выполнения.
        """
        grid_out = await grid_fs_service.download_file(self.id)
        return await grid_out.read()

    async def open_stream(self) -> AsyncIOMotorGridOut:
        """
        Получение объекта для чтения файла из GridFS.

        Returns:
            AsyncIOMotorGridOut: Объект для чтения файла из GridFS.

        Notes:
            - Может возникнуть ошибка от библиотеки motor во время выполнения.
        """
        return await grid_fs_service.fs.open_download_stream(self.id)

    @classmethod
    async def download_file_from_disk(
        cls,
        filename: str,
        filepath: str = "",
        tag: str = UNKNOWN_FILE_TAG,
        encoding: FileEncoding = FileEncoding.UTF_8,
        mode: str = "r",
    ) -> Self | None:
        """
        Загрузка файла с диска в GridFS.

        Args:
            filename (str): Название файла.
            filepath (str): Путь к директории с файлом.
            tag (str): Тег файла.
            encoding (FileEncoding): Кодировка файла.

        Returns:
            File | None: Загруженный файл или None в случае ошибки.

        Notes:
            - Может возникнуть ошибка от библиотек motor и aiofiles во время выполнения.
        """
        try:
            async with aiofiles.open(filepath + filename, mode, encoding=encoding) as f:  # type: ignore
                content_type = get_content_type_by_filename(
                    filename=filename,
                    with_default=True,
                )
                metadata = {
                    "content_type": content_type,
                    "tag": tag,
                    "encoding": encoding,
                }
                file_id = await grid_fs_service.upload_file(
                    await f.read(),
                    filename,
                    metadata=metadata,
                )
                file = cls(
                    _id=PydanticObjectId(file_id),
                    name=filename,
                    content_type=content_type,
                    tag=tag,
                    encoding=encoding,
                )
            return file
        except Exception as e:
            print("Error while downloading file to disk: %s", e)
            logging.error("Error while downloading file to disk: %s", e)
            return None

    async def upload_file_to_disk(self, filepath: str) -> bool:
        """
        Загрузка файла из GridFS на диск.

        Args:
            filepath (str): Путь к директории, куда должен быть загружен файл.

        Returns:
            bool: Успех операции.

        Notes:
            - Может возникнуть ошибка от библиотек motor и aiofiles во время выполнения.
        """

        try:
            async with aiofiles.open(filepath + self.name, "w", encoding=self.encoding) as f:
                data = (await self.read()).decode(self.encoding)
                await f.write(data)
            return True
        except Exception as e:
            logging.error("Error while writing file to disk: %s", e)
            return False

    async def delete_file_from_disk(
        self,
        filepath: str,
    ) -> bool:
        """
        Удаление файла с диска.

        Args:
            filepath (str): Путь к директории с файлом.

        Returns:
            bool: Успех операции.

        Notes:
            - Может возникнуть ошибка во время удаления файла.
        """

        try:
            os.remove(filepath + self.name)
            return True
        except Exception as e:
            logging.error("Error while removing file to disk: %s", e)
        return False

    async def delete(self) -> bool:
        """
        Удаление файла из GridFS.

        Returns:
            bool: Успех операции.
        """

        return await grid_fs_service.delete_file(self.id)

    @classmethod
    async def create(
        cls,
        file_content: bytes,
        filename: str | None,
        tag: str = UNKNOWN_FILE_TAG,
        encoding: FileEncoding = FileEncoding.UTF_8,
        allowed_file_extensions: FileExtensionGroup = FileExtensionGroup.ALL,
    ) -> Self:
        """
        Загрузка файла в GridFS.

        Args:
            file_content (bytes): Данные файла.
            filename (str | None): Название файла.
            tag (str): Тег файла.
            encoding (FileEncoding): Кодировка файла.

        Returns:
            File: Загруженный файл.

        Raises:
            HTTPException: Если имя файла пустое.

        Notes:
            - Может возникнуть ошибка от библиотеки motor во время выполнения.
        """
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name cannot be empty",
            )
        content_type = get_content_type_by_filename(
            filename=filename,
            allowed_file_extensions=allowed_file_extensions,
        )
        metadata = {"content_type": content_type, "tag": tag, "encoding": encoding}
        file_id = await grid_fs_service.upload_file(
            file_content,
            filename,
            metadata=metadata,
        )
        file = cls(
            _id=PydanticObjectId(file_id),
            name=filename,
            content_type=content_type,
            tag=tag,
            encoding=encoding,
        )
        return file

    @classmethod
    async def get(cls, file_id: PydanticObjectId) -> Self | None:
        """
        Получение файла из GridFS.

        Args:
            file_id (PydanticObjectId): Идентификатор файла.

        Returns:
            File | None: Файл или None, если не найден.

        Notes:
            - Может возникнуть ошибка от библиотеки motor во время выполнения.
        """
        try:
            grid_out = await grid_fs_service.download_file(file_id)
        except gridfs.NoFile:
            return None
        file = cls.__build_file(grid_out)
        return file

    @classmethod
    async def find(cls, query: dict) -> list[Self]:
        """
        Получение файлов из GridFS по параметрам запроса.

        Args:
            query (dict): Параметры запроса.

        Returns:
            list[File]: Список файлов.

        Notes:
            - Может возникнуть ошибка от библиотеки motor во время выполнения.
        """

        cursor = await grid_fs_service.find_files(query)

        return [cls.__build_file(f) async for f in cursor]

    @classmethod
    def __build_file(
        cls,
        grid_out: AsyncIOMotorGridOut,
    ):
        """
        Создание экземпляра File на основе данных из GridFS.

        Args:
            grid_out (AsyncIOMotorGridOut): Данные файла из GridFS.

        Returns:
            File: Созданный файл.
        """
        content_type = ContentType.DEFAULT
        tag = UNKNOWN_FILE_TAG
        encoding = FileEncoding.UTF_8
        if grid_out.metadata:
            try:
                content_type = ContentType(grid_out.metadata["content_type"])
            except:
                pass
            try:
                tag = grid_out.metadata["tag"]
            except:
                pass
            try:
                encoding = FileEncoding(grid_out.metadata["encoding"])
            except:
                pass
        return cls(
            _id=PydanticObjectId(grid_out._id),
            name=grid_out.filename if grid_out.filename else "Неизвестный файл",
            content_type=content_type,
            tag=tag,
            encoding=encoding,
        )
