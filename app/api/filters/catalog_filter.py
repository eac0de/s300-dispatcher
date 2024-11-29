"""
Модуль с фильтрами для query параметров запросов к каталогу
"""

from models.catalog_item.constants import CatalogItemGroup
from utils.document_filter import DocumentFilter, Filter, StandartParser


class DispatcherCatalogFilter(DocumentFilter):
    """
    Класс с фильтрами для каталога диспетчера
    """

    __filters__ = {
        "name": Filter[str](
            q_func=lambda x: {"name": {"$regex": x, "$options": "i"}},
            description="Название позиции",
        ),
        "group": Filter[CatalogItemGroup](
            q_func=lambda x: {"group": x},
            t_parser=StandartParser.get_enum_parser(CatalogItemGroup),
            description="Группа позиций",
        ),
    }


class TenantCatalogFilter(DocumentFilter):
    """
    Класс с фильтрами для каталога жителя
    """

    __filters__ = {
        "name": Filter[str](
            q_func=lambda x: {"name": {"$regex": x, "$options": "i"}},
            description="Название позиции",
        ),
        "group": Filter[CatalogItemGroup](
            q_func=lambda x: {"group": x},
            t_parser=StandartParser.get_enum_parser(CatalogItemGroup),
            description="Группа позиций",
        ),
    }
