"""
Модуль с сервисами для работы с заявками для сотрудников
"""

from datetime import datetime, timedelta
from typing import Any

from beanie import PydanticObjectId
from beanie.odm.queries.find import FindMany
from client.s300.api import S300API
from client.s300.models.area import AreaS300
from client.s300.models.employee import EmployeeS300
from client.s300.models.house import HouseS300
from client.s300.models.tenant import TenantS300
from fastapi import HTTPException
from file_manager import File
from models.request.archived_request import ArchivedRequestModel, ArchiverType
from models.request.categories_tree import RequestCategory
from models.request.constants import RequestSource, RequestStatus, RequestType
from models.request.embs.area import AreaRS
from models.request.embs.employee import DispatcherRS, ProviderRS
from models.request.embs.execution import ExecutionRS
from models.request.embs.house import HouseRS
from models.request.embs.relations import RelationsRS, RequestRelationsRS
from models.request.request import RequestModel
from models.request_template.constants import RequestTemplateType
from models.request_template.request_template import RequestTemplate
from schemes.request.dispatcher_request import RequestDCScheme
from schemes.request.request_stats import RequestStats
from schemes.request.request_tenant_stats import TenantRequestStats
from schemes.request_employee_schedule import (
    RequestEmployeeDailySchedule,
    RequestEmployeeWeeklySchedule,
)
from services.request.request_service import RequestService
from starlette import status
from utils.rollbacker import Rollbacker


class DispatcherRequestService(RequestService, Rollbacker):
    """
    Сервис для работы с заявками для сотрудников

    Args:
        RequestService (_type_): Сервис работы с заявками не привязанный к пользователю
        Rollbacker (_type_): Миксин для возможности отмены выполненной работы с заявкой при возникновении ошибок
    """

    def __init__(self, employee: EmployeeS300):
        """
        Инициализация сервиса

        Args:
            employee (EmployeeS300): Модель работника осуществляющего работу с позициями каталога
        """

        super().__init__()
        self.employee = employee

    async def get_request_stats(
        self,
    ) -> RequestStats:
        """
        Получение статистики по заявкам

        Returns:
            RequestStats: Результат
        """
        current_time = datetime.now()
        pipeline = [
            {
                "$match": await self._get_employee_query_binds(),
            },
            {
                "$group": {
                    "_id": None,
                    "accepted": {"$sum": {"$cond": [{"$eq": ["$status", RequestStatus.ACCEPTED]}, 1, 0]}},
                    "run": {"$sum": {"$cond": [{"$eq": ["$status", RequestStatus.RUN]}, 1, 0]}},
                    "overdue": {"$sum": {"$cond": [{"$and": [{"$eq": ["$status", RequestStatus.RUN]}, {"$lt": ["$execution.end_at", current_time]}]}, 1, 0]}},
                    "emergency": {"$sum": {"$cond": [{"$eq": ["$category", RequestCategory.EMERGENCY]}, 1, 0]}},
                }
            },
        ]
        result = await RequestModel.aggregate(pipeline).to_list()
        stats = result[0] if result else {}
        return RequestStats(
            accepted=stats.get("accepted", 0),
            run=stats.get("run", 0),
            overdue=stats.get("overdue", 0),
            emergency=stats.get("emergency", 0),
        )

    async def get_tenant_stats(
        self,
        tenant_id: PydanticObjectId,
    ) -> TenantRequestStats:
        """
        Getting statistics on requests

        Returns:
            RequestStats: Result
        """
        tenant = await TenantS300.get(tenant_id)
        if not tenant:
            raise HTTPException(
                detail="Tenant not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        pipeline = [
            {
                "$match": {
                    "house._id": tenant.house.id,
                    **await self._get_employee_query_binds(),
                },
            },
            {
                "$group": {
                    "_id": "$house._id",
                    "tenant": {
                        "$sum": {"$cond": [{"$eq": ["$requester._id", tenant.id]}, 1, 0]},
                    },
                    "area": {
                        "$sum": {"$cond": [{"$and": ["$area", {"$eq": ["$area._id", tenant.area.id]}]}, 1, 0]},
                    },
                    "house": {"$sum": 1},
                    "type_area": {
                        "$sum": {"$cond": [{"$eq": ["$_type", RequestType.AREA]}, 1, 0]},
                    },
                }
            },
        ]
        result = await RequestModel.aggregate(pipeline).to_list()
        request_stats = result[0] if result else {}
        tenant_stats = TenantRequestStats(
            tenant=request_stats.get("tenant", 0),
            area=request_stats.get("area", 0),
            house=request_stats.get("house", 0),
            type_area=request_stats.get("type_area", 0),
        )
        return tenant_stats

    async def get_requests(
        self,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> FindMany[RequestModel]:
        """
        Получение заявок

        Args:
            query_list (list[dict[str, Any]]): Список словарей для составления запроса
            offset (int | None, optional): Количество пропускаемых документов. Defaults to None
            limit (int | None, optional): Количество документов. Defaults to None
            sort (list[str] | None, optional): Список полей для сортировки. Defaults to None

        Returns:
            FindMany[RequestModel]: Список заявок
        """
        query_list.append(await self._get_employee_query_binds())
        requests = RequestModel.find(*query_list)
        requests.sort(*sort if sort else ["-_id"])
        if offset:
            requests.skip(offset)
        if limit:
            requests.limit(limit)
        return requests

    async def get_request(
        self,
        request_id: PydanticObjectId,
    ) -> RequestModel:
        """
        Получение заявки

        Args:
            request_id (PydanticObjectId): Идентификатор заявки

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Заявка
        """
        query = {"_id": request_id}
        query.update(await self._get_employee_query_binds())
        request = await RequestModel.find_one(query)
        if not request:
            raise HTTPException(
                detail="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return request

    async def create_request(
        self,
        scheme: RequestDCScheme,
    ) -> RequestModel:
        """
        Создание заявки

        Args:
            scheme (RequestDCScheme): Схема для создания заявки

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Созданная заявка
        """
        try:
            house = await HouseS300.get(scheme.house.id)
            if not house:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="House not found",
                )
            if scheme.actions:
                scheme.actions = list({a.id: a for a in scheme.actions}.values())
            await self._check_categories_tree(
                house=house,
                category=scheme.category,
                subcategory=scheme.subcategory,
                work_area=scheme.work_area,
                actions=scheme.actions,
            )
            area = None
            if scheme.type == RequestType.AREA:
                if not scheme.area:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Request with the type 'area' must have an area field",
                    )
                area = await AreaS300.get(scheme.area.id)
                if not area:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Area not found",
                    )
            provider_rs = ProviderRS.model_validate(self.employee.provider.model_dump(by_alias=True))
            binds = await self._get_binds(
                house=house,
                provider_id=provider_rs.id,
                execution_provider_id=provider_rs.id,
                area_id=area.id if area else None,
            )

            requester = await self._get_requester(
                scheme.requester.id,
                scheme.requester.type,
            )
            if scheme.execution.desired_start_at and scheme.execution.desired_end_at and scheme.execution.desired_start_at > scheme.execution.desired_end_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ExecutionRS desired_start_at can't be after desired_end_at",
                )
            execution = ExecutionRS(
                desired_start_at=scheme.execution.desired_start_at,
                desired_end_at=scheme.execution.desired_end_at,
                provider=provider_rs,
            )
            dispatcher = DispatcherRS.model_validate(self.employee.model_dump(by_alias=True))
            house_rs = HouseRS.model_validate(house.model_dump(by_alias=True))
            if scheme.relations.template_id:
                template = await RequestTemplate.find_one(
                    {
                        "_id": scheme.relations.template_id,
                        "_type": RequestTemplateType.REQUEST,
                        "provider_id": self.employee.provider.id,
                    }
                )
                if not template:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Request template not found",
                    )
            area_rs = AreaRS.model_validate(area.model_dump(by_alias=True)) if area else None
            relations_rs = RelationsRS.model_validate({**scheme.relations.model_dump(by_alias=True), "requests": []})
            number = await self._generate_number()
            request = RequestModel(
                _type=scheme.type,
                area=area_rs,
                house=house_rs,
                number=number,
                requester=requester,
                description=scheme.description,
                category=scheme.category,
                subcategory=scheme.subcategory,
                work_area=scheme.work_area,
                actions=scheme.actions,
                provider=provider_rs,
                execution=execution,
                relations=relations_rs,
                administrative_supervision=scheme.administrative_supervision,
                housing_supervision=scheme.housing_supervision,
                is_public=scheme.is_public,
                tag=scheme.tag,
                _binds=binds,
                dispatcher=dispatcher,
                source=RequestSource.DISPATCHER,
            )
            if scheme.relations.requests:
                related_request = await self.get_request(scheme.relations.requests[0].id)
                if not related_request:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Related request not found",
                    )
                request.relations.requests.append(RequestRelationsRS.model_validate(related_request.model_dump(by_alias=True)))
                await related_request.update(
                    {
                        "$push": {
                            "relations.requests": {
                                "_id": request.id,
                                "status": request.status,
                                "number": request.number,
                            }
                        }
                    }
                )
                self.add_rollback(related_request.update, {"$pull": {"relations.requests": {"_id": request.id}}})
            await request.save()
        except:
            await self.rollback()
            raise
        return request

    async def delete_request(
        self,
        request_id: PydanticObjectId,
    ):
        """
        Архивирование заявки

        Args:
            request_id (PydanticObjectId): Идентификатор заявки
        """
        request = await self.get_request(request_id)
        await ArchivedRequestModel(
            archiver_type=ArchiverType.EMPLOYEE,
            archiver_id=self.employee.id,
            **request.model_dump(by_alias=True),
        ).save()
        await request.delete()

    async def restore_request(
        self,
        request_id: PydanticObjectId,
    ) -> RequestModel:
        """
        Восстановление заявки суперпользователем

        Args:
            request_id (PydanticObjectId): Идентификатор заявки

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Восстановленная заявка
        """
        if not self.employee.is_super or not self.employee.external_control:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the superuser can restore the application",
            )
        archived_request = await ArchivedRequestModel.get(request_id)
        if not archived_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archived request not found",
            )
        request = await RequestModel(
            **archived_request.model_dump(by_alias=True),
        ).save()
        await archived_request.delete()
        return request

    async def get_request_employee_weekly_schedules(
        self,
        start_at: datetime,
        employee_ids: set[PydanticObjectId],
    ) -> list[RequestEmployeeWeeklySchedule]:
        """
        Получение недельного графика сотрудников

        Args:
            start_at (datetime): Дата от которой нужен график
            employee_ids (set[PydanticObjectId]): Список идентификаторов сотрудников

        Returns:
            list[RequestEmployeeWeeklySchedule]: Список недельных графиков работы сотрудников
        """
        employee_ids = await S300API.get_allowed_worker_ids(
            employee=self.employee,
            worker_ids=employee_ids,
        )
        if not employee_ids:
            return []
        start_at = start_at.replace(hour=0, minute=0, second=0, microsecond=0)
        query = {
            **await self._get_employee_query_binds(),
            "execution.start_at": {"$lt": start_at + timedelta(days=7)},
            "execution.end_at": {"$gte": start_at},
            "execution.employees._id": {"$in": employee_ids},
        }
        requests = RequestModel.find(query)
        result = {}
        async for request in requests:
            if not request.execution.end_at or not request.execution.start_at:
                continue

            # Определяем начальный и конечный дни
            effective_start = max(request.execution.start_at, start_at)
            effective_end = min(request.execution.end_at, start_at + timedelta(days=7))

            # Пробегаем по дням в диапазоне
            current_day = effective_start
            while current_day <= effective_end:
                day_index = (current_day - start_at).days
                for employee in request.execution.employees:
                    if employee.id not in employee_ids:
                        continue
                    employee_id = str(employee.id)

                    if employee_id not in result:
                        result[employee_id] = [0] * 7
                    if 0 <= day_index < 7:
                        result[employee_id][day_index] += 1  # Добавляем единичку для каждого дня

                current_day += timedelta(days=1)  # Переход к следующему дню
        schedules = []
        for employee_id in employee_ids:
            str_employee_id = str(employee_id)
            if str_employee_id in result:
                schedules.append(
                    RequestEmployeeWeeklySchedule(
                        employee_id=employee_id,
                        workload=result[str_employee_id],
                    ),
                )
                continue
            schedules.append(
                RequestEmployeeWeeklySchedule(
                    employee_id=employee_id,
                ),
            )
        return schedules

    async def get_request_employee_daily_schedules(
        self,
        start_at: datetime,
        employee_ids: set[PydanticObjectId],
    ) -> list[RequestEmployeeDailySchedule]:
        """
        Получение дневного графика сотрудников

        Args:
            start_at (datetime): Дата от которой нужен график
            employee_ids (set[PydanticObjectId]): Список идентификаторов сотрудников

        Returns:
            list[RequestEmployeeWeeklySchedule]: Список недельных графиков работы сотрудников
        """
        employee_ids = await S300API.get_allowed_worker_ids(
            employee=self.employee,
            worker_ids=employee_ids,
        )
        if not employee_ids:
            return []
        start_at = start_at.replace(hour=0, minute=0, second=0, microsecond=0)

        # Запрос для получения всех заявок в заданный диапазон
        query = {
            **await self._get_employee_query_binds(),
            "execution.start_at": {"$lt": start_at + timedelta(days=1)},
            "execution.end_at": {"$gte": start_at},
            "execution.employees._id": {"$in": employee_ids},
        }

        requests = RequestModel.find(query)
        result = {}
        async for request in requests:
            if not request.execution.start_at or not request.execution.end_at:
                continue
            execution_start = request.execution.start_at.replace(second=0, microsecond=0)
            execution_end = request.execution.end_at.replace(second=0, microsecond=0)

            # Определяем границы в рамках одного дня
            effective_start = max(execution_start, start_at)
            effective_end = min(execution_end, start_at + timedelta(days=1))

            # Заполняем результат по временным интервалам
            start_index = int((effective_start - start_at).total_seconds() // 900)
            end_index = int((effective_end - start_at).total_seconds() // 900)
            for employee in request.execution.employees:
                if employee.id not in employee_ids:
                    continue
                employee_id = str(employee.id)
                if employee_id not in result:
                    result[employee_id] = [[] for _ in range(96)]
                for i in range(start_index, end_index):
                    if 0 <= i < 96:
                        # Добавляем номер заявки в соответствующий временной интервал
                        result[employee_id][i].append(request.number)
        schedules = []
        for employee_id in employee_ids:
            str_employee_id = str(employee_id)
            if str_employee_id in result:
                schedules.append(
                    RequestEmployeeDailySchedule(
                        employee_id=employee_id,
                        workload=result[str_employee_id],
                    ),
                )
                continue
            schedules.append(
                RequestEmployeeDailySchedule(
                    employee_id=employee_id,
                ),
            )
        return schedules

    async def download_requester_attachment_file(
        self,
        request_id: PydanticObjectId,
        file_id: PydanticObjectId,
    ) -> File:
        """
        Скачивание файла вложения заявителя

        Args:
            request_id (PydanticObjectId): Идентификатор заявки
            file_id (PydanticObjectId): Идентификатор файла

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            File: Файл вложения заявителя
        """
        request = await self.get_request(request_id)
        for f in request.requester_attachment.files:
            if f.id == file_id:
                return f
        f = await File.get(file_id)
        if not f or f.tag != await self.get_filetag_for_requester_attachment(request.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
        return f

    async def download_execution_attachment_file(
        self,
        request_id: PydanticObjectId,
        file_id: PydanticObjectId,
    ) -> File:
        """
        Скачивание файла вложения сотрудников

        Args:
            request_id (PydanticObjectId): Идентификатор заявки
            file_id (PydanticObjectId): Идентификатор файла

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            File: Файл вложения сотрудников
        """
        request = await self.get_request(request_id)
        for f in request.execution.attachment.files:
            if f.id == file_id:
                return f
        f = await File.get(file_id)
        if not f or f.tag != await self.get_filetag_for_execution_attachment(request.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
        return f

    async def download_execution_act_file(
        self,
        request_id: PydanticObjectId,
        file_id: PydanticObjectId,
    ) -> File:
        """
        Скачивание файла акта выполненных работ
        Args:
            request_id (PydanticObjectId): Идентификатор заявки
            file_id (PydanticObjectId): Идентификатор файла

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            File: Файл акта выполненных работ
        """
        request = await self.get_request(request_id)
        for f in request.execution.act.files:
            if f.id == file_id:
                return f
        f = await File.get(file_id)
        if not f or f.tag != await self.get_filetag_for_execution_act(request.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
        return f

    async def _get_employee_query_binds(self) -> dict[str, PydanticObjectId]:
        query_binds: dict = {
            "_binds.pr": self.employee.binds_permissions.pr,
            "_binds.hg": self.employee.binds_permissions.hg,
        }
        return query_binds
