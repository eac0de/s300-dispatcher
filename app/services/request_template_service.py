"""
Модуль с сервисом для работы с шаблонами заявок
"""

from typing import Any

from beanie import PydanticObjectId
from beanie.exceptions import RevisionIdWasChanged
from beanie.odm.queries.find import FindMany
from fastapi import HTTPException
from starlette import status

from client.s300.models.employee import EmployeeS300
from models.request.categories_tree import (
    CATEGORY_SUBCATEGORY_WORK_AREA_TREE,
    RequestCategory,
    RequestSubcategory,
)
from models.request.request import RequestModel
from models.request_template.constants import RequestTemplateType
from models.request_template.request_template import RequestTemplate
from schemes.request_template_scheme import RequestTemplateCUScheme


class RequestTemplateService:
    """
    Сервис для работы с шаблонами заявок
    """

    def __init__(
        self,
        employee: EmployeeS300,
    ):
        """
        Инициализация сервиса

        Args:
            employee (EmployeeS300): Сотрудник который работает с шаблонами заявок
        """
        self.employee = employee

    async def create_template(
        self,
        scheme: RequestTemplateCUScheme,
    ) -> RequestTemplate:
        """
        Создание шаблона заявок

        Args:
            scheme (RequestTemplateCUScheme): Схема для создания шаблона заявок

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestTemplate: Созданный шаблон заявок
        """
        if scheme.type == RequestTemplateType.REQUEST:
            if not scheme.category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request template with type 'request' requires a category",
                )
            await self._check_categories_tree(
                category=scheme.category,
                subcategory=scheme.subcategory,
            )
        request_template = RequestTemplate(
            provider_id=self.employee.provider.id,
            name=scheme.name,
            category=scheme.category,
            subcategory=scheme.subcategory,
            _type=scheme.type,
            body=scheme.body,
        )
        try:
            request_template = await request_template.save()
        except RevisionIdWasChanged as e:
            raise HTTPException(
                detail="The request template name cannot be repeated",
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from e
        return request_template

    async def update_template(
        self,
        request_template_id: PydanticObjectId,
        scheme: RequestTemplateCUScheme,
    ) -> RequestTemplate:
        """
        Обновление шаблона заявок

        Args:
            request_template_id (PydanticObjectId): Идентификатор шаблона заявок
            scheme (RequestTemplateCUScheme): Схема для обновления шаблона заявок

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestTemplate: Созданный шаблон заявок
        """
        request_template = await self._get_template(request_template_id)
        is_request_type = scheme.type == RequestTemplateType.REQUEST
        if is_request_type:
            if not scheme.category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request template with type 'request' requires a category",
                )
            await self._check_categories_tree(
                category=scheme.category,
                subcategory=scheme.subcategory,
            )
        else:
            scheme.category = None
            scheme.subcategory = None
        request_template = RequestTemplate(
            _id=request_template.id,
            provider_id=request_template.provider_id,
            **scheme.model_dump(by_alias=True),
        )
        request_template = await request_template.save()
        return request_template

    async def delete_template(
        self,
        request_template_id: PydanticObjectId,
    ):
        """
        Удаление шаблона заявок

        Args:
            request_template_id (PydanticObjectId): Идентификатор шаблона заявок

        Raises:
            HTTPException: При неудовлетворительном запросе
        """
        request_template = await self._get_template(request_template_id)
        if await RequestModel.find({"relations.template_id": request_template.id}).exists():
            raise HTTPException(
                detail="Шаблон задействован в заявках",
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
            )
        await request_template.delete()

    async def get_templates(
        self,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> FindMany[RequestTemplate]:
        """
        Получение списка шаблонов заявок

        Returns:
            list[RequestTemplate]: Список шаблонов заявок
        """
        query_list.append({"provider_id": self.employee.provider.id})
        templates = RequestTemplate.find(*query_list)
        templates.sort(*sort if sort else ["-_id"])
        if offset:
            templates.skip(offset)
        if limit:
            templates.limit(limit)
        return templates

    @staticmethod
    async def _check_categories_tree(
        category: RequestCategory,
        subcategory: RequestSubcategory | None = None,
    ):
        c = CATEGORY_SUBCATEGORY_WORK_AREA_TREE["categories"].get(category)
        if not c:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Non-existent category",
            )
        if subcategory:
            if not c.get("subcategories"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category has no subcategory",
                )
            s = c["subcategories"].get(subcategory)
            if not s:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Non-existent subcategory",
                )

    async def _get_template(
        self,
        request_template_id: PydanticObjectId,
    ) -> RequestTemplate:
        request_template = await RequestTemplate.find_one(
            {
                "_id": request_template_id,
                "provider_id": self.employee.provider.id,
            }
        )
        if not request_template:
            raise HTTPException(
                detail="Request template not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return request_template
