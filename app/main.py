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

import json
import traceback
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from starlette import status
from starlette.middleware.gzip import GZipMiddleware

from api.middlewares.procces_time_middleware import ProcessTimeMiddleware
from api.routers.dispatcher_catalog_item_router import dispatcher_catalog_item_router
from api.routers.dispatcher_request_router import dispatcher_request_router
from api.routers.employee_schedule_router import employee_schedule_router
from api.routers.gateway_request_router import gateway_request_router
from api.routers.other_router import other_router
from api.routers.tenant_catalog_item_router import tenant_catalog_item_router
from api.routers.tenant_request_router import tenant_request_router
from config import settings
from database import init_db
from errors import FailedDependencyError
from utils.grid_fs.grid_fs import init_grid_fs_service
from utils.responses import JSONResponse, ObjectIdEncoder
from utils.telegram import send_notify_to_telegram


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Контекстный менеджер для инициализации базы данных и других сервисов.

    Этот менеджер управляет инициализацией необходимых сервисов при
    запуске приложения и обеспечивает их корректное завершение.
    """
    await init_db()
    await init_grid_fs_service()
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
    error_traceback = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    await send_notify_to_telegram(f"{request.method} {request.url}\n{error_traceback}")
    return JSONResponse(
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
    await send_notify_to_telegram(
        "\n".join(
            [
                "FAILED_DEPENDENCY",
                f"{request.method} {request.url}",
                exc.description,
                json.dumps(exc.kwargs, indent=4, ensure_ascii=False, cls=ObjectIdEncoder),
            ]
        )
    )
    return JSONResponse(
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8003, workers=3)
