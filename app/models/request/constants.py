"""
Модуль с константами для заявки
"""

from enum import Enum


class RequestType(str, Enum):
    """
    Типы заявки
    """

    HOUSE = "house"
    AREA = "area"


REQUEST_TYPE_EN_RU = {
    RequestType.HOUSE: "Общедомовая заявка",
    RequestType.AREA: "Квартирная заявка",
}


class RequestStatus(str, Enum):
    """
    Статусы заявки
    """

    PERFORMED = "performed"
    ACCEPTED = "accepted"
    RUN = "run"
    DELAYED = "delayed"
    ABANDONMENT = "abandonment"
    REFUSAL = "refusal"
    HIDDEN = "hidden"


REQUEST_STATUS_EN_RU = {
    RequestStatus.PERFORMED: "Выполнена",
    RequestStatus.ACCEPTED: "Принята к исполнению",
    RequestStatus.RUN: "На исполнении",
    RequestStatus.DELAYED: "Отложена",
    RequestStatus.ABANDONMENT: "Отказ от исполнения",
    RequestStatus.REFUSAL: "Отказ от заявки",
    RequestStatus.HIDDEN: "Скрыта",
}


class RequestPayStatus(str, Enum):
    """
    Статусы оплаты заявки
    """

    NO_CHARGE = "no_charge"
    WAIT = "wait"
    PROCESSING = "processing"
    PAID = "paid"


REQUEST_PAY_STATUS_EN_RU = (
    (RequestPayStatus.NO_CHARGE, "Не требует оплаты"),
    (RequestPayStatus.WAIT, "Ожидание оплаты"),
    (RequestPayStatus.PROCESSING, "Обработка отплаты"),
    (RequestPayStatus.PAID, "Оплачена"),
)


class RequestTag(str, Enum):
    """
    Теги заявки
    """

    URGENT = "urgent"
    CURRENT = "current"
    PLANNED = "planned"
    ACCEPTANCE = "acceptance"
    PROPHYLAXIS = "prophylaxis"


REQUEST_TAG_EN_RU = {
    RequestTag.URGENT: "Срочная",
    RequestTag.CURRENT: "Текущая",
    RequestTag.PLANNED: "Плановая",
    RequestTag.ACCEPTANCE: "Приемка",
    RequestTag.PROPHYLAXIS: "Профилактика",
}


class RequestSource(str, Enum):
    """
    Источники создания заявки
    """

    APPEAL = "appeal"
    TENANT = "tenant"
    DISPATCHER = "dispatcher"
    CATALOG = "catalog"


REQUEST_SOURCE_EN_RU = {
    RequestSource.APPEAL: "Из обращения",
    RequestSource.TENANT: "Житель",
    RequestSource.DISPATCHER: "Диспетчер",
    RequestSource.CATALOG: "Из каталога",
}
