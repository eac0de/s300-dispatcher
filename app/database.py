"""
Модуль инициализации базы данных

Данный модуль отвечает за подключение к MongoDB и инициализацию моделей документов с использованием Beanie и Motor.
"""

from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from client.c300.models.area import AreaC300
from client.c300.models.employee import EmployeeC300
from client.c300.models.house import HouseC300
from client.c300.models.provider import ProviderC300
from client.c300.models.tenant import TenantC300
from config import settings
from models.catalog_item.catalog_item import CatalogItem
from models.other.other_employee import OtherEmployee
from models.other.other_person import OtherPerson
from models.other.other_provider import OtherProvider
from models.request.archived_request import ArchivedRequestModel
from models.request.request import RequestModel
from models.request_history.request_history import RequestHistory
from models.request_template.request_template import RequestTemplate
from utils.request.request_log import RequestLog


async def init_db(*docs: type[Document]):
    """Инициализация подключения к базе данных и моделей документов.

    Эта функция создает асинхронное соединение с MongoDB и инициализирует модели документов
    для двух различных баз данных: основной и логов.

    Args:
        *docs: Дополнительные модели документов, которые могут быть переданы при вызове функции.

    В процессе инициализации происходит следующее:
    1. Устанавливается соединение с MongoDB с использованием URI из настроек.
    2. Инициализируются модели документов для основной базы данных.
    3. Инициализируются модели документов для базы данных логов.
    """
    client = AsyncIOMotorClient(str(settings.MONGO_URI))

    await init_beanie(
        database=client.get_database(settings.MAIN_DB),
        document_models=[
            RequestModel,
            ArchivedRequestModel,
            TenantC300,
            EmployeeC300,
            HouseC300,
            AreaC300,
            ProviderC300,
            RequestHistory,
            CatalogItem,
            RequestTemplate,
            OtherPerson,
            OtherEmployee,
            OtherProvider,
            *docs,
        ],
    )
    await init_beanie(
        database=client.get_database(settings.LOGS_DB),
        document_models=[
            RequestLog,
        ],
    )
