"""
Модуль с фильтрами для query параметров запросов к шаблонам заявок
"""

from qp_translator import Filter, QPTranslator, str_parsers

from models.request.categories_tree import RequestCategory
from models.request_template.constants import RequestTemplateType


class DispatcherRequestTemplateQPTranslator(QPTranslator):
    """
    Класс с фильтрами для шаблонов заявок диспетчера
    """

    __filters__ = {
        "type": Filter[RequestTemplateType](
            q_func=lambda x: {"_type": x},
            t_parser=str_parsers.get_enum_parser(RequestTemplateType),
            description="Тип шаблона заявки",
        ),
        "category": Filter[RequestCategory](
            q_func=lambda x: {"category": x},
            t_parser=str_parsers.get_enum_parser(RequestCategory),
            description="Категория",
        ),
    }
