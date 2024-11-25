"""
Модуль с константами шаблона заявки
"""

from enum import Enum


class RequestTemplateType(str, Enum):
    """
    Типы шаблона заявки
    """

    REQUEST = "request"
    PERFORMED = "performed"
    DELAYED = "delayed"
    ABANDONMENT = "abandonment"
    REFUSAL = "refusal"


TEMPLATE_TYPE_EN_RU = {
    RequestTemplateType.REQUEST: "Шаблон заявки",
    RequestTemplateType.PERFORMED: "Шаблон описания для статуса «Выполнена»",
    RequestTemplateType.DELAYED: "Шаблон описания для статуса «Отложена»",
    RequestTemplateType.ABANDONMENT: "Шаблон описания для статуса «Отказ в исполнении»",
    RequestTemplateType.REFUSAL: "Шаблон описания для статуса «Отказ от заявки»",
}
