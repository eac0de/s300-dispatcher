"""
Модуль для отправки электронных писем.

Этот модуль предоставляет функциональность для асинхронной отправки писем с использованием библиотеки aiosmtplib. 
Он поддерживает текстовые и HTML сообщения, а также возможность прикрепления файлов.

Зависимости:
    - aiosmtplib: Библиотека для асинхронной отправки SMTP сообщений.
    - config: Модуль с настройками проекта, включая данные для SMTP сервера.
    - utils.grid_fs.file: Модуль для работы с файлами.

Классы:
    - MailBodyType: Перечисление для определения типа тела письма.

Функции:
    - send_mail(subject: str, body: str, to_email: str, from_email: str, files: list[File], body_type: MAIL_BODY_TYPE_CHOICES): Асинхронно отправляет электронное письмо.

Примечания:
    - В режиме разработки (DEV) адрес получателя заменяется на тестовый адрес.
    - При отправке письма могут возникнуть ошибки, связанные с библиотекой aiosmtplib.
"""

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum

import aiosmtplib

from config import settings
from utils.grid_fs.file import File


class MailBodyType(str, Enum):
    """
    Перечисление для определения типа тела письма.

    Attributes:
        PLAIN: Обычный текст.
        HTML: HTML формат.
    """

    PLAIN = "plain"
    HTML = "html"


async def send_mail(
    subject: str,
    body: str,
    to_email: str,
    from_email: str = settings.SMTP_USERNAME,
    files: list[File] | None = None,
    body_type: MailBodyType = MailBodyType.PLAIN,
):
    """
    Асинхронная функция для отправки электронных писем.

    Args:
        subject (str): Тема письма.
        body (str): Тело сообщения.
        to_email (str): Адрес почты, на который отправляется письмо.
        from_email (str): Адрес почты отправителя.
        files (list[File]): Список файлов для вложения (по умолчанию None).
        body_type (MailBodyType): Тип тела письма (по умолчанию MailBodyType.PLAIN).

    Notes:
        - В режиме разработки (DEV) адрес получателя заменяется на тестовый адрес, указанный в настройках.
        - Возможны ошибки при отправке письма, связанные с библиотекой aiosmtplib.

    Example:
        await send_mail(
            subject="Тестовое письмо",
            body="Это тестовое сообщение",
            to_email="recipient@example.com",
            files=[file_instance],
            body_type=MailBodyType.HTML
        )
    """

    if settings.MODE != "PROD":
        to_email = settings.TEST_EMAIL

    # Создание сообщения
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, body_type.value))
    if files:
        for file in files:
            part = MIMEApplication(await file.read(), Name=file.name)
            part["Content-Disposition"] = f'attachment; filename="{file.name}"'
            part.add_header("Content-Type", file.content_type)
            msg.attach(part)
    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_SERVER,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
    )
