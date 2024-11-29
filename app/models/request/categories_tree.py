"""
Модуль с деревом категорий, подкатегорий, областей рабои и действий заявки
"""

from enum import Enum

from models.request.embs.action import ACTION_TYPE_EN_RU, ActionRSType


class RequestCategory(str, Enum):
    """
    Категории заявки
    """

    BUILDING_RENOVATION = "building_renovation"
    TERRITORY = "territory"
    COMMERCIAL = "commercial"
    EMERGENCY = "emergency"
    VANDALISM = "vandalism"
    VENTILATION = "ventilation"
    WATER_DISPOSAL = "water_disposal"
    ROOF = "roof"
    SEALING = "sealing"
    LEGAL_ISSUES = "legal_issues"
    FACADES = "facades"


REQUEST_CATEGORY_EN_RU = {
    RequestCategory.BUILDING_RENOVATION: "Ремонт строения/дома",
    RequestCategory.TERRITORY: "Территория",
    RequestCategory.COMMERCIAL: "Коммерческая",
    RequestCategory.EMERGENCY: "Аварийная",
    RequestCategory.VANDALISM: "Вандализм",
    RequestCategory.VENTILATION: "Вентиляция",
    RequestCategory.WATER_DISPOSAL: "Водоотведение",
    RequestCategory.ROOF: "Кровля",
    RequestCategory.SEALING: "Опломбирование",
    RequestCategory.LEGAL_ISSUES: "Орг.-правовые вопросы ЖКХ",
    RequestCategory.FACADES: "Фасады",
}


class RequestSubcategory(str, Enum):
    """
    Подкатегории заявки
    """

    GENERAL_PROPERTY = "general_property"
    CURRENT_REPAIR = "current_repair"
    SANITATION = "sanitation"
    IMPROVEMENT = "improvement"
    CHARGEABLE = "chargeable"
    WARRANTY = "warranty"
    LIFT = "lift"
    ELECTRICITY = "electricity"
    LEAK = "leak"
    OTHER = "other"
    WINDOWS = "windows"
    SANITARY_WARE = "sanitary_ware"
    ELECTRICS = "electrics"
    STAINED_GLASS = "stained_glass"
    DECORATION = "decoration"


REQUEST_SUBCATEGORY_EN_RU = {
    RequestSubcategory.GENERAL_PROPERTY: "Общее имущество",
    RequestSubcategory.CURRENT_REPAIR: "Текущий ремонт",
    RequestSubcategory.SANITATION: "Сан.содержание",
    RequestSubcategory.IMPROVEMENT: "Благоустройство",
    RequestSubcategory.CHARGEABLE: "Платная",
    RequestSubcategory.WARRANTY: "Гарантийная",
    RequestSubcategory.LIFT: "Лифт",
    RequestSubcategory.ELECTRICITY: "Электроснабжение",
    RequestSubcategory.LEAK: "Протечка",
    RequestSubcategory.OTHER: "Прочие работы",
    RequestSubcategory.WINDOWS: "Окна",
    RequestSubcategory.SANITARY_WARE: "Сантехника",
    RequestSubcategory.ELECTRICS: "Электрика",
    RequestSubcategory.STAINED_GLASS: "Витражи ГО",
    RequestSubcategory.DECORATION: "Отделка",
}


class RequestWorkArea(str, Enum):
    """
    Область работы заявки
    """

    AREA = "area"
    CELLAR = "cellar"
    STANDPIPE = "standpipe"
    HOUSE = "house"
    PORCH = "porch"


REQUEST_WORK_AREA_EN_RU = {
    RequestWorkArea.AREA: "В квартире",
    RequestWorkArea.CELLAR: "В подвале",
    RequestWorkArea.STANDPIPE: "Стояк",
    RequestWorkArea.HOUSE: "В доме",
    RequestWorkArea.PORCH: "В подъезде",
}

CATEGORY_SUBCATEGORY_WORK_AREA_TREE = {
    "categories": {
        RequestCategory.BUILDING_RENOVATION: {
            "name": REQUEST_CATEGORY_EN_RU[RequestCategory.BUILDING_RENOVATION],
            "subcategories": {
                RequestSubcategory.GENERAL_PROPERTY: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.GENERAL_PROPERTY],
                    "parent": RequestCategory.BUILDING_RENOVATION,
                },
                RequestSubcategory.CURRENT_REPAIR: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.CURRENT_REPAIR],
                    "parent": RequestCategory.BUILDING_RENOVATION,
                },
            },
        },
        RequestCategory.TERRITORY: {
            "name": REQUEST_CATEGORY_EN_RU[RequestCategory.TERRITORY],
            "subcategories": {
                RequestSubcategory.SANITATION: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.SANITATION],
                    "parent": RequestCategory.TERRITORY,
                },
                RequestSubcategory.IMPROVEMENT: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.IMPROVEMENT],
                    "parent": RequestCategory.TERRITORY,
                },
            },
        },
        RequestCategory.COMMERCIAL: {
            "name": REQUEST_CATEGORY_EN_RU[RequestCategory.COMMERCIAL],
            "subcategories": {
                RequestSubcategory.CHARGEABLE: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.CHARGEABLE],
                    "parent": RequestCategory.COMMERCIAL,
                    "work_areas": {
                        RequestWorkArea.AREA: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.AREA],
                            "actions": {
                                ActionRSType.CWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.CWS]},
                                ActionRSType.HWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.HWS]},
                                ActionRSType.CENTRAL_HEATING: {"name": ACTION_TYPE_EN_RU[ActionRSType.CENTRAL_HEATING]},
                            },
                        },
                        RequestWorkArea.CELLAR: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.CELLAR],
                            "actions": {
                                ActionRSType.CWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.CWS]},
                                ActionRSType.HWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.HWS]},
                                ActionRSType.CENTRAL_HEATING: {"name": ACTION_TYPE_EN_RU[ActionRSType.CENTRAL_HEATING]},
                            },
                        },
                        RequestWorkArea.STANDPIPE: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.STANDPIPE],
                            "actions": {
                                ActionRSType.CWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.CWS]},
                                ActionRSType.HWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.HWS]},
                                ActionRSType.CENTRAL_HEATING: {"name": ACTION_TYPE_EN_RU[ActionRSType.CENTRAL_HEATING]},
                            },
                        },
                    },
                },
                RequestSubcategory.WARRANTY: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.WARRANTY],
                    "parent": RequestCategory.COMMERCIAL,
                    "work_areas": {
                        RequestWorkArea.AREA: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.AREA],
                            "actions": {
                                ActionRSType.CWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.CWS]},
                                ActionRSType.HWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.HWS]},
                                ActionRSType.CENTRAL_HEATING: {"name": ACTION_TYPE_EN_RU[ActionRSType.CENTRAL_HEATING]},
                            },
                        },
                        RequestWorkArea.CELLAR: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.CELLAR],
                            "actions": {
                                ActionRSType.CWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.CWS]},
                                ActionRSType.HWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.HWS]},
                                ActionRSType.CENTRAL_HEATING: {"name": ACTION_TYPE_EN_RU[ActionRSType.CENTRAL_HEATING]},
                            },
                        },
                        RequestWorkArea.STANDPIPE: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.STANDPIPE],
                            "actions": {
                                ActionRSType.CWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.CWS]},
                                ActionRSType.HWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.HWS]},
                                ActionRSType.CENTRAL_HEATING: {"name": ACTION_TYPE_EN_RU[ActionRSType.CENTRAL_HEATING]},
                            },
                        },
                    },
                },
            },
        },
        RequestCategory.EMERGENCY: {
            "name": REQUEST_CATEGORY_EN_RU[RequestCategory.EMERGENCY],
            "subcategories": {
                RequestSubcategory.LIFT: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.LIFT],
                    "parent": RequestCategory.EMERGENCY,
                    "work_areas": {
                        RequestWorkArea.HOUSE: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.HOUSE],
                            "actions": {
                                ActionRSType.LIFT: {"name": ACTION_TYPE_EN_RU[ActionRSType.LIFT]},
                            },
                        },
                        RequestWorkArea.PORCH: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.PORCH],
                            "actions": {
                                ActionRSType.LIFT: {"name": ACTION_TYPE_EN_RU[ActionRSType.LIFT]},
                            },
                        },
                    },
                },
                RequestSubcategory.ELECTRICITY: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.ELECTRICITY],
                    "parent": RequestCategory.EMERGENCY,
                    "work_areas": {
                        RequestWorkArea.HOUSE: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.HOUSE],
                            "actions": {
                                ActionRSType.ELECTRICITY: {"name": ACTION_TYPE_EN_RU[ActionRSType.ELECTRICITY]},
                            },
                        },
                        RequestWorkArea.AREA: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.AREA],
                            "actions": {
                                ActionRSType.ELECTRICITY: {"name": ACTION_TYPE_EN_RU[ActionRSType.ELECTRICITY]},
                            },
                        },
                    },
                },
                RequestSubcategory.LEAK: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.LEAK],
                    "parent": RequestCategory.EMERGENCY,
                    "work_areas": {
                        RequestWorkArea.AREA: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.AREA],
                            "actions": {
                                ActionRSType.CWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.CWS]},
                                ActionRSType.HWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.HWS]},
                                ActionRSType.CENTRAL_HEATING: {"name": ACTION_TYPE_EN_RU[ActionRSType.CENTRAL_HEATING]},
                            },
                        },
                        RequestWorkArea.CELLAR: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.CELLAR],
                            "actions": {
                                ActionRSType.CWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.CWS]},
                                ActionRSType.HWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.HWS]},
                                ActionRSType.CENTRAL_HEATING: {"name": ACTION_TYPE_EN_RU[ActionRSType.CENTRAL_HEATING]},
                            },
                        },
                        RequestWorkArea.STANDPIPE: {
                            "name": REQUEST_WORK_AREA_EN_RU[RequestWorkArea.STANDPIPE],
                            "actions": {
                                ActionRSType.CWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.CWS]},
                                ActionRSType.HWS: {"name": ACTION_TYPE_EN_RU[ActionRSType.HWS]},
                                ActionRSType.CENTRAL_HEATING: {"name": ACTION_TYPE_EN_RU[ActionRSType.CENTRAL_HEATING]},
                            },
                        },
                    },
                },
                RequestSubcategory.OTHER: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.OTHER],
                    "parent": RequestCategory.EMERGENCY,
                },
            },
        },
        RequestCategory.VANDALISM: {
            "name": REQUEST_CATEGORY_EN_RU[RequestCategory.VANDALISM],
            "subcategories": {
                RequestSubcategory.WINDOWS: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.WINDOWS],
                    "parent": RequestCategory.VANDALISM,
                },
                RequestSubcategory.SANITARY_WARE: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.SANITARY_WARE],
                    "parent": RequestCategory.VANDALISM,
                },
                RequestSubcategory.ELECTRICS: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.ELECTRICS],
                    "parent": RequestCategory.VANDALISM,
                },
                RequestSubcategory.STAINED_GLASS: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.STAINED_GLASS],
                    "parent": RequestCategory.VANDALISM,
                },
                RequestSubcategory.DECORATION: {
                    "name": REQUEST_SUBCATEGORY_EN_RU[RequestSubcategory.DECORATION],
                    "parent": RequestCategory.VANDALISM,
                },
            },
        },
        RequestCategory.VENTILATION: {
            "name": REQUEST_CATEGORY_EN_RU[RequestCategory.VENTILATION],
        },
        RequestCategory.WATER_DISPOSAL: {
            "name": REQUEST_CATEGORY_EN_RU[RequestCategory.WATER_DISPOSAL],
        },
        RequestCategory.ROOF: {
            "name": REQUEST_CATEGORY_EN_RU[RequestCategory.ROOF],
        },
        RequestCategory.SEALING: {
            "name": REQUEST_CATEGORY_EN_RU[RequestCategory.SEALING],
        },
        RequestCategory.LEGAL_ISSUES: {
            "name": REQUEST_CATEGORY_EN_RU[RequestCategory.LEGAL_ISSUES],
        },
        RequestCategory.FACADES: {
            "name": REQUEST_CATEGORY_EN_RU[RequestCategory.FACADES],
        },
    },
}
