from datetime import datetime

from beanie import PydanticObjectId
from models.appeal.constants import AppealSource, AppealStatus, AppealType
from qp_translator import Filter, QPTranslator, str_parsers


class DispatcherAppealsQPTranslator(QPTranslator):
    """
    Класс с фильтрами для обращений диспетчера
    """

    __filters__ = {
        "status__in": Filter[AppealStatus](
            q_func=lambda x: {"status": {"$in": x}},
            many=True,
            t_parser=str_parsers.get_enum_parser(AppealStatus),
            description="Статус обращения",
        ),
        "source__in": Filter[AppealSource](
            q_func=lambda x: {"source": {"$in": x}},
            many=True,
            t_parser=str_parsers.get_enum_parser(AppealSource),
            description="Источник обращения",
        ),
        "categories_id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"category_id": {"$in": x}},
            many=True,
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            description="Категории обращений",
        ),
        "number": Filter[str](
            q_func=lambda x: {"number": x},
            description="Номер обращения",
        ),
        "incoming_number": Filter[str](
            q_func=lambda x: {"incoming_number": x},
            description="Входящий номер обращения",
        ),
        "type__in": Filter[AppealType](
            q_func=lambda x: {"_type": {"$in": x}},
            many=True,
            t_parser=str_parsers.get_enum_parser(AppealType),
            description="Источник обращения",
        ),
        "created_at__gte": Filter[datetime](
            q_func=lambda x: {"created_at": {"$gte": x}},
            t_parser=str_parsers.datetime_parser,
            description="Дата подачи обращения (С)",
        ),
        "created_at__lt": Filter[datetime](
            q_func=lambda x: {"created_at": {"$lt": x}},
            t_parser=str_parsers.datetime_parser,
            description="Дата подачи обращения (По)",
        ),
        "appealer__house__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"appealer.house._id": {"$in": x}},
            many=True,
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            description="Адреса домов",
            exclusions=["appealer__area__id__in"],
        ),
        "appealer__area__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"appealer.area._id": {"$in": x}},
            many=True,
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            description="Квартиры",
        ),
        "executor__department__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"executor.department._id": {"$in": x}},
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            exclusions=["executor__position__id__in", "executor__id__in"],
            many=True,
            description="Исполнитель заявки (Отдел)",
        ),
        "executor__position__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"executor.position._id": {"$in": x}},
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            exclusions=["executor__id__in"],
            many=True,
            description="Исполнитель заявки (Должность)",
        ),
        "executor__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"executor._id": {"$in": x}},
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            many=True,
            description="Исполнитель заявки (Сотрудник)",
        ),
    }


class DispatcherAppealCommentsQPTranslator(QPTranslator):
    """
    Класс с фильтрами для обращений диспетчера
    """


class TenantAppealsQPTranslator(QPTranslator):
    """
    Класс с фильтрами для обращений диспетчера
    """
