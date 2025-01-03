from datetime import datetime, timedelta
from typing import Any

from beanie import PydanticObjectId
from beanie.odm.queries.find import FindMany
from client.s300.models.department import DepartmentS300
from client.s300.models.employee import AppealAccessLevel, EmployeeS300
from client.s300.models.tenant import TenantS300
from fastapi import HTTPException
from file_manager import File
from models.appeal.appeal import Appeal
from models.appeal.constants import AppealSource, AppealStatus
from models.appeal.embs.appealer import Appealer
from models.appeal.embs.employee import DispatcherAS, EmployeeAS, ProviderAS
from models.appeal.embs.observers import EmployeeObserverAS, ObserversAS
from models.appeal_comment.appeal_comment import AppealComment
from models.base.binds import DepartmentBinds
from schemes.appeal.appeal_stats import AppealStats
from schemes.appeal.dispatcher_appeal import AppealCommentStats, AppealDCScheme
from services.appeal.appeal_service import AppealService
from starlette import status


class DispatcherAppealService(AppealService):

    def __init__(self, employee: EmployeeS300):

        super().__init__()
        self.employee = employee

    async def get_appeal_stats(
        self,
    ) -> AppealStats:
        """
        Получение статистики по заявкам

        Returns:
            RequestStats: Результат
        """
        current_time = datetime.now()
        pipeline = [
            {
                "$match": {
                    "provider._id": self.employee.provider.id,
                }
            },
            {
                "$addFields": {
                    "is_overdue": {
                        "$cond": {
                            "if": {"$lt": ["$deadline_at", current_time]},
                            "then": True,
                            "else": False,
                        }
                    }
                }
            },
            {
                "$facet": {
                    "accepted": [
                        {"$match": {"status": AppealStatus.NEW}},
                        {"$count": "count"},
                    ],
                    "run": [
                        {"$match": {"status": AppealStatus.RUN}},
                        {"$count": "count"},
                    ],
                    "overdue": [
                        {"$match": {"is_overdue": True}},
                        {"$count": "count"},
                    ],
                    "performed": [
                        {"$match": {"status": AppealStatus.PERFORMED}},
                        {"$count": "count"},
                    ],
                }
            },
        ]

        result = await Appeal.aggregate(pipeline).to_list()
        stats = result[0] if result else {}
        return AppealStats(
            accepted=stats["accepted"][0].get("count", 0) if stats.get("accepted") else 0,
            run=stats["run"][0].get("count", 0) if stats.get("run") else 0,
            overdue=stats["overdue"][0].get("count", 0) if stats.get("overdue") else 0,
            performed=stats["performed"][0].get("count", 0) if stats.get("performed") else 0,
        )

    async def get_appeals(
        self,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> FindMany[Appeal]:
        query_list.append(await self._get_employee_query_binds())
        appeals = Appeal.find(*query_list)
        appeals.sort(*sort if sort else ["-_id"])
        if offset:
            appeals.skip(offset)
        if limit:
            appeals.limit(limit)
        return appeals

    async def get_comment_stats_dict(
        self,
        appeal_ids: list[PydanticObjectId],
        employee_id: PydanticObjectId,
    ) -> dict[PydanticObjectId, AppealCommentStats]:
        pipeline = [
            {"$match": {"appeal_id": {"$in": appeal_ids}}},
            {
                "$group": {
                    "_id": "$appeal_id",
                    "all": {"$sum": 1},
                    "unread": {"$sum": {"$cond": [{"$not": [{"$in": [employee_id, "$read_by"]}]}, 1, 0]}},
                }
            },
        ]

        result = await AppealComment.aggregate(pipeline).to_list()
        stats = {item["_id"]: AppealCommentStats(all=item["all"], unread=item["unread"]) for item in result}
        return stats

    async def get_appeal(
        self,
        appeal_id: PydanticObjectId,
    ) -> Appeal:
        query: dict = {
            "_id": appeal_id,
        }
        query.update(await self._get_employee_query_binds())
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
            department = await DepartmentS300.get_by_is_accepting_appeals(self.employee)

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
            status=AppealStatus.RUN if executor else AppealStatus.NEW,
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
        return await appeal.save()

    async def delete_appeal(
        self,
        appeal_id: PydanticObjectId,
    ):
        appeal = await self.get_appeal(appeal_id)
        await appeal.delete()

    async def download_appealer_file(
        self,
        appeal_id: PydanticObjectId,
        file_id: PydanticObjectId,
    ) -> File:
        appeal = await self.get_appeal(appeal_id)
        for file in appeal.appealer_files:
            if file.id == file_id:
                return file
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appealer file not found",
        )

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

    async def get_appeal_comments(
        self,
        appeal_id: PydanticObjectId,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> list[AppealComment]:
        appeal = await self.get_appeal(appeal_id)
        query_list.append({"appeal_id": appeal.id})
        appeal_comments = AppealComment.find(*query_list)
        appeal_comments.sort(*sort if sort else ["-_id"])
        if offset:
            appeal_comments.skip(offset)
        if limit:
            appeal_comments.limit(limit)
        appeal_comment_list = await appeal_comments.to_list()
        for comment in appeal_comment_list:
            if self.employee.id in comment.read_by:
                comment.read_by = {self.employee.id}
            else:
                comment.read_by = set()

        return appeal_comment_list

    async def download_comment_file(
        self,
        appeal_id: PydanticObjectId,
        comment_id: PydanticObjectId,
        file_id: PydanticObjectId,
    ) -> File:
        appeal = await self.get_appeal(appeal_id)
        comment = await AppealComment.find_one({"_id": comment_id, "appeal_id": appeal.id})
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        for file in comment.files:
            if file.id == file_id:
                return file
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment file not found",
        )

    async def _get_employee_query_binds(self) -> dict:
        query_binds: dict = {"provider._id": self.employee.provider.id}

        if self.employee.appeal_access_level != AppealAccessLevel.BASIC:
            if self.employee.appeal_access_level == AppealAccessLevel.DEPARTMENT:
                query_binds.update(
                    {
                        "$or": [
                            {"_binds.dp": self.employee.department.id},
                            {"observers.employees.id": self.employee.id},
                            {"dispatcher._id": self.employee.id},
                        ]
                    }
                )
        else:
            query_binds.update(
                {
                    "$or": [
                        {"observers.departments": [], "observers.employees": []},
                        {"observers.employees.id": self.employee.id},
                        {"dispatcher._id": self.employee.id},
                    ]
                }
            )
        return query_binds
