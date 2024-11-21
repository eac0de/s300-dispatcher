"""
Модуль с константами для позиций каталога
"""

from enum import Enum


class CatalogItemGroup(str, Enum):
    """
    Группы позиций каталога
    """

    ELECTRICS = "electrics"
    PLUMBING = "plumbing"


class CatalogMeasurementUnit(str, Enum):
    """
    Единицы измерения позиций каталога
    """

    THOUSAND_SETS = "thousand_sets"
    PLACE = "place"
    METER = "meter"
    SQUARE_METER = "square_meter"
    LITER = "liter"
    CUBIC_METER = "cubic_meter"
    KILOGRAM = "kilogram"
    TON = "ton"
    SHEET = "sheet"
    PRODUCT = "product"
    SET = "set"
    PAIR = "pair"
    ROLL = "roll"
    PACK = "pack"
    PIECE = "piece"
    THOUSAND_PIECES = "thousand_pieces"
    LINEAR_METER = "linear_meter"


CATALOG_MEASUREMENT_UNIT_EN_RU = {
    CatalogMeasurementUnit.THOUSAND_SETS: "Тысяча комплектов",
    CatalogMeasurementUnit.PLACE: "Место",
    CatalogMeasurementUnit.METER: "Метр",
    CatalogMeasurementUnit.SQUARE_METER: "Квадратный метр",
    CatalogMeasurementUnit.LITER: "Литр",
    CatalogMeasurementUnit.CUBIC_METER: "Кубический метр",
    CatalogMeasurementUnit.KILOGRAM: "Килограмм",
    CatalogMeasurementUnit.TON: "Тонна; метрическая тонна (1000 кг)",
    CatalogMeasurementUnit.SHEET: "Лист",
    CatalogMeasurementUnit.PRODUCT: "Изделие",
    CatalogMeasurementUnit.SET: "Набор",
    CatalogMeasurementUnit.PAIR: "Пара (2 шт.)",
    CatalogMeasurementUnit.ROLL: "Рулон",
    CatalogMeasurementUnit.PACK: "Упаковка",
    CatalogMeasurementUnit.PIECE: "Штука",
    CatalogMeasurementUnit.THOUSAND_PIECES: "Тысяча штук",
    CatalogMeasurementUnit.LINEAR_METER: "Погонный метр",
}
