"""
Модуль с деревом категорий, подкатегорий, областей рабои и действий заявки
"""

from enum import Enum

from models.request.embs.action import ActionRSType


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
            "name": "Ремонт строения/дома",
            "subcategories": {
                RequestSubcategory.GENERAL_PROPERTY: {
                    "name": "Общее имущество",
                    "parent": RequestCategory.BUILDING_RENOVATION,
                },
                RequestSubcategory.CURRENT_REPAIR: {
                    "name": "Текущий ремонт",
                    "parent": RequestCategory.BUILDING_RENOVATION,
                },
            },
        },
        RequestCategory.TERRITORY: {
            "name": "Территория",
            "subcategories": {
                RequestSubcategory.SANITATION: {
                    "name": "Сан.содержание",
                    "parent": RequestCategory.TERRITORY,
                },
                RequestSubcategory.IMPROVEMENT: {
                    "name": "Благоустройство",
                    "parent": RequestCategory.TERRITORY,
                },
            },
        },
        RequestCategory.COMMERCIAL: {
            "name": "Коммерческая",
            "subcategories": {
                RequestSubcategory.CHARGEABLE: {
                    "name": "Платная",
                    "parent": RequestCategory.COMMERCIAL,
                    "work_areas": {
                        RequestWorkArea.AREA: {
                            "name": "В квартире",
                            "actions": {
                                ActionRSType.CWS: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.CELLAR: {
                            "name": "В подвале",
                            "actions": {
                                ActionRSType.CWS: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.STANDPIPE: {
                            "name": "Стояк",
                            "actions": {
                                ActionRSType.CWS: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                    },
                },
                RequestSubcategory.WARRANTY: {
                    "name": "Гарантийная",
                    "parent": RequestCategory.COMMERCIAL,
                    "work_areas": {
                        RequestWorkArea.AREA: {
                            "name": "В квартире",
                            "actions": {
                                ActionRSType.CWS: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.CELLAR: {
                            "name": "В подвале",
                            "actions": {
                                ActionRSType.CWS: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.STANDPIPE: {
                            "name": "Стояк",
                            "actions": {
                                ActionRSType.CWS: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                    },
                },
            },
        },
        RequestCategory.EMERGENCY: {
            "name": "Аварийная",
            "subcategories": {
                RequestSubcategory.LIFT: {
                    "name": "Лифт",
                    "parent": RequestCategory.EMERGENCY,
                    "work_areas": {
                        RequestWorkArea.HOUSE: {
                            "name": "В доме",
                            "actions": {
                                ActionRSType.LIFT: {"name": "Отключить лифт", "notify_title": "Лифт отключен"},
                            },
                        },
                        RequestWorkArea.PORCH: {
                            "name": "В подъезде",
                            "actions": {
                                ActionRSType.LIFT: {"name": "Отключить лифт", "notify_title": "Лифт отключен"},
                            },
                        },
                    },
                },
                RequestSubcategory.ELECTRICITY: {
                    "name": "Электроснабжение",
                    "parent": RequestCategory.EMERGENCY,
                    "work_areas": {
                        RequestWorkArea.HOUSE: {
                            "name": "В доме",
                            "actions": {
                                ActionRSType.ELECTRICITY: {"name": "Отключить Электроснабжение", "notify_title": "Электроснабжение отключено"},
                            },
                        },
                        RequestWorkArea.AREA: {
                            "name": "В квартире",
                            "actions": {
                                ActionRSType.ELECTRICITY: {"name": "Отключить Электроснабжение", "notify_title": "Электроснабжение отключено"},
                            },
                        },
                    },
                },
                RequestSubcategory.LEAK: {
                    "name": "Протечка",
                    "parent": RequestCategory.EMERGENCY,
                    "work_areas": {
                        RequestWorkArea.AREA: {
                            "name": "В квартире",
                            "actions": {
                                ActionRSType.CWS: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.CELLAR: {
                            "name": "В подвале",
                            "actions": {
                                ActionRSType.CWS: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.STANDPIPE: {
                            "name": "Стояк",
                            "actions": {
                                ActionRSType.CWS: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                    },
                },
            },
        },
        RequestCategory.VANDALISM: {
            "name": "Вандализм",
            "subcategories": {
                RequestSubcategory.WINDOWS: {
                    "name": "Окна",
                    "parent": RequestCategory.VANDALISM,
                },
                RequestSubcategory.SANITARY_WARE: {
                    "name": "Сантехника",
                    "parent": RequestCategory.VANDALISM,
                },
                RequestSubcategory.ELECTRICS: {
                    "name": "Электрика",
                    "parent": RequestCategory.VANDALISM,
                },
                RequestSubcategory.STAINED_GLASS: {
                    "name": "Витражи ГО",
                    "parent": RequestCategory.VANDALISM,
                },
                RequestSubcategory.DECORATION: {
                    "name": "Отделка",
                    "parent": RequestCategory.VANDALISM,
                },
            },
        },
        RequestCategory.VENTILATION: {
            "name": "Вентиляция",
        },
        RequestCategory.WATER_DISPOSAL: {
            "name": "Водоотведение",
        },
        RequestCategory.ROOF: {
            "name": "Кровля",
        },
        RequestCategory.SEALING: {
            "name": "Опломбирование",
        },
        RequestCategory.LEGAL_ISSUES: {
            "name": "Орг.-правовые вопросы ЖКХ",
        },
        RequestCategory.FACADES: {
            "name": "Фасады",
        },
    },
}
