"""
Модуль с фильтрами для query параметров запросов к заявкам
"""

from datetime import datetime

from beanie import PydanticObjectId

from utils.document_filter import DocumentFilter, Filter, StandartParser


class RequestParser:
    """
    Класс с парсерами для заявок
    """

    @staticmethod
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


class DispatcherRequestFilter(DocumentFilter):
    """
    Класс с фильтрами для заявок диспетчера
    """

    __filters__ = {
        "status__in": Filter[str](
            q_func=lambda x: {"status": {"$in": x}},
            many=True,
        ),
        "type": Filter[str](
            q_func=lambda x: {"_type": x},
        ),
        "source": Filter[str](
            q_func=lambda x: {"source": x},
        ),
        "house__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"house._id": {"$in": x}},
            many=True,
            t_parser=StandartParser.get_type_parser(PydanticObjectId),
        ),
        "area_range": Filter[str](
            q_func=lambda x: {"area.number": {"$in": x}},
            t_parser=RequestParser.area_range_parser,
        ),
        "created_at__gte": Filter[datetime](
            q_func=lambda x: {"created_at": {"$gte": x}},
            t_parser=StandartParser.datetime_parser,
        ),
        "created_at__lte": Filter[datetime](
            q_func=lambda x: {"created_at": {"$lte": x}},
            t_parser=StandartParser.datetime_parser,
        ),
        "execution__end_at__gte": Filter[datetime](
            q_func=lambda x: {"execution.end_at": {"$gte": x}},
            t_parser=StandartParser.datetime_parser,
        ),
        "execution__desired_start_at__gte": Filter[datetime](
            q_func=lambda x: {"execution.desired_start_at": {"$gte": x}},
            t_parser=StandartParser.datetime_parser,
        ),
        "execution__desired_end_at__lte": Filter[datetime](
            q_func=lambda x: {"execution.desired_end_at": {"$lte": x}},
            t_parser=StandartParser.datetime_parser,
        ),
        "tenant__number": Filter[str](
            q_func=lambda x: {"requester.number": x},
        ),
        "administrative_supervision": Filter[bool](
            q_func=lambda x: {"administrative_supervision": x},
            t_parser=StandartParser.bool_parser,
        ),
        "housing_supervision": Filter[bool](
            q_func=lambda x: {"housing_supervision": x},
            t_parser=StandartParser.bool_parser,
        ),
        "is_public": Filter[bool](
            q_func=lambda x: {"is_public": x},
            t_parser=StandartParser.bool_parser,
        ),
        "tag": Filter[str](
            q_func=lambda x: {"tag": x},
        ),
        "category": Filter[str](
            q_func=lambda x: {"category": x},
        ),
        "subcategory": Filter[str](
            q_func=lambda x: {"subcategory": x},
            exclusions=["category"],
        ),
        "work_area": Filter[str](
            q_func=lambda x: {"work_area": x},
        ),
        "actions__type__in": Filter[str](
            q_func=lambda x: {"action._type": {"$in": x}},
        ),
        "actions__lift__date_from": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "lift"}, {"action.date_from": {"$gte": x}}]},
            t_parser=StandartParser.datetime_parser,
        ),
        "actions__lift__date_till": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "lift"}, {"action.date_till": {"$lte": x}}]},
            t_parser=StandartParser.datetime_parser,
        ),
        "actions__central_heating__date_from": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "central_heating"}, {"action.date_from": {"$gte": x}}]},
            t_parser=StandartParser.datetime_parser,
        ),
        "actions__central_heating__date_till": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "central_heating"}, {"action.date_till": {"$lte": x}}]},
            t_parser=StandartParser.datetime_parser,
        ),
        "actions__hot_water_supply__date_from": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "hot_water_supply"}, {"action.date_from": {"$gte": x}}]},
            t_parser=StandartParser.datetime_parser,
        ),
        "actions__hot_water_supply__date_till": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "hot_water_supply"}, {"action.date_till": {"$lte": x}}]},
            t_parser=StandartParser.datetime_parser,
        ),
        "actions__cold_water_supply__date_from": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "cold_water_supply"}, {"action.date_from": {"$gte": x}}]},
            t_parser=StandartParser.datetime_parser,
        ),
        "actions__cold_water_supply__date_till": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "cold_water_supply"}, {"action.date_till": {"$lte": x}}]},
            t_parser=StandartParser.datetime_parser,
        ),
        "actions__electricity__date_from": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "electricity"}, {"action.date_from": {"$gte": x}}]},
            t_parser=StandartParser.datetime_parser,
        ),
        "actions__electricity__date_till": Filter[datetime](
            q_func=lambda x: {"$and": [{"action._type": "electricity"}, {"action.date_till": {"$lte": x}}]},
            t_parser=StandartParser.datetime_parser,
        ),
        "dispatcher__department__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"dispatcher.department._id": {"$in": x}},
            t_parser=StandartParser.get_type_parser(PydanticObjectId),
            exclusions=["dispatcher__position__id__in", "dispatcher__id__in"],
            many=True,
        ),
        "dispatcher__position__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"dispatcher.position._id": {"$in": x}},
            t_parser=StandartParser.get_type_parser(PydanticObjectId),
            exclusions=["dispatcher__id__in"],
            many=True,
        ),
        "dispatcher__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"dispatcher._id": {"$in": x}},
            t_parser=StandartParser.get_type_parser(PydanticObjectId),
            many=True,
        ),
        "execution__employees__department__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"execution.employees.department._id": {"$in": x}},
            t_parser=StandartParser.get_type_parser(PydanticObjectId),
            exclusions=["execution__employees__position__id__in", "execution__employees__id__in"],
            many=True,
        ),
        "execution__employees__position__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"execution.employees.position._id": {"$in": x}},
            t_parser=StandartParser.get_type_parser(PydanticObjectId),
            exclusions=["execution__employees__id__in"],
            many=True,
        ),
        "execution__employees__id__in": Filter[PydanticObjectId](
            q_func=lambda x: {"execution.employees._id": {"$in": x}},
            t_parser=StandartParser.get_type_parser(PydanticObjectId),
            many=True,
        ),
        "execution__total_rate__lte": Filter[float](
            q_func=lambda x: {"execution.total_rate": {"$lte": x}},
            t_parser=StandartParser.get_type_parser(float),
        ),
        "execution__total_rate__gte": Filter[float](
            q_func=lambda x: {"execution.total_rate": {"$gte": x}},
            t_parser=StandartParser.get_type_parser(float),
        ),
        "relations__template_id": Filter[PydanticObjectId](
            q_func=lambda x: {"relations.template_id": x},
            t_parser=StandartParser.get_type_parser(PydanticObjectId),
        ),
        "monitoring__control_messages__0__exists": Filter[bool](
            q_func=lambda x: {"monitoring.control_messages.0": {"$exists": x}},
            t_parser=StandartParser.get_type_parser(bool),
        ),
    }


class TenantRequestFilter(DocumentFilter):
    """
    Класс с фильтрами для заявок жителя
    """
