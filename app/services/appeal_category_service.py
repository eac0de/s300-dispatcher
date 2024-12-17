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
from models.appeal_category.appeal_category import AppealCategory
from schemes.appeal_category import AppealCategoryCUScheme


class AppealCategoryService:
    """
    Сервис для работы с категориями обращений
    """

    def __init__(
        self,
        employee: EmployeeS300,
    ):
        """
        Инициализация сервиса

        Args:
            employee (EmployeeS300): Сотрудник который работает с категориями обращений
        """
        self.employee = employee

    async def create_appeal_category(
        self,
        scheme: AppealCategoryCUScheme,
    ) -> AppealCategory:
        """
        Создание категории обращения

        Args:
            scheme (AppealCategoryCUScheme): Схема для создания категории обращения

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            AppealCategory: Созданный категория обращений
        """
        appeal_category = AppealCategory(
            provider_id=self.employee.provider.id,
            name=scheme.name,
            description=scheme.description,
        )
        try:
            return await appeal_category.save()
        except RevisionIdWasChanged as e:
            raise HTTPException(
                detail="The appeal category name cannot be repeated",
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from e

    async def update_appeal_category(
        self,
        appeal_category_id: PydanticObjectId,
        scheme: AppealCategoryCUScheme,
    ) -> AppealCategory:
        """
        Обновление категории обращений

        Args:
            appeal_category_id (PydanticObjectId): Идентификатор категории обращений
            scheme (AppealCategoryCUScheme): Схема для обновления категории обращений

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            AppealCategory: Созданная категория обращений
        """
        appeal_category = await self._get_appeal_category(appeal_category_id)
        appeal_category = AppealCategory(
            _id=appeal_category.id,
            provider_id=appeal_category.provider_id,
            **scheme.model_dump(by_alias=True),
        )
        try:
            return await appeal_category.save()
        except RevisionIdWasChanged as e:
            raise HTTPException(
                detail="The appeal category name cannot be repeated",
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from e

    async def delete_appeal_category(
        self,
        appeal_category_id: PydanticObjectId,
    ):
        """
        Удаление категории обращений

        Args:
            appeal_category_id (PydanticObjectId): Идентификатор категории обращений

        Raises:
            HTTPException: При неудовлетворительном запросе
        """
        appeal_category = await self._get_appeal_category(appeal_category_id)
        await appeal_category.delete()

    async def get_appeal_categories(
        self,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> FindMany[AppealCategory]:
        """
        Получение списка категорий обращений

        Returns:
            list[AppealCategory]: Список категорий обращений
        """
        query_list.append({"provider_id": self.employee.provider.id})
        appeal_categories = AppealCategory.find(*query_list)
        appeal_categories.sort(*sort if sort else ["-_id"])
        if offset:
            appeal_categories.skip(offset)
        if limit:
            appeal_categories.limit(limit)
        return appeal_categories

    async def _get_appeal_category(
        self,
        appeal_category_id: PydanticObjectId,
    ) -> AppealCategory:
        appeal_category = await AppealCategory.find_one(
            {
                "_id": appeal_category_id,
                "provider_id": self.employee.provider.id,
            }
        )
        if not appeal_category:
            raise HTTPException(
                detail="Appeal category not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return appeal_category
