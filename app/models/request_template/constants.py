"""
Модуль с константами шаблона заявки
"""

from enum import Enum


class TemplateType(str, Enum):
    """
    Типы шаблона заявки
    """

    REQUEST = "request"
    PERFORMED = "performed"
    DELAYED = "delayed"
    ABANDONMENT = "abandonment"
    REFUSAL = "refusal"
