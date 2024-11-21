"""
Модуль с константами для работы с файлами
"""

from enum import Enum


class ContentType(str, Enum):
    """
    Типы контента файлов
    """

    DEFAULT = "application/octet-stream"
    PDF = "application/pdf"
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    XLS = "application/vnd.ms-excel"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    PPT = "application/vnd.ms-powerpoint"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    TXT = "text/plain"
    CSV = "text/csv"
    JSON = "application/json"
    XML = "application/xml"
    HTML = "text/html"
    JPG = "image/jpeg"
    PNG = "image/png"
    GIF = "image/gif"
    BMP = "image/bmp"
    TIFF = "image/tiff"
    MP3 = "audio/mpeg"
    WAV = "audio/wav"
    MP4 = "video/mp4"
    MOV = "video/quicktime"
    AVI = "video/x-msvideo"
    ZIP = "application/zip"
    GZ = "application/gzip"
    TAR = "application/x-tar"
    RAR = "application/x-rar-compressed"


class FileExtensionGroup(str, Enum):
    """
    Группы расширений файлов
    """

    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    ALL = "all"

    @property
    def content_type_map(self) -> dict[str, ContentType]:
        """
        Получение карты типов контента файла

        Returns:
            dict[str, ContentType]: Карта типов контента файла
        """
        if self == FileExtensionGroup.IMAGE:
            return IMAGE_CONTENT_TYPE_MAP
        if self == FileExtensionGroup.VIDEO:
            return VIDEO_CONTENT_TYPE_MAP
        if self == FileExtensionGroup.DOCUMENT:
            return DOCUMENT_CONTENT_TYPE_MAP
        return CONTENT_TYPE_MAP


# Фото файлы
IMAGE_CONTENT_TYPE_MAP = {
    "jpg": ContentType.JPG,
    "jpeg": ContentType.JPG,
    "png": ContentType.PNG,
    "gif": ContentType.GIF,
    "bmp": ContentType.BMP,
    "tiff": ContentType.TIFF,
}

# Видео файлы
VIDEO_CONTENT_TYPE_MAP = {
    "mp4": ContentType.MP4,
    "mov": ContentType.MOV,
    "avi": ContentType.AVI,
}

DOCUMENT_CONTENT_TYPE_MAP = {
    "pdf": ContentType.PDF,
    "doc": ContentType.DOC,
    "docx": ContentType.DOCX,
    "xls": ContentType.XLS,
    "xlsx": ContentType.XLSX,
    "ppt": ContentType.PPT,
    "pptx": ContentType.PPTX,
    "txt": ContentType.TXT,
    "csv": ContentType.CSV,
}

OTHER_CONTENT_TYPE_MAP = {
    "json": ContentType.JSON,
    "xml": ContentType.XML,
    "html": ContentType.HTML,
    "mp3": ContentType.MP3,
    "wav": ContentType.WAV,
    "zip": ContentType.ZIP,
    "gz": ContentType.GZ,
    "tar": ContentType.TAR,
    "rar": ContentType.RAR,
}


CONTENT_TYPE_MAP = {
    **IMAGE_CONTENT_TYPE_MAP,
    **VIDEO_CONTENT_TYPE_MAP,
    **DOCUMENT_CONTENT_TYPE_MAP,
    **OTHER_CONTENT_TYPE_MAP,
}


class FileEncoding(str, Enum):
    """
    Кодировки файлов
    """

    UTF_8 = "utf-8"
    CP1251 = "cp1251"
