"""
Модуль с кастомными json энкодерами.

Классы:
    - EnhancedJSONEncoder: Кастомный JSON-энкодер.

Примечания:
    - Использование этого модуля упрощает интеграцию с базами данных MongoDB,
      предоставляя удобный способ сериализации данных для API-ответов.
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any

from beanie import PydanticObjectId
from bson import ObjectId


class EnhancedJSONEncoder(json.JSONEncoder):
    """
    Класс кастомного энкодера JSON.

    Этот класс расширяет стандартный JSON-энкодер
    """

    def default(self, o):
        if isinstance(o, (ObjectId, PydanticObjectId)):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.value
        if hasattr(o, "__iter__"):
            return list(o)

        # Let the base class default method raise the TypeError
        return super().default(o)

    @classmethod
    def normalize(cls, data: Any) -> Any:
        """Кодирует данные в JSON с помощью специального энкодера и декодирует обратно."""
        json_data = json.dumps(data, cls=cls)
        return json.loads(json_data)
