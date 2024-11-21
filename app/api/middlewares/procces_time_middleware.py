"""
Модуль с middleware ProcessTimeMiddleware
"""

import time

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class ProcessTimeMiddleware:
    """
    Middleware для отслеживания времени обработки запроса
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        start_time = time.time()

        async def send_with_process_time(message: Message):
            if message["type"] == "http.response.start":
                process_time = time.time() - start_time
                headers = MutableHeaders(raw=message["headers"])
                headers["X-Process-Time"] = f"{process_time:.4f} seconds"

            await send(message)

        # Передаем управление следующему обработчику, передавая свою функцию send
        await self.app(scope, receive, send_with_process_time)
