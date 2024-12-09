"""
Модуль с кастомным инстансом Celery
"""

import asyncio
from asyncio import AbstractEventLoop
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

import celery
from file_manager import config_file_manager
from template_renderer import config_template_renderer

from config import settings
from database import init_db

T = TypeVar("T")


class Celery(celery.Celery):
    """Кастомный класс Celery для асинхронных функций

    Этот класс наследует от стандартного класса Celery и добавляет поддержку
    асинхронных задач, позволяя вызывать асинхронные функции из синхронных контекстов.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализация экземпляра Celery.

        Args:
            *args: Позиционные аргументы для конструктора Celery.
            **kwargs: Ключевые аргументы для конструктора Celery.

        В процессе инициализации происходит установка базы данных, GridFS и рендерера шаблонов.
        """
        super().__init__(*args, **kwargs)

        # тут хранятся функции для удобства тестирования (eager execution)
        self.functions: dict[str, Callable[..., Any]] = {}

        # цикл событий, чтобы из синхронной функции вызывать асинхронную
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(init_db())
        self.loop.run_until_complete(
            config_file_manager(
                mongo_uri=str(settings.MONGO_URI),
                db_name=settings.GRID_FS_DB,
            )
        )
        self.loop.run_until_complete(config_template_renderer(templates_path="static/templates"))

    def task(
        self,
        task: Callable[..., Awaitable[T]] | None = None,
        **opts: Any,
    ) -> Callable:
        """Декоратор для регистрации асинхронных задач.

        Этот метод позволяет зарегистрировать асинхронную функцию как задачу Celery,
        автоматически оборачивая ее так, чтобы ее можно было вызывать из синхронного контекста.

        Args:
            task (Callable[..., Awaitable[T]] | None): Функция задачи, если она передана.
            **opts: Дополнительные параметры для настройки задачи.

        Returns:
            Callable: Обернутая функция задачи, которую можно вызывать как задачу Celery.
        """
        create_task = super().task

        def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., T]:
            @create_task(**opts)
            @wraps(func)
            def wrapper(*args: Any, loop: AbstractEventLoop | None = None, **kwargs: Any) -> T:
                loop = loop or self.loop
                return loop.run_until_complete(func(*args, **kwargs))

            self.functions[wrapper.__name__] = func

            return wrapper

        if task:
            return decorator(task)

        return decorator


celery_app = Celery(
    settings.PROJECT_NAME,
    broker=str(settings.REDIS_BROKER_URL),
    backend=str(settings.REDIS_BROKER_URL),
    include=[
        "tasks.send_mail",
    ],
)

celery_app.conf.update(timezone=settings.TZ)

# celery_app.conf.beat_schedule = {
#     'generate_registries': {
#         'task': 'tasks.generate_registries.generate_registries',
#         'schedule': crontab(hour='2', minute='0'),  # Каждый день в два часа утра
#         'args': ()
#     },
# }
