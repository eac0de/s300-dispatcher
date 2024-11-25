"""
Модуль с роутером для работы с константами
"""

from fastapi import APIRouter, status

from models.request.categories_tree import CATEGORY_SUBCATEGORY_WORK_AREA_TREE
from models.request.constants import (
    REQUEST_STATUS_EN_RU,
    REQUEST_TAG_EN_RU,
    REQUEST_TYPE_EN_RU,
)
from models.request_template.constants import TEMPLATE_TYPE_EN_RU
from utils.responses import JSONResponse

constants_router = APIRouter(
    tags=["constants"],
)


@constants_router.get(
    path="/requests/",
    status_code=status.HTTP_200_OK,
)
async def get_requests_constants():
    """
    Получение типов заявки
    """
    results = {
        # "RequestTemplateType": [{"value": k, "text": v} for k, v in TEMPLATE_TYPE_EN_RU.items()],
        # "RequestStatus": [{"value": k, "text": v} for k, v in REQUEST_STATUS_EN_RU.items()],
        # "RequestType": [{"value": k, "text": v} for k, v in REQUEST_TYPE_EN_RU.items()],
        # "RequestSupervisions": [{"value": "housing_supervision", "text": "004"}, {"value": "administrative_supervision", "text": "Администрация района"}],
        # "RequestTag": [{"value": k, "text": v} for k, v in REQUEST_TAG_EN_RU.items()],
        "RequestSamplesType": [{"value": k, "text": v} for k, v in TEMPLATE_TYPE_EN_RU.items()],
        "RequestStatus": [{"value": k, "text": v} for k, v in REQUEST_STATUS_EN_RU.items()],
        "RequestType": [{"value": k, "text": v} for k, v in REQUEST_TYPE_EN_RU.items()],
        "RequestSupervision": [{"value": "housing_supervision", "text": "004"}, {"value": "administrative_supervision", "text": "Администрация района"}],
        "IntercomStatusChoices": [{"value": k, "text": v} for k, v in REQUEST_TAG_EN_RU.items()],
        "AccrualsSectorType": [
            {"value": "rent", "text": "Квартплата"},
            {"value": "social_rent", "text": "Социальный найм"},
            {"value": "capital_repair", "text": "Капитальный ремонт"},
            {"value": "heat_supply", "text": "Теплоснабжение"},
            {"value": "water_supply", "text": "Водоснабжение"},
            {"value": "waste_water", "text": "Водоотведение"},
            {"value": "catv", "text": "Кабельное ТВ"},
            {"value": "garbage", "text": "Вывоз мусора"},
            {"value": "reg_fee", "text": "Целевой взнос"},
            {"value": "lease", "text": "Аренда"},
            {"value": "commercial", "text": "Платные услуги"},
            {"value": "gas_supply", "text": "Газоснабжение"},
            {"value": "communal", "text": "Коммунальные услуги"},
            {"value": "cold_water_public", "text": "Холодное водоснабжение ОДН"},
        ],
        "AreaLocations": [
            {"value": "wc", "text": "санузел"},
            {"value": "hall", "text": "прихожая"},
            {"value": "garage", "text": "гараж"},
            {"value": "toilet", "text": "туалет"},
            {"value": "storey", "text": "этажная площадка"},
            {"value": "living", "text": "жилая комната"},
            {"value": "kitchen", "text": "кухня"},
            {"value": "corridor", "text": "коридор"},
            {"value": "bathroom", "text": "ванная"},
            {"value": "pantry", "text": "кладовка"},
        ],
        # "RequestSamplesType": [
        #     {"value": "body", "text": "Шаблон заявки"},
        #     {"value": "delayed", "text": "Шаблон описания для статуса «Отложена»"},
        #     {"value": "performed", "text": "Шаблон описания для статуса «Выполнена»"},
        #     {"value": "abandonment", "text": "Шаблон описания для статуса «Отказ в исполнении»"},
        #     {"value": "refusal", "text": "Шаблон описания для статуса «Отказ от заявки»"},
        # ],
        "CatalogueGroup": [
            {"value": 0, "text": "прочие"},
            {"value": 1, "text": "электро-технические"},
            {"value": 2, "text": "санитарно-технические"},
            {"value": 3, "text": "ремонтно-строительные"},
            {"value": 4, "text": "шаблонные заявки"},
            {"value": 5, "text": "распределители тепловой энергии"},
        ],
        # "RequestStatus": [
        #     {"value": "accepted", "text": "Принята"},
        #     {"value": "run", "text": "На исполнении"},
        #     {"value": "delayed", "text": "Отложена"},
        #     {"value": "performed", "text": "Выполнена"},
        #     {"value": "abandonment", "text": "Отказ в исполнении"},
        #     {"value": "refusal", "text": "Отказ от заявки"},
        # ],
        "PhoneType": [
            {"value": "cell", "text": "мобильный"},
            {"value": "work", "text": "рабочий"},
            {"value": "dispatcher", "text": "диспетчерский"},
            {"value": "home", "text": "домашний"},
            {"value": "fax", "text": "факс"},
            {"value": "emergency", "text": "аварийный"},
        ],
        # "RequestType": [{"value": "HouseRequest", "text": "Общедомовая заявка"}, {"value": "AreaRequest", "text": "Квартирная заявка"}],
        # "RequestSupervision": [{"value": "housing_supervision", "text": "004"}, {"value": "administrative_supervision", "text": "Администрация района"}],
        # "RequestPayableType": [{"value": "none", "text": "не требует оплаты"}, {"value": "pre", "text": "предоплата"}, {"value": "post", "text": "по факту выполнения"}],
        # "IntercomStatusChoices": [
        #     {"value": "urgent", "text": "Срочная"},
        #     {"value": "current", "text": "Текущая"},
        #     {"value": "planned", "text": "Плановая"},
        #     {"value": "acceptance", "text": "Приемка"},
        #     {"value": "prophylaxis", "text": "Профилактика"},
        # ],
        "MeterTypeNamesShort": [
            {"value": "ColdWaterAreaMeter", "text": "ХВС"},
            {"value": "HotWaterAreaMeter", "text": "ГВС"},
            {"value": "ElectricOneRateAreaMeter", "text": "ЭЛ"},
            {"value": "ElectricTwoRateAreaMeter", "text": "ЭЛДТ"},
            {"value": "ElectricThreeRateAreaMeter", "text": "ЭЛТТ"},
            {"value": "HeatAreaMeter", "text": "ТПЛ"},
            {"value": "HeatDistributorAreaMeter", "text": "РТЭ"},
            {"value": "GasAreaMeter", "text": "ГАЗ"},
            {"value": "ColdWaterHouseMeter", "text": "ХВС"},
            {"value": "HotWaterHouseMeter", "text": "ГВС"},
            {"value": "ElectricOneRateHouseMeter", "text": "ЭЛ"},
            {"value": "ElectricTwoRateHouseMeter", "text": "ЭЛДТ"},
            {"value": "ElectricThreeRateHouseMeter", "text": "ЭЛТТ"},
            {"value": "HeatHouseMeter", "text": "ТПЛ"},
            {"value": "GasHouseMeter", "text": "ГАЗ"},
        ],
        "MeterTypeUnitNames": [
            {"value": "ColdWaterAreaMeter", "text": "м3"},
            {"value": "HotWaterAreaMeter", "text": "м3"},
            {"value": "ElectricOneRateAreaMeter", "text": "КВт/ч"},
            {"value": "ElectricTwoRateAreaMeter", "text": "КВт/ч"},
            {"value": "ElectricThreeRateAreaMeter", "text": "КВт/ч"},
            {"value": "HeatAreaMeter", "text": "ГКкал"},
            {"value": "HeatDistributorAreaMeter", "text": "ГКкал"},
            {"value": "GasAreaMeter", "text": "м3"},
            {"value": "ColdWaterHouseMeter", "text": "м3"},
            {"value": "HotWaterHouseMeter", "text": "м3"},
            {"value": "ElectricOneRateHouseMeter", "text": "КВт/ч"},
            {"value": "ElectricTwoRateHouseMeter", "text": "КВт/ч"},
            {"value": "ElectricThreeRateHouseMeter", "text": "КВт/ч"},
            {"value": "HeatHouseMeter", "text": "ГКкал"},
            {"value": "GasHouseMeter", "text": "м3"},
        ],
        "MeterTypeNames": [
            {"value": "ColdWaterAreaMeter", "text": "Холодной воды"},
            {"value": "HotWaterAreaMeter", "text": "Горячей воды"},
            {"value": "ElectricOneRateAreaMeter", "text": "Электрический однотарифный"},
            {"value": "ElectricTwoRateAreaMeter", "text": "Электрический двухтарифный"},
            {"value": "ElectricThreeRateAreaMeter", "text": "Электрический трёхтарифный"},
            {"value": "HeatAreaMeter", "text": "Тепла"},
            {"value": "HeatDistributorAreaMeter", "text": "Распределителя тепла"},
            {"value": "GasAreaMeter", "text": "Газа"},
            {"value": "ColdWaterHouseMeter", "text": "Холодной воды"},
            {"value": "HotWaterHouseMeter", "text": "Горячей воды"},
            {"value": "ElectricOneRateHouseMeter", "text": "Электрический однотарифный"},
            {"value": "ElectricTwoRateHouseMeter", "text": "Электрический двухтарифный"},
            {"value": "ElectricThreeRateHouseMeter", "text": "Электрический трёхтарифный"},
            {"value": "HeatHouseMeter", "text": "Тепла"},
            {"value": "GasHouseMeter", "text": "Газа"},
        ],
        "RequestRelationship": [{"value": "sync", "text": "Дублирующие"}, {"value": "regular", "text": "Cвязанные"}],
        "WaterType": [{"value": "hot", "text": "ГВС"}, {"value": "cold", "text": "ХВС"}, {"value": "central", "text": "ЦО"}, {"value": "gaz", "text": "Газ"}],
        "NotificationConstants": [{"value": "email", "text": "E-mail"}, {"value": "telegram", "text": "Telegram-бот"}, {"value": "app", "text": "В кабинет-жителя.рф"}],
        "SocialTypeConstants": [{"value": "viber", "text": "Viber"}, {"value": "telegram", "text": "Telegram"}, {"value": "whatsapp", "text": "WhatsApp"}],
    }

    return JSONResponse(content={"results": results})


@constants_router.get(
    path="/requests/categories_tree/",
    status_code=status.HTTP_200_OK,
)
async def get_requests_categories_tree():
    """
    Получение дерева категорий, подкатегорий, областей работ и действий
    """
    return JSONResponse(content=CATEGORY_SUBCATEGORY_WORK_AREA_TREE)
