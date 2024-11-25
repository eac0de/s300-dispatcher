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
        RequestCategory.BUILDING_RENOVATION.value: {
            "name": "Ремонт строения/дома",
            "subcategories": {
                RequestSubcategory.GENERAL_PROPERTY.value: {
                    "name": "Общее имущество",
                    "parent": RequestCategory.BUILDING_RENOVATION.value,
                },
                RequestSubcategory.CURRENT_REPAIR.value: {
                    "name": "Текущий ремонт",
                    "parent": RequestCategory.BUILDING_RENOVATION.value,
                },
            },
        },
        RequestCategory.TERRITORY.value: {
            "name": "Территория",
            "subcategories": {
                RequestSubcategory.SANITATION.value: {
                    "name": "Сан.содержание",
                    "parent": RequestCategory.TERRITORY.value,
                },
                RequestSubcategory.IMPROVEMENT.value: {
                    "name": "Благоустройство",
                    "parent": RequestCategory.TERRITORY.value,
                },
            },
        },
        RequestCategory.COMMERCIAL.value: {
            "name": "Коммерческая",
            "subcategories": {
                RequestSubcategory.CHARGEABLE.value: {
                    "name": "Платная",
                    "parent": RequestCategory.COMMERCIAL.value,
                    "work_areas": {
                        RequestWorkArea.AREA.value: {
                            "name": "В квартире",
                            "actions": {
                                ActionRSType.CWS.value: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS.value: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING.value: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.CELLAR.value: {
                            "name": "В подвале",
                            "actions": {
                                ActionRSType.CWS.value: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS.value: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING.value: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.STANDPIPE.value: {
                            "name": "Стояк",
                            "actions": {
                                ActionRSType.CWS.value: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS.value: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING.value: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                    },
                },
                RequestSubcategory.WARRANTY.value: {
                    "name": "Гарантийная",
                    "parent": RequestCategory.COMMERCIAL.value,
                    "work_areas": {
                        RequestWorkArea.AREA.value: {
                            "name": "В квартире",
                            "actions": {
                                ActionRSType.CWS.value: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS.value: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING.value: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.CELLAR.value: {
                            "name": "В подвале",
                            "actions": {
                                ActionRSType.CWS.value: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS.value: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING.value: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.STANDPIPE.value: {
                            "name": "Стояк",
                            "actions": {
                                ActionRSType.CWS.value: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS.value: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING.value: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                    },
                },
            },
        },
        RequestCategory.EMERGENCY.value: {
            "name": "Аварийная",
            "subcategories": {
                RequestSubcategory.LIFT.value: {
                    "name": "Лифт",
                    "parent": RequestCategory.EMERGENCY.value,
                    "work_areas": {
                        RequestWorkArea.HOUSE.value: {
                            "name": "В доме",
                            "actions": {
                                ActionRSType.LIFT.value: {"name": "Отключить лифт", "notify_title": "Лифт отключен"},
                            },
                        },
                        RequestWorkArea.PORCH.value: {
                            "name": "В подъезде",
                            "actions": {
                                ActionRSType.LIFT.value: {"name": "Отключить лифт", "notify_title": "Лифт отключен"},
                            },
                        },
                    },
                },
                RequestSubcategory.ELECTRICITY.value: {
                    "name": "Электроснабжение",
                    "parent": RequestCategory.EMERGENCY.value,
                    "work_areas": {
                        RequestWorkArea.HOUSE.value: {
                            "name": "В доме",
                            "actions": {
                                ActionRSType.ELECTRICITY.value: {"name": "Отключить Электроснабжение", "notify_title": "Электроснабжение отключено"},
                            },
                        },
                        RequestWorkArea.AREA.value: {
                            "name": "В квартире",
                            "actions": {
                                ActionRSType.ELECTRICITY.value: {"name": "Отключить Электроснабжение", "notify_title": "Электроснабжение отключено"},
                            },
                        },
                    },
                },
                RequestSubcategory.LEAK.value: {
                    "name": "Протечка",
                    "parent": RequestCategory.EMERGENCY.value,
                    "work_areas": {
                        RequestWorkArea.AREA.value: {
                            "name": "В квартире",
                            "actions": {
                                ActionRSType.CWS.value: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS.value: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING.value: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.CELLAR.value: {
                            "name": "В подвале",
                            "actions": {
                                ActionRSType.CWS.value: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS.value: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING.value: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                        RequestWorkArea.STANDPIPE.value: {
                            "name": "Стояк",
                            "actions": {
                                ActionRSType.CWS.value: {"name": "Отключить стояк ХВС", "notify_title": "Стояк ХВС отключен"},
                                ActionRSType.HWS.value: {"name": "Отключить стояк ГВС", "notify_title": "Стояк ГВС отключен"},
                                ActionRSType.CENTRAL_HEATING.value: {"name": "Отключить стояк ЦО", "notify_title": "Стояк ЦО отключен"},
                            },
                        },
                    },
                },
            },
        },
        RequestCategory.VANDALISM.value: {
            "name": "Вандализм",
            "subcategories": {
                RequestSubcategory.WINDOWS.value: {
                    "name": "Окна",
                    "parent": RequestCategory.VANDALISM.value,
                },
                RequestSubcategory.SANITARY_WARE.value: {
                    "name": "Сантехника",
                    "parent": RequestCategory.VANDALISM.value,
                },
                RequestSubcategory.ELECTRICS.value: {
                    "name": "Электрика",
                    "parent": RequestCategory.VANDALISM.value,
                },
                RequestSubcategory.STAINED_GLASS.value: {
                    "name": "Витражи ГО",
                    "parent": RequestCategory.VANDALISM.value,
                },
                RequestSubcategory.DECORATION.value: {
                    "name": "Отделка",
                    "parent": RequestCategory.VANDALISM.value,
                },
            },
        },
        RequestCategory.VENTILATION.value: {
            "name": "Вентиляция",
        },
        RequestCategory.WATER_DISPOSAL.value: {
            "name": "Водоотведение",
        },
        RequestCategory.ROOF.value: {
            "name": "Кровля",
        },
        RequestCategory.SEALING.value: {
            "name": "Опломбирование",
        },
        RequestCategory.LEGAL_ISSUES.value: {
            "name": "Орг.-правовые вопросы ЖКХ",
        },
        RequestCategory.FACADES.value: {
            "name": "Фасады",
        },
    },
}
