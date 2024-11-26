"""
Модуль с настройками приложения
"""

import os
from typing import Literal

from beanie import PydanticObjectId
from pydantic import EmailStr, MongoDsn, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения
    """

    # common
    PROJECT_NAME: str = "s300-dispatcher"
    MODE: Literal["TEST", "DEV", "PROD"] = "DEV"
    TZ: str = "Europe/Moscow"
    PROJECT_DIR: str = os.path.dirname(os.path.abspath(__file__))

    # requests
    UNPAID_REQUEST_LIFETIME_MINUTE: int = 20

    # security
    SECURITY_TOKEN: str = "KAKA"

    # jwt
    JWT_SECRET_KEY: str = "KEK"
    JWT_ALGORITHM: str = "HS256"

    # for mail
    SMTP_SERVER: str = "smtp.eis24.me"
    SMTP_PORT: int = 25  # Порт SMTP сервера (обычно 587 для TLS)
    SMTP_USERNAME: str = "no_reply@eis24.me"
    SMTP_PASSWORD: str = "1d18b5CTc6Bb67"

    # c300
    C300_HOSTS: list[str] = [
        "http://10.1.1.213:8081",
    ]
    C300_API_PREFIX: str = "api/gw/request_service"
    C300_TOKEN: str = "YOAmBevZHkYk3zPjfQp4"

    # hosts
    REDIS_BROKER_URL: RedisDsn = "redis://localhost:6379/0"  # type: ignore
    MONGO_URI: MongoDsn = "mongodb://10.1.1.221:27017"  # type: ignore

    # dbs
    MAIN_DB: str = "system300_request_service_main"
    GRID_FS_DB: str = "system300_request_service_grid_fs"
    LOGS_DB: str = "system300_request_service_logs"

    # other
    BUSINESS_TYPE_UDO_ID: PydanticObjectId = PydanticObjectId("5427dc2bf3b7d44b1ae89b0e")

    # for test
    TEST_EMAIL: EmailStr = "zhea@eis24.me"

    # telegram
    TG_BOT_TOKEN: str = "7807646643:AAG4Bmro_dBzznHqq3ys90zs4pe_tFnSv3M"
    REQUEST_SERVICE_CHAT_ID: int = -1002457675475


settings = Settings()
