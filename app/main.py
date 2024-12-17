"""
Модуль приложения FastAPI.

Данный модуль отвечает за инициализацию и конфигурацию веб-приложения FastAPI. 
Он включает в себя настройку маршрутов, middleware, обработку исключений, 
и инициализацию базы данных и других сервисов.

Основные компоненты:
- Инициализация базы данных.
- Настройка middleware для обработки времени выполнения и сжатия ответов.
- Определение маршрутов для обработки запросов.
- Обработка исключений и отправка уведомлений в Telegram.

Основные функции:
- Запуск приложения с использованием uvicorn.
"""

import traceback
from contextlib import asynccontextmanager

import jsony
import uvicorn
from email_sender import config_email_sender
from fastapi import FastAPI, Request
from file_manager import config_file_manager
from jsony_responses import JSONYResponse
from starlette import status
from starlette.middleware.gzip import GZipMiddleware
from telegram_sender import TelegramSender, config_telegram_sender
from template_renderer import config_template_renderer

from api.middlewares.procces_time_middleware import ProcessTimeMiddleware
from api.routers.appeal_category_router import appeal_category_router
from api.routers.constants_router import constants_router
from api.routers.dispatcher_appeal_router import dispatcher_appeal_router
from api.routers.dispatcher_catalog_item_router import dispatcher_catalog_item_router
from api.routers.dispatcher_request_router import dispatcher_request_router
from api.routers.employee_schedule_router import employee_schedule_router
from api.routers.gateway_request_router import gateway_request_router
from api.routers.other_router import other_router
from api.routers.request_template_router import request_template_router
from api.routers.tenant_catalog_item_router import tenant_catalog_item_router
from api.routers.tenant_request_router import tenant_request_router
from config import settings
from database import init_db
from errors import FailedDependencyError


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Контекстный менеджер для инициализации базы данных и других сервисов.

    Этот менеджер управляет инициализацией необходимых сервисов при
    запуске приложения и обеспечивает их корректное завершение.
    """
    await init_db()
    await config_file_manager(
        mongo_uri=str(settings.MONGO_URI),
        db_name=settings.GRID_FS_DB,
    )
    await config_template_renderer(
        templates_path="static/templates",
    )
    await config_telegram_sender(
        chat_id=settings.REQUEST_SERVICE_CHAT_ID,
        telegram_bot_token=settings.TG_BOT_TOKEN,
    )
    await config_email_sender(
        smtp_server=settings.SMTP_SERVER,
        smtp_port=settings.SMTP_PORT,
        smtp_username=settings.SMTP_USERNAME,
        smtp_password=settings.SMTP_PASSWORD,
        test_email=settings.TEST_EMAIL if settings.MODE != "PROD" else None,
    )
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    docs_url="/api/docs",
)


@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Обработчик исключений для внутренних серверных ошибок.

    Args:
        request (Request): HTTP запрос.
        exc (Exception): Исключение, которое произошло.

    Returns:
        JSONResponse: Ответ с информацией об ошибке.
    """
    tb = traceback.extract_tb(exc.__traceback__)
    last_call = tb[-1] if tb else None
    if last_call:
        error_location = f"File {last_call.filename}, line {last_call.lineno}, in {last_call.name}"
    else:
        error_location = "No traceback available"
    message = f"{request.method} {request.url}\n{error_location}\n{str(exc)}\nError type: {type(exc).__name__}"
    await TelegramSender.send(message)
    return JSONYResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc) if settings.MODE != "PROD" else "Internal server error"},
    )


@app.exception_handler(FailedDependencyError)
async def failed_dependency_error_handler(request: Request, exc: FailedDependencyError):
    """Обработчик исключений для ошибок зависимости.

    Args:
        request (Request): HTTP запрос.
        exc (FailedDependencyError): Исключение, которое произошло.

    Returns:
        JSONResponse: Ответ с информацией об ошибке зависимости.
    """
    await TelegramSender.send(
        "\n".join(
            [
                "FAILED_DEPENDENCY",
                f"{request.method} {request.url}",
                exc.description,
                jsony.dumps(exc.kwargs, indent=4, ensure_ascii=False),
            ]
        )
    )
    return JSONYResponse(
        status_code=status.HTTP_424_FAILED_DEPENDENCY,
        content={"detail": {"description": exc.description, **exc.kwargs}},
    )


# ___ Middlewares ___ #

app.add_middleware(
    ProcessTimeMiddleware,
)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)

# ___ Routers ___ #
app.include_router(
    router=dispatcher_request_router,
    prefix="/dispatcher/requests",
)
app.include_router(
    router=tenant_request_router,
    prefix="/tenant/requests",
)
app.include_router(
    router=gateway_request_router,
    prefix="/gateway/requests",
)
app.include_router(
    router=request_template_router,
    prefix="/dispatcher/request_templates",
)
app.include_router(
    router=dispatcher_catalog_item_router,
    prefix="/dispatcher/catalog",
)
app.include_router(
    router=tenant_catalog_item_router,
    prefix="/tenant/catalog",
)
app.include_router(
    router=employee_schedule_router,
    prefix="/dispatcher/employee_schedules",
)
app.include_router(
    router=other_router,
    prefix="/dispatcher/other",
)
app.include_router(
    router=constants_router,
    prefix="/constants",
)
app.include_router(
    router=dispatcher_appeal_router,
    prefix="/dispatcher/appeals",
)
app.include_router(
    router=appeal_category_router,
    prefix="/dispatcher/appeal_categories",
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8003, workers=3)
