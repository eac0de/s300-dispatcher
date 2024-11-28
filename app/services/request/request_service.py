"""
Модуль для работы с заявками
"""

from datetime import datetime
from random import randint

from beanie import PydanticObjectId
from fastapi import HTTPException
from starlette import status

from client.s300.api import S300API
from client.s300.models.employee import EmployeeS300
from client.s300.models.house import HouseS300
from client.s300.models.tenant import TenantS300
from config import settings
from models.base.binds import ProviderHouseGroupBinds
from models.other.other_employee import OtherEmployee
from models.other.other_person import OtherPerson
from models.other.other_provider import OtherProvider
from models.request.categories_tree import (
    CATEGORY_SUBCATEGORY_WORK_AREA_TREE,
    RequestCategory,
    RequestSubcategory,
    RequestWorkArea,
)
from models.request.embs.action import (
    ActionRS,
    ActionRSType,
    LiftShutdownActionRS,
    StandpipeShutdownActionRS,
)
from models.request.embs.area import AreaRS
from models.request.embs.employee import ProviderRS
from models.request.embs.house import HouseRS
from models.request.embs.requester import (
    EmployeeRequester,
    OtherEmployeeRequester,
    OtherPersonRequester,
    RequesterType,
    TenantRequester,
)
from models.request.request import RequestModel


class RequestService:
    """
    Сервис работы с заявками не привязанный к пользователю
    """

    @staticmethod
    async def _get_requester(
        requester_id: PydanticObjectId,
        requester_type: RequesterType,
    ) -> TenantRequester | OtherPersonRequester | EmployeeRequester | OtherEmployeeRequester:
        if requester_type == RequesterType.TENANT:
            tenant = await TenantS300.get(requester_id)
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tenant not found",
                )
            return TenantRequester(
                _id=requester_id,
                short_name=tenant.short_name,
                full_name=tenant.full_name,
                phone_numbers=tenant.phone_numbers,
                email=tenant.email,
                area=AreaRS.model_validate(tenant.area.model_dump(by_alias=True)),
                house=HouseRS.model_validate(tenant.house.model_dump(by_alias=True)),
            )
        if requester_type == RequesterType.EMPLOYEE:
            employee = await EmployeeS300.get(requester_id)
            if not employee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee not found",
                )
            return EmployeeRequester(
                _id=requester_id,
                short_name=employee.short_name,
                full_name=employee.full_name,
                phone_numbers=employee.phone_numbers,
                email=employee.email,
                position_name=employee.position.name,
                provider=ProviderRS.model_validate(employee.provider.model_dump(by_alias=True)),
            )
        if requester_type == RequesterType.OTHER_EMPLOYEE:
            other_employee = await OtherEmployee.get(requester_id)
            if not other_employee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Other employee not found",
                )
            other_provider = await OtherProvider.get(other_employee.provider_id)
            if not other_provider:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Other employee contains a non-existent provider_id",
                )
            return OtherEmployeeRequester(
                _id=requester_id,
                short_name=other_employee.short_name,
                full_name=other_employee.full_name,
                phone_numbers=other_employee.phone_numbers,
                email=other_employee.email,
                position_name=other_employee.position_name,
                provider=other_provider,
            )
        other_person = await OtherPerson.get(requester_id)
        if not other_person:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="other person not found",
            )
        return OtherPersonRequester(
            _id=requester_id,
            short_name=other_person.short_name,
            full_name=other_person.full_name,
            phone_numbers=other_person.phone_numbers,
            email=other_person.email,
        )

    @staticmethod
    async def _check_categories_tree(
        house: HouseS300,
        category: RequestCategory,
        subcategory: RequestSubcategory | None = None,
        work_area: RequestWorkArea | None = None,
        actions: list[ActionRS | LiftShutdownActionRS | StandpipeShutdownActionRS] | None = None,
    ):
        c = CATEGORY_SUBCATEGORY_WORK_AREA_TREE["categories"].get(category)
        if not c:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Non-existent category",
            )
        s = None
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
        wa = None
        if work_area:
            if not s:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Subcategory not selected",
                )
            if not s.get("work_areas"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Subcategory does not have a work area",
                )
            wa = s["work_areas"].get(work_area)
            if not wa:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Non-existing work area",
                )
        if actions:
            if not wa:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Work area not selected",
                )
            if not wa.get("actions"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The work area does not contain any possible actions",
                )
            for action in actions:
                a = wa["actions"].get(action.type)
                if not a:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Non-existent action",
                    )
                if action.start_at and action.end_at and action.start_at > action.end_at:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="The start time of an action cannot be later than its end time",
                    )
                if action.type == ActionRSType.LIFT:
                    lift = house.get_lift(action.lift.id)
                    if not lift:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Lift with this id was not found in the house",
                        )
                elif action.type == ActionRSType.CENTRAL_HEATING or action.type == ActionRSType.CWS or action.type == ActionRSType.HWS:
                    standpipe = house.get_standpipe(action.standpipe.id)
                    if not standpipe:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Standpipe with this id was not found in the house",
                        )

    @staticmethod
    async def _generate_number():
        while True:
            number = "78"
            # Генерация 3 и 4 случайного разряда
            number += "{:02d}".format(randint(0, 99))
            # Генерация 5 и 6 случайного разряда за исключением чисел 01 … 12
            tmp_int = (randint(1, 87) + 13) % 100
            number += "{:02d}".format(tmp_int)
            # Генерация разрядов 7 … 13
            number += "{:07d}".format(randint(0, 9999999))
            if not await RequestModel.find_one({"number": number}):
                return number

    @staticmethod
    async def _get_provider_binds(
        provider_id: PydanticObjectId,
        execution_provider_id: PydanticObjectId,
        house: HouseS300,
    ) -> set[PydanticObjectId]:
        provider_bind = None
        execution_provider_bind = None
        udo_bind = None
        if not house.service_binds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The house has no binds to providers",
            )
        for bind in house.service_binds:
            end_at = bind.end_at if bind.end_at else datetime(year=9999, month=12, day=1)
            now = datetime.now()
            if bind.start_at > now or now > end_at or not bind.is_active:
                continue
            if bind.provider == execution_provider_id:
                execution_provider_bind = bind
            if bind.provider == provider_id:
                provider_bind = bind
            if bind.business_type == settings.BUSINESS_TYPE_UDO_ID:
                udo_bind = bind
        if not provider_bind or not execution_provider_bind:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Provider{"-owner" if provider_bind else "-executor"} of the application is not bind to the house',
            )
        if provider_id != execution_provider_bind:
            if provider_bind.group or provider_bind.is_public:
                if provider_bind.group != execution_provider_bind.group and provider_bind.is_public != execution_provider_bind.is_public:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Provider-executor and provider-owner of the application must be in the same group",
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Provider-owner of the application does not have a group",
                )
        result = {provider_id, execution_provider_id}
        if udo_bind and provider_bind.is_public:
            result.add(udo_bind.provider)
        return result

    async def _get_binds(
        self,
        house: HouseS300,
        provider_id: PydanticObjectId,
        execution_provider_id: PydanticObjectId,
        area_id: PydanticObjectId | None = None,
    ) -> ProviderHouseGroupBinds:
        pr = await self._get_provider_binds(
            provider_id=provider_id,
            execution_provider_id=execution_provider_id,
            house=house,
        )
        hg = await S300API.get_house_group_ids(
            house_id=house.id,
            area_id=area_id,
        )
        if not hg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No attachments to a group of houses were found",
            )
        binds = ProviderHouseGroupBinds(
            hg=hg,
            pr=pr,
        )
        return binds

    @staticmethod
    async def get_filetag_for_requester_attachment(request_id: PydanticObjectId) -> str:
        """
        Получение тега файла вложения заявителя

        Args:
            request_id (PydanticObjectId): Идентификатор заявки

        Returns:
            str: Тег
        """
        return f"requester_attachment {str(request_id)}"

    @staticmethod
    async def get_filetag_for_execution_attachment(request_id: PydanticObjectId) -> str:
        """
        Получение тега файла вложения сотрудников

        Args:
            request_id (PydanticObjectId): Идентификатор заявки

        Returns:
            str: Тег
        """
        return f"execution_attachment {str(request_id)}"

    @staticmethod
    async def get_filetag_for_execution_act(request_id: PydanticObjectId) -> str:
        """
        Получение тега файла акта выполненных работ

        Args:
            request_id (PydanticObjectId): Идентификатор заявки

        Returns:
            str: Тег
        """
        return f"execution_act {str(request_id)}"
