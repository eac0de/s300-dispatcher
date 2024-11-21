"""
Модуль с константами для истории изменения заявки
"""

from enum import Enum


class UpdateUserType(str, Enum):
    """
    Типы пользователя изменившего заявку
    """

    REQUESTER = "requester"
    EMPLOYEE = "employee"
