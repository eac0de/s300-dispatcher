from datetime import datetime, timedelta

from telegram_sender import TelegramSender

from celery_app import celery_app
from utils.request.request_log import RequestLog


@celery_app.task
async def clear_logs() -> dict:
    """
    Задача на очистку базы данных от старых логов

    Returns:
        dict: Результат очистки
    """

    await TelegramSender.send("Очистка логов начата")
    try:
        before_registry_lifetime = datetime.now() - timedelta(days=7)
        request_logs_delete_result = await RequestLog.find({"request_time": {"$lte": before_registry_lifetime}}).delete()
        request_logs_deleted_count = request_logs_delete_result.deleted_count if request_logs_delete_result else 0
        await TelegramSender.send(f"Очистка логов окончена\n" f"Удалено RequestLog - {request_logs_deleted_count}")
        return {
            "deleted_RequestLog": request_logs_deleted_count,
        }
    except Exception as e:
        await TelegramSender.send(f"Ошибка очистки логов:\n" f"{str(e)}")
        raise
