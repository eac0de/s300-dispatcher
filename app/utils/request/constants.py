"""
Модуль с константами для работы с запросами
"""

from enum import Enum


class RequestMethod(str, Enum):
    """
    HTTP-глаголы для работы с запросами
    """

    GET = "get"
    POST = "post"
    PATCH = "patch"
    PUT = "put"
    DELETE = "delete"
