"""
Модуль с фильтрами для query параметров запросов к каталогу
"""

from qp_translator import Filter, QPTranslator, str_parsers

from models.catalog_item.constants import CatalogItemGroup


class DispatcherCatalogQPTranslator(QPTranslator):
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
            t_parser=str_parsers.get_enum_parser(CatalogItemGroup),
            description="Группа позиций",
        ),
    }


class TenantCatalogQPTranslator(QPTranslator):
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
            t_parser=str_parsers.get_enum_parser(CatalogItemGroup),
            description="Группа позиций",
        ),
    }
