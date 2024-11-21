from celery_app import celery_app
from config import settings
from utils.grid_fs.file import File
from utils.send_mail import MailBodyType, send_mail
from utils.template_renderer import template_renderer


@celery_app.task
async def send_html_mail(
    template_name: str,
    context: dict,
    subject: str,
    to_email: str,
    from_email: str = settings.SMTP_USERNAME,
    files: list[File] | None = None,
):
    """
    Функция для отправки рендером шаблона и отправкой электронных писем в HTML формате

    Args:
        template_name (str): Название шаблона в папке /templates
        context (dict): Контекст для рендеринга шаблона
        subject (str): Тема письма
        to_email (str): Адрес почты, на который отправляется письмо
        from_email (str): Адрес почты отправителя
        files (list[File]): Файлы для вложения

    Notes:
        - Функция может отдавать ошибки aiosmtplib библиотеки в ходе отправки письма
        - При работе на тестовом сервере to_email подменяется на тестовый
    """

    error = None
    try:
        mail_body = await template_renderer.render_template(
            template_name=template_name,
            context=context,
        )
        await send_mail(
            subject=subject,
            body=mail_body,
            to_email=to_email,
            from_email=from_email,
            files=files,
            body_type=MailBodyType.HTML,
        )
    except Exception as e:
        error = str(e)
    return dict(
        subject=subject,
        to_email=to_email,
        from_email=from_email,
        error=error,
    )
