"""
Модуль с сервисом для работы со сторонними субъектами
"""

from typing import Any

from beanie import PydanticObjectId
from fastapi import HTTPException
from starlette import status

from client.c300.models.employee import EmployeeC300
from models.base.binds import ProviderBinds
from models.other.other_employee import OtherEmployee
from models.other.other_person import OtherPerson
from models.other.other_provider import OtherProvider
from schemes.other import (
    OtherEmployeeCUScheme,
    OtherPersonCUScheme,
    OtherProviderCUScheme,
)


class OtherService:
    """
    Сервис для работы со сторонними субъектами
    """

    def __init__(self, employee: EmployeeC300):
        """
        Инициализация сервиса

        Args:
            employee (EmployeeC300): Сотрудник работающий со сторонними субъектами
        """
        self.employee = employee

    async def get_other_person_list(
        self,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> list[OtherPerson]:
        """
        Получение списка сторонних лиц

        Args:
            query_list (list[dict[str, Any]]): Список словарей для составления запроса
            offset (int | None, optional): Количество пропускаемых документов. Defaults to None
            limit (int | None, optional): Количество документов. Defaults to None
            sort (list[str] | None, optional): Список полей для сортировки. Defaults to None

        Returns:
            list[OtherPerson]: Список сторонних лиц
        """
        query_list.append({"_binds.pr": self.employee.binds_permissions.pr})
        other_persons = OtherPerson.find(*query_list)
        other_persons.sort(*sort if sort else ["-_id"])
        other_persons.skip(0 if offset is None else offset)
        other_persons.limit(20 if limit is None else limit)
        return await other_persons.to_list()

    async def create_other_person(
        self,
        scheme: OtherPersonCUScheme,
    ) -> OtherPerson:
        """
        Создание стороннего лица

        Args:
            scheme (OtherPersonCUScheme): Схема для создания стороннего лица

        Returns:
            OtherPerson: Созданное стороннее лицо
        """
        short_name = await self._get_short_name(scheme.full_name)
        other_person = await OtherPerson(
            short_name=short_name,
            _binds=ProviderBinds(pr={self.employee.provider.id}),
            **scheme.model_dump(by_alias=True),
        ).save()
        return other_person

    async def update_other_person(
        self,
        other_person_id: PydanticObjectId,
        scheme: OtherPersonCUScheme,
    ) -> OtherPerson:
        """
        Обновление стороннего лица

        Args:
            other_person_id (PydanticObjectId): Идентификатор стороннего лица
            scheme (OtherPersonCUScheme): Схема для обновления стороннего лица

        Returns:
            OtherPerson: Обновленное стороннее лицо
        """
        other_person = await self._get_other_person(other_person_id)
        short_name = other_person.short_name
        if other_person.full_name != scheme.full_name:
            short_name = await self._get_short_name(scheme.full_name)
        other_person = await OtherPerson(
            _id=other_person.id,
            short_name=short_name,
            _binds=ProviderBinds(pr={self.employee.provider.id}),
            **scheme.model_dump(by_alias=True),
        ).save()
        return other_person

    async def delete_other_person(
        self,
        other_person_id: PydanticObjectId,
    ):
        """
        Удаление стороннего лица

        Args:
            other_person_id (PydanticObjectId): Идентификатор стороннего лица
        """
        other_person = await self._get_other_person(other_person_id)
        await other_person.delete()

    async def _get_other_person(
        self,
        other_person_id: PydanticObjectId,
    ) -> OtherPerson:
        query = {"_id": other_person_id}
        query.update(
            {
                "_binds.pr": self.employee.binds_permissions.pr,
            }
        )
        other_person = await OtherPerson.find_one(query)
        if not other_person:
            raise HTTPException(
                detail="Other person not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return other_person

    async def get_other_employee_list(
        self,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> list[OtherEmployee]:
        """
        Получение списка сторонних сотрудников

        Args:
            query_list (list[dict[str, Any]]): Список словарей для составления запроса
            offset (int | None, optional): Количество пропускаемых документов. Defaults to None
            limit (int | None, optional): Количество документов. Defaults to None
            sort (list[str] | None, optional): Список полей для сортировки. Defaults to None

        Returns:
            list[OtherEmployee]: Список сторонних сотрудников
        """
        query_list.append({"_binds.pr": self.employee.binds_permissions.pr})
        other_employees = OtherEmployee.find(*query_list)
        other_employees.sort(*sort if sort else ["-_id"])
        other_employees.skip(0 if offset is None else offset)
        other_employees.limit(20 if limit is None else limit)
        return await other_employees.to_list()

    async def create_other_employee(
        self,
        scheme: OtherEmployeeCUScheme,
    ) -> OtherEmployee:
        """
        Создание стороннего сотрудника

        Args:
            scheme (OtherEmployeeCUScheme): Схема для создания стороннего сотрудника

        Returns:
            OtherEmployee: Созданный сторонний сотрудник
        """
        provider = await OtherProvider.find_one({"_id": scheme.provider_id, "_binds.pr": self.employee.binds_permissions.pr})
        if not provider:
            raise HTTPException(
                detail="Other provider not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        short_name = await self._get_short_name(scheme.full_name)
        other_employee = await OtherEmployee(
            short_name=short_name,
            _binds=ProviderBinds(pr={self.employee.provider.id}),
            **scheme.model_dump(by_alias=True),
        ).save()
        return other_employee

    async def update_other_employee(
        self,
        other_employee_id: PydanticObjectId,
        scheme: OtherEmployeeCUScheme,
    ) -> OtherEmployee:
        """
        Обновление стороннего сотрудника

        Args:
            other_employee_id (PydanticObjectId): Идентификатор стороннего сотрудника
            scheme (OtherEmployeeCUScheme): Схема для обновления стороннего сотрудника

        Returns:
            OtherEmployee: Обновленный сторонний сотрудник
        """
        other_employee = await self._get_other_employee(other_employee_id)
        provider = None
        if other_employee.provider_id != scheme.provider_id:
            provider = await OtherProvider.get(scheme.provider_id)
            if not provider:
                raise HTTPException(
                    detail="Other provider not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
        short_name = other_employee.short_name
        if other_employee.full_name != scheme.full_name:
            short_name = await self._get_short_name(scheme.full_name)
        other_employee = await OtherEmployee(
            _id=other_employee.id,
            short_name=short_name,
            _binds=other_employee.binds,
            **scheme.model_dump(by_alias=True),
        ).save()
        return other_employee

    async def delete_other_employee(
        self,
        other_employee_id: PydanticObjectId,
    ):
        """
        Удаление стороннего сотрудника

        Args:
            other_employee_id (PydanticObjectId): Идентификатор стороннего сотрудника
        """
        other_employee = await self._get_other_employee(other_employee_id)
        await other_employee.delete()

    async def _get_other_employee(
        self,
        other_employee_id: PydanticObjectId,
    ) -> OtherEmployee:
        query = {"_id": other_employee_id}
        query.update(
            {
                "_binds.pr": self.employee.binds_permissions.pr,
            }
        )
        other_employee = await OtherEmployee.find_one(query)
        if not other_employee:
            raise HTTPException(
                detail="Other person not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return other_employee

    async def get_other_provider_list(
        self,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> list[OtherProvider]:
        """
        Получение списка сторонних организаций

        Args:
            query_list (list[dict[str, Any]]): Список словарей для составления запроса
            offset (int | None, optional): Количество пропускаемых документов. Defaults to None
            limit (int | None, optional): Количество документов. Defaults to None
            sort (list[str] | None, optional): Список полей для сортировки. Defaults to None

        Returns:
            list[OtherProvider]: Список сторонних организаций
        """
        query_list.append({"_binds.pr": self.employee.binds_permissions.pr})
        other_providers = OtherProvider.find(*query_list)
        other_providers.sort(*sort if sort else ["-_id"])
        other_providers.skip(0 if offset is None else offset)
        other_providers.limit(20 if limit is None else limit)
        return await other_providers.to_list()

    async def create_other_provider(
        self,
        scheme: OtherProviderCUScheme,
    ) -> OtherProvider:
        """
        Создание сторонней организации

        Args:
            scheme (OtherProviderCUScheme): Схема для создания сторонней организации

        Returns:
            OtherProvider: Созданная сторонняя организация
        """
        other_provider = await OtherProvider(
            _binds=ProviderBinds(pr={self.employee.provider.id}),
            **scheme.model_dump(by_alias=True),
        ).save()
        return other_provider

    async def update_other_provider(
        self,
        other_provider_id: PydanticObjectId,
        scheme: OtherProviderCUScheme,
    ) -> OtherProvider:
        """
        Обновление сторонней организации

        Args:
            other_provider_id (PydanticObjectId): Идентификатор сторонней организации
            scheme (OtherProviderCUScheme): Схема для обновления сторонней организации
        Returns:
            OtherProvider: Обновленная сторонняя организация
        """
        other_provider = await self._get_other_provider(other_provider_id)
        other_provider = await OtherProvider(
            _id=other_provider.id,
            _binds=other_provider.binds,
            **scheme.model_dump(by_alias=True),
        ).save()
        return other_provider

    async def delete_other_provider(
        self,
        other_provider_id: PydanticObjectId,
    ):
        """
        Удаление сторонней организации

        Args:
            other_provider_id (PydanticObjectId): Идентификатор сторонней организации
        """
        other_provider = await self._get_other_provider(other_provider_id)
        other_employee = await OtherEmployee.find_one({"provider_id": other_provider.id})
        if other_employee:
            raise HTTPException(
                detail="It is impossible to delete a other provider if at least 1 other employee is bound to it",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        await other_provider.delete()

    async def _get_other_provider(
        self,
        other_provider_id: PydanticObjectId,
    ) -> OtherProvider:
        query = {"_id": other_provider_id}
        query.update(
            {
                "_binds.pr": self.employee.binds_permissions.pr,
            }
        )
        other_provider = await OtherProvider.find_one(query)
        if not other_provider:
            raise HTTPException(
                detail="Other provider not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return other_provider

    @staticmethod
    async def _get_short_name(full_name: str) -> str:
        """
        Генерирует сокращенное имя из полного имени.

        Args:
            full_name (str): Полное имя, состоящее из трех слов.

        Returns:
            str: Сокращенное имя в формате "Фамилия И. О.".

        Raises:
            HTTPException: Если `full_name` не состоит ровно из трех слов.
        """
        # Удаляем лишние пробелы и делим на слова
        full_name_split = list(filter(bool, full_name.strip().split(" ")))
        full_name_split_len = len(full_name_split)
        if full_name_split_len == 2:
            f, i = full_name_split
            return f"{f} {i[0]}."
        if full_name_split_len != 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The 'full_name' field must consist of exactly 3 words separated by spaces.",
            )
        f, i, o = full_name_split
        return f"{f} {i[0]}. {o[0]}."
