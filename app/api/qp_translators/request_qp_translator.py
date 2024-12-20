"""
Модуль с фильтрами для query параметров запросов к заявкам
"""

from datetime import datetime, timedelta

from beanie import PydanticObjectId
from qp_translator import Filter, QPTranslator, str_parsers

from models.request.categories_tree import (
    RequestCategory,
    RequestSubcategory,
    RequestWorkArea,
)
from models.request.constants import (
    RequestSource,
    RequestStatus,
    RequestTag,
    RequestType,
)
from models.request.embs.action import ActionRSType


def area_range_parser(v: str) -> list[str]:
    """
    Парсинг строки со списком номеров квартир/подъездов.
    Допускает использование диапазонов.
        '1,2,3,4,5-20,60-67,80П,81Н,90-95П,100-120Н'
    """
    numbers = set()
    chunks = v.replace(" ", "").split(",")

    for chunk in chunks:
        if not chunk:
            continue

        area_type = chunk[-1].upper() if chunk[-1] in {"Н", "П", "н", "п"} else ""
        chunk = chunk[:-1] if area_type else chunk

        if "-" in chunk:
            low, high = chunk.split("-")
            if len(low) != 1 or len(high) != 1 or not all(n.isnumeric() for n in [low, high]):
                raise ValueError("Two numbers must be hyphenated and numeric")
            for number in range(int(low), int(high) + 1):
                numbers.add(str(number) + area_type)
        else:
            if not chunk.isnumeric():
                raise ValueError("All values must be numeric")
            numbers.add(chunk + area_type)

    if len(numbers) > 500:
        raise ValueError("Too many area numbers")
    return list(numbers)


class DispatcherRequestQPTranslator(QPTranslator):
    """
    Класс с фильтрами для заявок диспетчера
    """

    __filters__ = {
        "status__in": Filter[RequestStatus](
            q_func=lambda x: {"status": {"$in": x}},
            many=True,
            t_parser=str_parsers.get_enum_parser(RequestStatus),
            description="Статус заявки",
        ),
        "type": Filter[RequestType](
            q_func=lambda x: {"_type": x},
            t_parser=str_parsers.get_enum_parser(RequestType),
            description="Тип заявки",
        ),
        "source": Filter[RequestSource](
            q_func=lambda x: {"source": x},
            t_parser=str_parsers.get_enum_parser(RequestSource),
            description="Способ подачи",
        ),
        "house__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"house._id": {"$in": x}},
            many=True,
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            description="Адреса домов",
        ),
        "area_range": Filter[str](
            q_func=lambda x: {"area.number": {"$in": x}},
            t_parser=area_range_parser,
            description="Квартиры",
        ),
        "created_at__gte": Filter[datetime](
            q_func=lambda x: {"created_at": {"$gte": x}},
            t_parser=str_parsers.datetime_parser,
            description="Дата подачи заявки (С)",
        ),
        "created_at__lt": Filter[datetime](
            q_func=lambda x: {"created_at": {"$lt": x}},
            t_parser=str_parsers.datetime_parser,
            description="Дата подачи заявки (По)",
        ),
        "execution__end_at__gte": Filter[datetime](
            q_func=lambda x: {"execution.end_at": {"$gte": x}},
            t_parser=str_parsers.datetime_parser,
            description="Дата выполнения заявки (С)",
        ),
        "execution__end_at__lt": Filter[datetime](
            q_func=lambda x: {"execution.end_at": {"$lt": x}},
            t_parser=str_parsers.datetime_parser,
            description="Дата выполнения заявки (По)",
        ),
        "execution__desired_start_at__gte": Filter[datetime](
            q_func=lambda x: {"execution.desired_start_at": {"$gte": x}},
            t_parser=str_parsers.datetime_parser,
            description="Желаемое время выполнения заявки (С)",
        ),
        "execution__desired_end_at__lt": Filter[datetime](
            q_func=lambda x: {"execution.desired_end_at": {"$lt": x}},
            t_parser=str_parsers.datetime_parser,
            description="Желаемое время выполнения заявки (По)",
        ),
        "tenant__number": Filter[str](
            q_func=lambda x: {"requester.number": x},
            description="Номер лицевого счета",
        ),
        "administrative_supervision": Filter[bool](
            q_func=lambda x: {"administrative_supervision": x},
            t_parser=str_parsers.bool_parser,
            description="Дополнительные параметры заявки (Администрация района)",
        ),
        "housing_supervision": Filter[bool](
            q_func=lambda x: {"housing_supervision": x},
            t_parser=str_parsers.bool_parser,
            description="Дополнительные параметры заявки (004)",
        ),
        "is_public": Filter[bool](
            q_func=lambda x: {"is_public": x},
            t_parser=str_parsers.bool_parser,
            description="Видимость заявки",
        ),
        "tag": Filter[RequestTag](
            q_func=lambda x: {"tag": x},
            t_parser=str_parsers.get_enum_parser(RequestTag),
            description="Теги",
        ),
        "category": Filter[RequestCategory](
            q_func=lambda x: {"category": x},
            t_parser=str_parsers.get_enum_parser(RequestCategory),
            description="Категория",
        ),
        "subcategory": Filter[RequestSubcategory](
            q_func=lambda x: {"subcategory": x},
            t_parser=str_parsers.get_enum_parser(RequestSubcategory),
            exclusions=["category"],
            description="Подкатегория",
        ),
        "work_area": Filter[RequestWorkArea](
            q_func=lambda x: {"work_area": x},
            t_parser=str_parsers.get_enum_parser(RequestWorkArea),
            description="Область работ",
        ),
        "actions__type__in": Filter[ActionRSType](
            q_func=lambda x: {"action._type": {"$in": x}},
            many=True,
            t_parser=str_parsers.get_enum_parser(ActionRSType),
            description="Тип аварийного отключения(если выбор отключения без времени))",
        ),
        "actions__lift__date_from": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "lift"}, {"action.date_from": {"$gte": x}}]},
            t_parser=str_parsers.datetime_parser,
            description="Время отключения лифта (С)",
        ),
        "actions__lift__date_till": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "lift"}, {"action.date_till": {"$lt": x}}]},
            t_parser=str_parsers.datetime_parser,
            description="Время отключения лифта (По)",
        ),
        "actions__central_heating__date_from": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "central_heating"}, {"action.date_from": {"$gte": x}}]},
            t_parser=str_parsers.datetime_parser,
            description="Время отключения центрального отопления (С)",
        ),
        "actions__central_heating__date_till": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "central_heating"}, {"action.date_till": {"$lt": x}}]},
            t_parser=str_parsers.datetime_parser,
            description="Время отключения центрального отопления (По)",
        ),
        "actions__hot_water_supply__date_from": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "hot_water_supply"}, {"action.date_from": {"$gte": x}}]},
            t_parser=str_parsers.datetime_parser,
            description="Время отключения горячего водоснабжения (С)",
        ),
        "actions__hot_water_supply__date_till": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "hot_water_supply"}, {"action.date_till": {"$lt": x}}]},
            t_parser=str_parsers.datetime_parser,
            description="Время отключения горячего водоснабжения (По)",
        ),
        "actions__cold_water_supply__date_from": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "cold_water_supply"}, {"action.date_from": {"$gte": x}}]},
            t_parser=str_parsers.datetime_parser,
            description="Время отключения холодного водоснабжения (С)",
        ),
        "actions__cold_water_supply__date_till": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "cold_water_supply"}, {"action.date_till": {"$lt": x}}]},
            t_parser=str_parsers.datetime_parser,
            description="Время отключения холодного водоснабжения (По)",
        ),
        "actions__electricity__date_from": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "electricity"}, {"action.date_from": {"$gte": x}}]},
            t_parser=str_parsers.datetime_parser,
            description="Время отключения электроснабжения (С)",
        ),
        "actions__electricity__date_till": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "electricity"}, {"action.date_till": {"$lt": x}}]},
            t_parser=str_parsers.datetime_parser,
            description="Время отключения электроснабжения (По)",
        ),
        "dispatcher__department__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"dispatcher.department._id": {"$in": x}},
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            exclusions=["dispatcher__position__id__in", "dispatcher__id__in"],
            many=True,
            description="Создатель заявки (Отдел)",
        ),
        "dispatcher__position__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"dispatcher.position._id": {"$in": x}},
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            exclusions=["dispatcher__id__in"],
            many=True,
            description="Создатель заявки (Должность)",
        ),
        "dispatcher__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"dispatcher._id": {"$in": x}},
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            many=True,
            description="Создатель заявки (Сотрудник)",
        ),
        "execution__employees__department__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"execution.employees.department._id": {"$in": x}},
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            exclusions=["execution__employees__position__id__in", "execution__employees__id__in"],
            many=True,
            description="Исполнитель заявки (Отдел)",
        ),
        "execution__employees__position__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"execution.employees.position._id": {"$in": x}},
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            exclusions=["execution__employees__id__in"],
            many=True,
            description="Исполнитель заявки (Должность)",
        ),
        "execution__employees__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"execution.employees._id": {"$in": x}},
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            many=True,
            description="Исполнитель заявки (Сотрудник)",
        ),
        "execution__average_rating__lte": Filter[float](
            q_func=lambda x: {"execution.average_rating": {"$lte": x}},
            t_parser=str_parsers.get_type_parser(float),
            description="Рейтинг заявки (От)",
        ),
        "execution__average_rating__gte": Filter[float](
            q_func=lambda x: {"execution.average_rating": {"$gte": x}},
            t_parser=str_parsers.get_type_parser(float),
            description="Рейтинг заявки (До)",
        ),
        "relations__template_id": Filter[PydanticObjectId](
            q_func=lambda x: {"relations.template_id": x},
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            description="Рейтинг заявки (Шаблон заявки)",
        ),
        "monitoring__control_messages__0__exists": Filter[bool](
            q_func=lambda x: {"monitoring.control_messages.0": {"$exists": x}},
            t_parser=str_parsers.get_type_parser(bool),
            description="Статус контроля",
        ),
    }


class TenantRequestQPTranslator(QPTranslator):
    """
    Класс с фильтрами для заявок жителя
    """


class DispatcherRequestReportQPTranslator(DispatcherRequestQPTranslator):
    """
    Класс с фильтрами для заявок жителя
    """

    @staticmethod
    def q_func_created_at__gte_filter(x: datetime | list[datetime]):
        if not isinstance(x, datetime):
            x = datetime.now()
        x = x.replace(hour=0, minute=0, second=0, microsecond=0)
        return {
            "created_at": {
                "$gte": x,
                "$lte": x + timedelta(days=1),
            },
        }

    __filters__ = {
        "created_at__gte": Filter[datetime](
            q_func=q_func_created_at__gte_filter,
            t_parser=str_parsers.datetime_parser,
            is_required=True,
        ),
        "created_at__lte": Filter[datetime](
            q_func=lambda x: {"created_at": {"$lte": x}},
            t_parser=str_parsers.datetime_parser,
            description="Дата подачи заявки (По)",
            exclusions=["created_at__gte"],
        ),
    }
