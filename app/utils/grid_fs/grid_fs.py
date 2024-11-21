"""
Модуль с сервисом для работы с файлами через GridFS
"""

from beanie import PydanticObjectId
from bson import ObjectId
from gridfs import NoFile
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorGridFSBucket,
    AsyncIOMotorGridOut,
    AsyncIOMotorGridOutCursor,
)

from config import settings


class GridFSService:
    """
    Сервис для работы с файлами через GridFS
    """

    _instance = None
    fs: AsyncIOMotorGridFSBucket

    def __new__(cls, *args, **kwargs):
        cls._instance = super().__new__(cls, *args, **kwargs)
        client = AsyncIOMotorClient(str(settings.MONGO_URI))
        db = client.get_database(settings.GRID_FS_DB)
        cls.fs = AsyncIOMotorGridFSBucket(db)
        return cls._instance

    async def upload_file(
        self,
        file_content: bytes | str,
        filename: str,
        metadata: dict,
    ) -> ObjectId:
        """
        Загрузка файла в grid_fs

        Args:
            file_content(bytes): Данные файла
            filename (list): Название файла
            metadata (dict): Метаданные файла

        Returns:
            ObjectId: Идентификатор загруженного файла

        Notes:
            - Функция может отдавать ошибки motor библиотеки в ходе выполнения
        """

        file_id = await self.fs.upload_from_stream(
            filename,
            file_content,
            metadata=metadata,
        )
        return file_id

    async def find_files(
        self,
        query: dict,
    ) -> AsyncIOMotorGridOutCursor:
        """
        Получение курсора на файлы из grid_fs по параметрам запроса

        Args:
            query(dict): Параметры запроса

        Returns:
            AsyncIOMotorGridOut: Курсор на файлы

        Notes:
            - Функция может отдавать ошибки motor библиотеки в ходе выполнения
        """

        files = self.fs.find(query)
        return files

    async def download_file(self, file_id: PydanticObjectId) -> AsyncIOMotorGridOut:
        """
        Получение файла из grid_fs

        Args:
            file_id(str | ObjectId | PydanticObjectId): Идентификатор файла

        Returns:
            AsyncIOMotorGridOut

        Notes:
            - Функция может отдавать ошибки motor библиотеки в ходе выполнения
        """

        return await self.fs.open_download_stream(file_id)

    async def delete_file(
        self,
        file_id: PydanticObjectId,
    ) -> bool:
        """
        Удаление файла из grid_fs

        Args:
            file_id(str | ObjectId | PydanticObjectId): Идентификатор файла

        Returns:
            bool: Был ли удален файл
        """

        try:
            await self.fs.delete(file_id)
            return True
        except NoFile:
            return False


grid_fs_service = GridFSService()


async def init_grid_fs_service():
    """
    Функция для инициализации сервиса в своем асинхронном цикле
    """
    global grid_fs_service
    grid_fs_service = GridFSService()
