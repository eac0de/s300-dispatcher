from beanie import PydanticObjectId
from qp_translator import Filter, QPTranslator, str_parsers


class OtherPersonQPTranslator(QPTranslator):
    """
    Класс с фильтрами для каталога жителя
    """


class OtherEmployeeQPTranslator(QPTranslator):
    """
    Класс с фильтрами для каталога жителя
    """

    __filters__ = {
        "provider_id": Filter[PydanticObjectId](
            q_func=lambda x: {"provider_id": x},
            t_parser=str_parsers.get_type_parser(PydanticObjectId),
            description="Организация",
        ),
    }


class OtherProviderQPTranslator(QPTranslator):
    """
    Класс с фильтрами для каталога жителя
    """
