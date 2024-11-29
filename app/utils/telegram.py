"""
Модуль для отправки уведомлений в Telegram.

Этот модуль предоставляет функциональность для асинхронной отправки уведомлений в Telegram-чат через использование API Telegram бота. 
Он гарантирует безопасность выполнения и подавляет исключения, что делает его пригодным для использования в критичных системах, где важно 
избегать остановки работы из-за ошибок уведомления.

Зависимости:
    - aiohttp: Библиотека для выполнения асинхронных HTTP-запросов.
    - config: Модуль с настройками проекта, включая токен бота и ID чата.

Функции:
    - send_notify_to_telegram(message: str): Асинхронно отправляет сообщение в указанный Telegram-чат.

Примечания:
    - Функция `send_notify_to_telegram` обрабатывает все исключения, включая сетевые ошибки и ошибки API Telegram.
    - Ожидание ответа на запрос ограничено 5 секундами для предотвращения долгих задержек при проблемах с сетью.
"""

import aiohttp

from config import settings


async def send_notify_to_telegram(message: str):
    """
    Асинхронная отправка уведомления в Telegram.

    Отправляет сообщение в указанный Telegram-чат через бот API.
    Функция безопасна, так как обрабатывает все исключения и не вызывает их вне себя.

    Args:
        message (str): Текст сообщения, которое нужно отправить.

    Notes:
        - Использует токен бота и ID чата, определенные в настройках проекта.
        - Все ошибки (например, сетевые сбои или ошибки API Telegram) подавляются.
        - Время ожидания ответа на запрос ограничено 5 секундами.

    Example:
        await send_notify_to_telegram("Тестовое сообщение")
    """
    try:
        url = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": settings.REQUEST_SERVICE_CHAT_ID,
            "text": message[:4000],
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=url,
                data=payload,
                timeout=5,  # type: ignore
            ):
                pass
    except:
        pass
