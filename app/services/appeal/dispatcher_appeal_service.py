from datetime import datetime, timedelta
from typing import Any

from beanie import PydanticObjectId
from beanie.odm.queries.find import FindMany
from fastapi import HTTPException
from file_manager import File
from starlette import status

from client.s300.models.department import DepartmentS300
from client.s300.models.employee import EmployeeS300
from client.s300.models.tenant import TenantS300
from models.appeal.appeal import Appeal
from models.appeal.constants import AppealSource, AppealStatus
from models.appeal.embs.appealer import Appealer
from models.appeal.embs.employee import DispatcherAS, EmployeeAS, ProviderAS
from models.appeal.embs.observers import EmployeeObserverAS, ObserversAS
from models.appeal_control_right.appeal_control_right import AppealControlRight
from models.appeal_control_right.constants import AppealControlRightType
from models.base.binds import DepartmentBinds
from schemes.appeal.dispatcher_appeal import AppealDCScheme
from services.appeal.appeal_service import AppealService


class DispatcherAppealService(AppealService):

    def __init__(self, employee: EmployeeS300):

        super().__init__()
        self.employee = employee

    async def get_appeals(
        self,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> FindMany[Appeal]:
        query_list.append({"provider_id": self.employee.provider.id})
        appeal_control_right = await AppealControlRight.find_one({"employee_id": self.employee.id})
        if appeal_control_right:
            if appeal_control_right.type == AppealControlRightType.DEPARTMENT:
                query_list.append(
                    {
                        "$or": [
                            {"_binds.dp": self.employee.department.id},
                            {"dispatcher._id": self.employee.id},
                        ]
                    }
                )
        else:
            query_list.append(
                {
                    "$or": [
                        {"observers.departments": [], "observers.employees": []},
                        {"dispatcher._id": self.employee.id},
                    ]
                }
            )
        requests = Appeal.find(*query_list)
        requests.sort(*sort if sort else ["-_id"])
        if offset:
            requests.skip(offset)
        if limit:
            requests.limit(limit)
        return requests

    async def get_appeal(
        self,
        appeal_id: PydanticObjectId,
    ) -> Appeal:
        query: dict = {"_id": appeal_id, "provider_id": self.employee.provider.id}
        appeal_control_right = await AppealControlRight.find_one({"employee_id": self.employee.id})
        if appeal_control_right:
            if appeal_control_right.type == AppealControlRightType.DEPARTMENT:
                query["$or"] = [
                    {"_binds.dp": self.employee.department.id},
                    {"dispatcher._id": self.employee.id},
                ]

        else:
            query["$or"] = [
                {"observers.departments": [], "observers.employees": []},
                {"dispatcher._id": self.employee.id},
            ]
        appeal = await Appeal.find_one(query)
        if not appeal:
            raise HTTPException(
                detail="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return appeal

    async def create_appeal(
        self,
        scheme: AppealDCScheme,
    ) -> Appeal:
        current_time = datetime.now()
        await self._check_categories(scheme.category_ids, self.employee.provider.id)
        tenant = await TenantS300.get(scheme.appealer.id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant not found",
            )
        appealer = Appealer.model_validate(tenant.model_dump(by_alias=True))
        dispatcher = DispatcherAS.model_validate(self.employee.model_dump(by_alias=True))
        provider_as = ProviderAS.model_validate(self.employee.provider.model_dump(by_alias=True))
        number = await self._generate_number(self.employee.provider.id, current_time)
        binds = DepartmentBinds()
        executor = None
        observers = ObserversAS()
        if len(set(e.id for e in scheme.observers.employees)) == 1 and not scheme.observers.departments:
            employee = await EmployeeS300.get(scheme.observers.employees[0].id)
            if not employee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee not found",
                )
            executor = EmployeeAS.model_validate(employee.model_dump(by_alias=True))
            binds.dp.add(employee.department.id)
        elif scheme.observers.departments or scheme.observers.employees:
            for e in scheme.observers.employees:
                employee = await EmployeeS300.get(e.id)
                if not employee:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Employee not found",
                    )
                if employee.provider.id != self.employee.provider.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Employee from another provider",
                    )
                observers.employees.append(EmployeeObserverAS.model_validate(employee.model_dump(by_alias=True)))
                binds.dp.add(employee.department.id)
            for d in scheme.observers.departments:
                department = await DepartmentS300.get(d.id)
                if not department:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Department not found",
                    )
                if department.provider_id != self.employee.provider.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Department from another provider",
                    )
                binds.dp.add(department.id)
        else:
            department = await DepartmentS300.get_by_is_accepting_appeals(
                is_accepting_appeals=True,
                provider_id=self.employee.provider.id,
            )
            if department:
                binds.dp.add(department.id)
            else:
                binds.dp.add(self.employee.department.id)
        deadline_at = datetime.now() + timedelta(days=3)  # TODO Уточнить где брать дедлайн
        appeal = Appeal(
            created_at=current_time,
            subject=scheme.subject,
            description=scheme.description,
            dispatcher=dispatcher,
            appealer=appealer,
            executor=executor,
            status=AppealStatus.RUN,
            _type=scheme.type,
            observers=observers,
            category_ids=scheme.category_ids,
            _binds=binds,
            number=number,
            provider=provider_as,
            source=AppealSource.DISPATCHER,
            incoming_number=scheme.incoming_number,
            incoming_at=scheme.incoming_at,
            deadline_at=deadline_at,
        )
        return appeal

    async def delete_appeal(
        self,
        appeal_id: PydanticObjectId,
    ):
        appeal = await self.get_appeal(appeal_id)
        await appeal.delete()

    async def download_answer_file(
        self,
        appeal_id: PydanticObjectId,
        answer_id: PydanticObjectId,
        file_id: PydanticObjectId,
    ) -> File:
        appeal = await self.get_appeal(appeal_id)
        if not appeal.answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found",
            )
        if appeal.answer.id == answer_id:
            for file in appeal.answer.files:
                if file.id == file_id:
                    return file
        for answer in appeal.add_answers:
            if answer.id != answer_id:
                continue
            for file in answer.files:
                if file.id == file_id:
                    return file
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer file not found",
        )
