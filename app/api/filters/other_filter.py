from beanie import PydanticObjectId

from utils.document_filter import DocumentFilter, Filter, StandartParser


class OtherPersonFilter(DocumentFilter):
    """
    Класс с фильтрами для каталога жителя
    """


class OtherEmployeeFilter(DocumentFilter):
    """
    Класс с фильтрами для каталога жителя
    """

    __filters__ = {
        "provider_id": Filter[PydanticObjectId](
            q_func=lambda x: {"provider_id": x},
            t_parser=StandartParser.get_type_parser(PydanticObjectId),
            description="Организация",
        ),
    }


class OtherProviderFilter(DocumentFilter):
    """
    Класс с фильтрами для каталога жителя
    """
