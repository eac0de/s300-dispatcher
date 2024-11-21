"""
Модуль с дополнительным классом для заявки - действия
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class ActionRSType(str, Enum):
    """
    Типы действий
    """

    LIFT = "lift"
    CENTRAL_HEATING = "central_heating"
    HWS = "hot_water_supply"
    CWS = "cold_water_supply"
    ELECTRICITY = "electricity"


ACTION_TYPE_EN_RU = {
    ActionRSType.LIFT: "Лифт",
    ActionRSType.CENTRAL_HEATING: "Центральное отопление",
    ActionRSType.HWS: "Горячее водоснабжение",
    ActionRSType.CWS: "Холодное водоснабжение",
    ActionRSType.ELECTRICITY: "Электричество",
}

ACTION_TYPE_EN_RU_DISPLAY = {
    ActionRSType.LIFT: "лифта",
    ActionRSType.CENTRAL_HEATING: "центрального отопления",
    ActionRSType.HWS: "горячего водоснабжения",
    ActionRSType.CWS: "холодного водоснабжения",
    ActionRSType.ELECTRICITY: "электричества",
}


class ActionRS(BaseModel):
    """
    Класс действия
    """

    start_at: datetime | None = Field(
        default=None,
        title="С какого времени",
    )
    end_at: datetime | None = Field(
        default=None,
        title="До какого времени",
    )
    type: Literal[ActionRSType.ELECTRICITY,] = Field(
        alias="_type",
        title="Тип действия",
    )


class LiftActionRS(BaseModel):
    """
    Класс лифта для действия отключения лифта
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор лифта",
    )


class LiftShutdownActionRS(ActionRS):
    """
    Класс действия отключения лифта
    """

    type: Literal[ActionRSType.LIFT] = Field(
        alias="_type",
        title="Тип действия",
    )
    lift: LiftActionRS = Field(
        title="Лифт",
    )


class StandpipeActionRS(BaseModel):
    """
    Класс стояка для действия отключения стояка ГВС, ХВС или ЦО
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор стояка",
    )


class StandpipeShutdownActionRS(ActionRS):
    """
    Класс действия отключения стояка ГВС, ХВС или ЦО
    """

    type: Literal[
        ActionRSType.CENTRAL_HEATING,
        ActionRSType.CWS,
        ActionRSType.HWS,
    ] = Field(
        alias="_type",
        title="Тип действия",
    )
    standpipe: StandpipeActionRS = Field(
        title="Стояк",
    )
