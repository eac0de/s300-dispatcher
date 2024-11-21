"""
Модуль для рендера шаблонов с использованием Jinja2.

Данный модуль предоставляет класс TemplateRenderer для асинхронного рендера шаблонов
и вспомогательную функцию для его инициализации.
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import settings


class TemplateRenderer:
    """
    Класс для асинхронного рендера шаблонов с использованием Jinja2.

    Attributes:
        env (Environment): Объект окружения Jinja2, настроенный на загрузку шаблонов и поддержку асинхронного рендера.
    """

    def __init__(self):
        """
        Инициализирует объект TemplateRenderer, настраивая окружение Jinja2.

        Загружает шаблоны из директории, заданной в настройках проекта, с поддержкой
        автоматического экранирования для файлов с расширениями .html и .xml.
        """
        template_folder = "/templates"
        self.env = Environment(
            loader=FileSystemLoader(settings.PROJECT_DIR + template_folder),
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=True,
        )

    async def render_template(self, template_name: str, context: dict) -> str:
        """
        Асинхронно рендерит шаблон с указанным контекстом.

        Args:
            template_name (str): Имя файла шаблона, который нужно отрендерить.
            context (dict): Словарь с данными, которые будут использованы в шаблоне.

        Returns:
            str: Рендеренный HTML-код.

        Raises:
            TemplateNotFound: Если указанный шаблон не найден в заданной директории.
            TemplateError: Если возникла ошибка при рендере шаблона.
        """
        template = self.env.get_template(template_name)
        return await template.render_async(context)


template_renderer = TemplateRenderer()


async def init_template_renderer():
    """
    Инициализирует объект template_renderer для использования в асинхронном цикле.

    Это позволяет перезагрузить или создать экземпляр TemplateRenderer при необходимости.
    """

    global template_renderer
    template_renderer = TemplateRenderer()
