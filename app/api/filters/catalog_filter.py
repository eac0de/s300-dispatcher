"""
Модуль с фильтрами для query параметров запросов к каталогу
"""

from utils.document_filter import DocumentFilter, Filter


class DispatcherCatalogFilter(DocumentFilter):
    """
    Класс с фильтрами для каталога диспетчера
    """

    __filters__ = {
        "name": Filter[str](
            q_func=lambda x: {"name": {"$regex": x, "$options": "i"}},
        ),
        "group": Filter[str](
            q_func=lambda x: {"group": x},
        ),
    }


class TenantCatalogFilter(DocumentFilter):
    """
    Класс с фильтрами для каталога жителя
    """

    __filters__ = {
        "name": Filter[str](
            q_func=lambda x: {"name": {"$regex": x, "$options": "i"}},
        ),
        "group": Filter[str](
            q_func=lambda x: {"group": x},
        ),
    }
