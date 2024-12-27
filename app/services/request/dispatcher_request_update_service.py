"""
Модуль для обновления заявки сотрудником
"""

from datetime import datetime, timedelta

from beanie import PydanticObjectId
from fastapi import HTTPException, UploadFile
from file_manager import File
from starlette import status

from client.s300.api import S300API
from client.s300.models.employee import EmployeeS300
from client.s300.models.house import HouseS300
from client.s300.models.provider import ProviderS300
from models.extra.attachment import Attachment
from models.request.categories_tree import (
    REQUEST_CATEGORY_EN_RU,
    REQUEST_SUBCATEGORY_EN_RU,
    REQUEST_WORK_AREA_EN_RU,
    RequestCategory,
    RequestSubcategory,
    RequestWorkArea,
)
from models.request.constants import (
    REQUEST_STATUS_EN_RU,
    REQUEST_TAG_EN_RU,
    RequestStatus,
    RequestTag,
)
from models.request.embs.action import (
    ACTION_TYPE_EN_RU,
    ActionRS,
    ActionRSType,
    LiftShutdownActionRS,
    StandpipeShutdownActionRS,
)
from models.request.embs.employee import EmployeeRS, ProviderRS
from models.request.embs.relations import RequestRelationsRS
from models.request.request import RequestModel
from models.request_history.request_history import (
    RequestHistory,
    Update,
    UpdatedField,
    UpdateUser,
    UpdateUserType,
)
from models.request_template.constants import RequestTemplateType
from models.request_template.request_template import RequestTemplate
from schemes.extra.only_id import OnlyIdScheme
from schemes.request.dispatcher_request import (
    RelationsRequestDCUScheme,
    RequestDUScheme,
)
from schemes.request.request_status import (
    RequestDStatusUScheme,
    ResourcesRequestDStatusUScheme,
)
from services.request.request_service import RequestService
from utils.rollbacker import Rollbacker


class DispatcherRequestUpdateService(RequestService, Rollbacker):
    """
    Сервис для обновления заявки сотрудником

    Args:
        RequestService (_type_): Сервис работы с заявками не привязанный к пользователю
        Rollbacker (_type_): Миксин для возможности отмены выполненной работы с заявкой при возникновении ошибок
    """

    def __init__(
        self,
        employee: EmployeeS300,
        request: RequestModel,
    ):
        """
        Инициализация сервиса

        Args:
            employee (EmployeeS300): Модель работника осуществляющего работу с позициями каталога
            request (RequestModel): Модель заявки для обновления
        """
        super().__init__()
        if request.execution.provider.id != employee.provider.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permissions",
            )
        self.employee = employee
        self.request = request
        self.updated_fields: list[UpdatedField] = []

    async def update_request(
        self,
        scheme: RequestDUScheme,
    ) -> RequestModel:
        """
        Обновление не относящихся ко статусу и ресурсам полей заявки

        Args:
            scheme (RequestDUScheme): Схема для обновления заявки

        Returns:
            RequestModel: Обновленная заявка
        """
        try:
            await self._update_description(scheme.description)
            await self._update_desired_execution_times(
                execution_desired_start_at=scheme.execution.desired_start_at,
                execution_desired_end_at=scheme.execution.desired_end_at,
            )
            await self._update_category_subcategory_work_area(
                category=scheme.category,
                subcategory=scheme.subcategory,
                work_area=scheme.work_area,
                actions=scheme.actions,
            )
            await self._update_tag(scheme.tag)
            await self._update_is_public(scheme.is_public)
            await self._update_add_params(
                administrative_supervision=scheme.administrative_supervision,
                housing_supervision=scheme.housing_supervision,
            )
            await self._update_relations(scheme.relations)

            await self._update_execution_act(scheme.execution.act)
            await self._update_execution_attachment(scheme.execution.attachment)
            await self._update_requester_attachment(scheme.requester_attachment)

            await self.request.save()
        except:
            await self.rollback()
            raise
        await self._update_request_history()
        return self.request

    async def update_request_status(
        self,
        scheme: RequestDStatusUScheme,
    ) -> RequestModel:
        """
        Обновление полей связанных со статусом и ресурсами полей

        Args:
            scheme (RequestDStatusUScheme): Схема для обновления заявки

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Обновленная модель заявки
        """
        try:
            if scheme.status == RequestStatus.ACCEPTED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to change status to accepted",
                )
            if scheme.execution.provider.id != self.request.execution.provider.id:
                await self._update_execution_provider(scheme.execution.provider.id)
                await self._update_execution_employees([])
                await self._update_request_history()
                await self.request.save()
                return self.request
            if scheme.status == RequestStatus.RUN:
                if not scheme.execution.start_at or not scheme.execution.end_at or not scheme.execution.employees:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="With 'run' status, you must include start and end times and at least 1 employee",
                    )
                await self._update_execution_times(
                    execution_start_at=scheme.execution.start_at,
                    execution_end_at=scheme.execution.end_at,
                )
                await self._update_execution_employees(scheme.execution.employees)
                await self._update_resources(scheme.resources)
            elif scheme.status == RequestStatus.DELAYED:
                if not scheme.execution.delayed_until or not scheme.execution.description:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="With 'delayed' status, you must include delayed_until time and reason",
                    )
                await self._update_execution_delayed_until(scheme.execution.delayed_until)
                await self._update_execution_description(scheme.execution.description)
                await self._update_resources(scheme.resources)
            elif scheme.status == RequestStatus.PERFORMED:
                if not scheme.execution.start_at or not scheme.execution.end_at or not scheme.execution.employees or not scheme.execution.description:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="With 'performed' status, you must include start and end times, at least 1 employee and work description",
                    )
                await self._update_execution_times(
                    execution_start_at=scheme.execution.start_at,
                    execution_end_at=scheme.execution.end_at,
                )
                await self._update_execution_employees(scheme.execution.employees)
                await self._update_execution_description(scheme.execution.description)
                await self._update_execution_is_partially(scheme.execution.is_partially)
                await self._update_warranty_until(scheme.execution.warranty_until)
                await self._update_resources(scheme.resources)
            else:
                if not scheme.execution.description:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="With 'abandonment' or 'refusal' status, you must include reason",
                    )
                await self._update_execution_description(scheme.execution.description)
            if self.request.status != scheme.status:
                self.request.status_updated_at = datetime.now()
                self.request.status = scheme.status
                self.updated_fields.append(
                    UpdatedField(
                        name="status",
                        value=scheme.status,
                        name_display="Статус",
                        value_display=REQUEST_STATUS_EN_RU[scheme.status],
                    )
                )

            await self.request.save()
        except:
            await self.rollback()
            raise
        await self._update_request_history(tag="status")
        return self.request

    async def upload_requester_attachment_files(
        self,
        files: list[UploadFile],
    ) -> list[File]:
        """
        Загрузка файлов вложения заявителя

        Args:
            files (list[UploadFile]): Файлы

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Обновленная заявка
        """
        if not files or [file for file in files if file.size == 0]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A file is required, and it cannot be empty (0 bytes)",
            )
        new_files = []
        try:
            for file in files:
                f = await File.create(
                    file_content=await file.read(),
                    filename=file.filename,
                    tag=await self.get_filetag_for_requester_attachment(self.request.id),
                )
                self.add_rollback(f.delete)
                self.updated_fields.append(
                    UpdatedField(
                        name="requester_attachment.files",
                        value=f,
                        name_display="Новый файл от жильца",
                        value_display=f.name,
                        link=f"/dispatcher/requests/{str(self.request.id)}/requester_attachment_files/{str(f.id)}",
                    )
                )
                new_files.append(f)
            self.request.requester_attachment.files.extend(new_files)
            await self.request.save()
        except:
            await self.rollback()
            raise
        await self._update_request_history()
        return self.request.requester_attachment.files

    async def upload_execution_attachment_files(
        self,
        files: list[UploadFile],
    ) -> list[File]:
        """
        Загрузка файлов вложения сотрудников

        Args:
            files (list[UploadFile]): Файлы

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Обновленная заявка
        """
        if not files or [file for file in files if file.size == 0]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A file is required, and it cannot be empty (0 bytes)",
            )
        new_files = []
        try:
            for file in files:
                f = await File.create(
                    file_content=await file.read(),
                    filename=file.filename,
                    tag=await self.get_filetag_for_execution_attachment(self.request.id),
                )
                self.add_rollback(f.delete)
                self.updated_fields.append(
                    UpdatedField(
                        name="execution.attachment.files",
                        value=f,
                        name_display="Новый файл выполненных работ",
                        value_display=f.name,
                        link=f"/dispatcher/requests/{str(self.request.id)}/execution_attachment_files/{str(f.id)}",
                    )
                )
                new_files.append(f)
            self.request.execution.attachment.files.extend(new_files)
            await self.request.save()
        except:
            await self.rollback()
            raise
        await self._update_request_history()
        return self.request.execution.attachment.files

    async def upload_execution_act_files(
        self,
        files: list[UploadFile],
    ) -> list[File]:
        """
        Загрузка файлов вложения сотрудников

        Args:
            files (list[UploadFile]): Файлы

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Обновленная заявка
        """
        if not files or [file for file in files if file.size == 0]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A file is required, and it cannot be empty (0 bytes)",
            )
        new_files = []
        try:
            for file in files:
                f = await File.create(
                    file_content=await file.read(),
                    filename=file.filename,
                    tag=await self.get_filetag_for_execution_act(self.request.id),
                )
                self.add_rollback(f.delete)
                self.updated_fields.append(
                    UpdatedField(
                        name="execution.act.files",
                        value=f,
                        name_display="Новый файл акта выполненных работ",
                        value_display=f.name,
                        link=f"/dispatcher/requests/{str(self.request.id)}/execution_act_files/{str(f.id)}",
                    )
                )
                new_files.append(f)

            self.request.execution.act.files.extend(new_files)
            await self.request.save()
        except:
            await self.rollback()
            raise
        await self._update_request_history()
        return self.request.execution.act.files

    async def _update_request_history(self, tag: str | None = None) -> None:
        if not self.updated_fields:
            return
        current_time = datetime.now()

        request_history = await RequestHistory.find_one({"request_id": self.request.id})
        if not request_history:
            if not tag and current_time - self.request.created_at < timedelta(minutes=5) and self.request.dispatcher and self.request.dispatcher.id == self.employee.id:
                return
            request_history = RequestHistory(request_id=self.request.id)
        user = UpdateUser(
            _id=self.employee.external_control.id if self.employee.external_control else self.employee.id,
            full_name=self.employee.external_control.full_name if self.employee.external_control else self.employee.full_name,
            _type=UpdateUserType.EMPLOYEE,
        )
        update = Update(
            user=user,
            updated_fields=self.updated_fields,
            tag=tag,
        )
        if request_history.updates:
            last_update = sorted(request_history.updates, key=lambda x: x.updated_at)[-1]
            if current_time - last_update.updated_at < timedelta(minutes=5) and last_update.user.id == self.employee.id and last_update.tag == tag:
                update.updated_fields.extend(last_update.updated_fields)
                request_history.updates.remove(last_update)
        update.updated_fields.sort(key=lambda x: x.name)
        request_history.updates.append(update)
        request_history.updates.sort(
            key=lambda x: x.updated_at,
            reverse=True,
        )
        await request_history.save()

    async def _update_description(
        self,
        description: str,
    ):
        if self.request.description == description:
            return
        self.request.description = description
        self.updated_fields.append(
            UpdatedField(
                name="description",
                value=description,
                name_display="Описание",
                value_display=description,
            )
        )

    async def _update_tag(
        self,
        tag: RequestTag,
    ):
        if self.request.tag == tag:
            return
        self.request.tag = tag
        self.updated_fields.append(
            UpdatedField(
                name="tag",
                value=tag,
                name_display="Тег",
                value_display=REQUEST_TAG_EN_RU[tag],
            )
        )

    async def _update_relations(
        self,
        relations: RelationsRequestDCUScheme,
    ):
        if self.request.relations.template_id != relations.template_id:
            if relations.template_id:
                template = await RequestTemplate.find_one(
                    {
                        "_id": relations.template_id,
                        "_type": RequestTemplateType.REQUEST,
                        "provider_id": self.employee.provider.id,
                    }
                )
                if not template:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Request template not found",
                    )
                self.updated_fields.append(
                    UpdatedField(
                        name="template_id",
                        value=relations.template_id,
                        name_display="Шаблон заявки",
                        value_display=template.name,
                    )
                )
            else:
                self.updated_fields.append(
                    UpdatedField(
                        name="template_id",
                        value=relations.template_id,
                        name_display="Шаблон заявки",
                        value_display="Не выбран",
                    )
                )
            self.request.relations.template_id = relations.template_id
        new = {r.id for r in relations.requests if r.id != self.request.id}
        old = {r.id for r in self.request.relations.requests}
        if new == old:
            return
        add_request_ids = new - old
        delete_request_ids = old - new
        if delete_request_ids:
            new_request_list = []
            for r in self.request.relations.requests:
                if r.id in delete_request_ids:
                    self.updated_fields.append(
                        UpdatedField(
                            name="relations.requests",
                            value=None,
                            name_display="Удалена связанная заявка",
                            value_display=r.number,
                        )
                    )
                    continue
                await RequestModel.find({"_id": {"$in": delete_request_ids}}).update_many({"$pull": {"relations.requests": {"_id": self.request.id}}})
                self.add_rollback(
                    RequestModel.find({"_id": {"$in": delete_request_ids}}).update_many,
                    {"$push": {"relations.requests": {"_id": self.request.id, "number": self.request.number, "status": self.request.status}}},
                )
                new_request_list.append(r)
            self.request.relations.requests = new_request_list
        if add_request_ids:
            query = {
                "_id": {"$in": add_request_ids},
                "_binds.pr": self.employee.binds_permissions.pr,
                "_binds.hg": self.employee.binds_permissions.hg,
            }
            requests = await RequestModel.find(query).to_list()
            not_found_request_ids = add_request_ids - {r.id for r in requests}
            if not_found_request_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Some requests were not found: {not_found_request_ids}",
                )
            for r in requests:
                related_request = RequestRelationsRS.model_validate(r.model_dump(by_alias=True))
                self.updated_fields.append(
                    UpdatedField(
                        name="relations.requests",
                        value=related_request,
                        name_display="Добавлена связанная заявка",
                        value_display=related_request.number,
                    )
                )
                self.request.relations.requests.append(related_request)
            await RequestModel.find({"_id": {"$in": add_request_ids}}).update_many(
                {
                    "$push": {
                        "relations.requests": {
                            "_id": self.request.id,
                            "status": self.request.status,
                            "number": self.request.number,
                        }
                    }
                }
            )
            self.add_rollback(
                RequestModel.find({"_id": {"$in": add_request_ids}}).update_many,
                {
                    "$pull": {
                        "relations.requests": {
                            "_id": self.request.id,
                        }
                    }
                },
            )

    async def _update_add_params(
        self,
        administrative_supervision: bool,
        housing_supervision: bool,
    ):
        if self.request.administrative_supervision != administrative_supervision:
            self.request.administrative_supervision = administrative_supervision
            self.updated_fields.append(
                UpdatedField(
                    name="administrative_supervision",
                    value=administrative_supervision,
                    name_display="Отслеживание администрацией района",
                    value_display="Да" if administrative_supervision else "Нет",
                )
            )
        if self.request.housing_supervision != housing_supervision:
            self.request.housing_supervision = housing_supervision
            self.updated_fields.append(
                UpdatedField(
                    name="housing_supervision",
                    value=housing_supervision,
                    name_display="Отслеживание аварийной службой",
                    value_display="Да" if housing_supervision else "Нет",
                )
            )

    async def _update_is_public(
        self,
        is_public: bool,
    ):
        if self.request.is_public == is_public:
            return
        self.request.is_public = is_public
        self.updated_fields.append(
            UpdatedField(
                name="is_public",
                value=is_public,
                name_display="Видимость",
                value_display="Для всех в доме" if is_public else "Только для заявителя",
            )
        )

    async def _update_category_subcategory_work_area(
        self,
        category: RequestCategory,
        subcategory: RequestSubcategory | None,
        work_area: RequestWorkArea | None,
        actions: list[ActionRS | LiftShutdownActionRS | StandpipeShutdownActionRS],
    ):
        if category == self.request.category and work_area == self.request.work_area and subcategory == self.request.subcategory and not self.request.actions and not actions:
            return
        house = await HouseS300.get(self.request.house.id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дом не найден",
            )
        await self._check_categories_tree(
            house=house,
            category=category,
            subcategory=subcategory,
            work_area=work_area,
            actions=actions,
        )
        if category != self.request.category:
            self.request.category = category
            self.updated_fields.append(
                UpdatedField(
                    name="category",
                    value=category,
                    name_display="Категория",
                    value_display=REQUEST_CATEGORY_EN_RU[category],
                )
            )
        if subcategory != self.request.subcategory:
            self.request.subcategory = subcategory
            self.updated_fields.append(
                UpdatedField(
                    name="subcategory",
                    value=subcategory,
                    name_display="Подкатегория",
                    value_display=REQUEST_SUBCATEGORY_EN_RU[subcategory] if subcategory else "Нет",
                )
            )
        if work_area != self.request.work_area:
            self.request.work_area = work_area
            self.updated_fields.append(
                UpdatedField(
                    name="work_area",
                    value=work_area,
                    name_display="Область работ",
                    value_display=REQUEST_WORK_AREA_EN_RU[work_area] if work_area else "Нет",
                )
            )
        if self.request.actions or actions:
            actions = list({a.id: a for a in actions}.values())
            existing_actions = {a.id: a for a in self.request.actions}
            for action in actions:
                if action.id not in existing_actions:
                    start_at = f" c {action.start_at.strftime('%H:%M %d.%m.%Y')}" if action.start_at else ""
                    end_at = f" до {action.end_at.strftime('%H:%M %d.%m.%Y')}" if action.end_at else ""
                    self.updated_fields.append(
                        UpdatedField(
                            name="actions",
                            value=action,
                            name_display="Новое действие",
                            value_display=f"{ACTION_TYPE_EN_RU[action.type]}{start_at}{end_at}",
                        )
                    )
                    continue
                a = existing_actions.pop(action.id)
                if action.end_at != a.end_at:
                    self.updated_fields.append(
                        UpdatedField(
                            name="actions.end_at",
                            value=action.end_at,
                            name_display=f"Время окончания {ACTION_TYPE_EN_RU[action.type]}",
                            value_display=action.end_at.strftime("%H:%M %d.%m.%Y") if action.end_at else "Нет",
                        )
                    )
                if action.start_at != a.start_at:
                    self.updated_fields.append(
                        UpdatedField(
                            name="actions.start_at",
                            value=action.start_at,
                            name_display=f"Время начала {ACTION_TYPE_EN_RU[action.type]}",
                            value_display=action.start_at.strftime("%H:%M %d.%m.%Y") if action.start_at else "Нет",
                        )
                    )
                if action.type == ActionRSType.LIFT and getattr(getattr(action, "lift", None), "id", None) != getattr(getattr(a, "lift", None), "id", None):
                    self.updated_fields.append(
                        UpdatedField(
                            name="actions.lift",
                            value=action.start_at,
                            name_display="Отключаемый лифт",
                            value_display=str(action.lift.id) if action.lift else "Не выбран",
                        )
                    )
                if (action.type == ActionRSType.CENTRAL_HEATING or action.type == ActionRSType.CWS or action.type == ActionRSType.HWS) and getattr(getattr(action, "standpipe", None), "id", None) != getattr(getattr(a, "standpipe", None), "id", None):  # type: ignore
                    self.updated_fields.append(
                        UpdatedField(
                            name="actions.lift",
                            value=action.start_at,
                            name_display=f"Отключаемый стояк {ACTION_TYPE_EN_RU[action.type]}",
                            value_display=str(action.standpipe.id) if action.standpipe else "Не выбран",
                        )
                    )
            for action in existing_actions.values():
                start_at = f" c {action.start_at.strftime('%H:%M %d.%m.%Y')}" if action.start_at else ""
                end_at = f" до {action.end_at.strftime('%H:%M %d.%m.%Y')}" if action.end_at else ""
                self.updated_fields.append(
                    UpdatedField(
                        name="actions",
                        value=None,
                        name_display="Удалено действие",
                        value_display=f"{ACTION_TYPE_EN_RU[action.type]}{start_at}{end_at}",
                    )
                )
            self.request.actions = actions

    async def _update_desired_execution_times(
        self,
        execution_desired_start_at: datetime | None,
        execution_desired_end_at: datetime | None,
    ):
        if execution_desired_start_at and execution_desired_end_at and execution_desired_start_at > execution_desired_end_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ExecutionRS desired_start_at can't be after desired_end_at",
            )
        if self.request.execution.desired_start_at != execution_desired_start_at:
            self.request.execution.desired_start_at = execution_desired_start_at
            self.updated_fields.append(
                UpdatedField(
                    name="execution.desired_start_at",
                    value=execution_desired_start_at,
                    name_display="Желаемое время начала работ",
                    value_display=execution_desired_start_at.strftime("%H:%M %d.%m.%Y") if execution_desired_start_at else "Нет",
                )
            )
        if self.request.execution.desired_end_at != execution_desired_end_at:
            self.request.execution.desired_end_at = execution_desired_end_at
            self.updated_fields.append(
                UpdatedField(
                    name="execution.desired_end_at",
                    value=execution_desired_end_at,
                    name_display="Желаемое время окончания работ",
                    value_display=execution_desired_end_at.strftime("%H:%M %d.%m.%Y") if execution_desired_end_at else "Нет",
                )
            )

    async def _update_warranty_until(
        self,
        execution_warranty_until: datetime | None,
    ):
        if self.request.execution.warranty_until == execution_warranty_until:
            return
        self.request.execution.warranty_until = execution_warranty_until
        self.updated_fields.append(
            UpdatedField(
                name="execution.warranty_until",
                value=execution_warranty_until,
                name_display="Гарантия на выполненные работы",
                value_display=f"По {execution_warranty_until.strftime('%H:%M %d.%m.%Y')}" if execution_warranty_until else "Нет",
            )
        )

    async def _update_resources(
        self,
        resources: ResourcesRequestDStatusUScheme,
    ):
        if self.request.resources.materials or resources.materials:
            resources.materials = list({m.name: m for m in resources.materials}.values())
            existing_materials = {m.name: m for m in self.request.resources.materials}
            for material in resources.materials:
                if material.name not in existing_materials:
                    self.updated_fields.append(
                        UpdatedField(
                            name="resources.materials",
                            value=material,
                            name_display="Новый вручную добавленный материал",
                            value_display=f"{material.name}, кол-во - {material.quantity}, {round(material.price/100, 2)} р. за ед.",
                        )
                    )
                    continue
                m = existing_materials.pop(material.name)
                if material.quantity != m.quantity:
                    self.updated_fields.append(
                        UpdatedField(
                            name="resources.materials.quantity",
                            value=material.quantity,
                            name_display=f"Кол-во вручную добавленного материала {material.name}",
                            value_display=str(material.quantity),
                        )
                    )
                if material.price != m.price:
                    self.updated_fields.append(
                        UpdatedField(
                            name="resources.materials.price",
                            value=material.price,
                            name_display=f"Стоимость за ед. вручную добавленный материала {material.name}",
                            value_display=str(material.price),
                        )
                    )
            for name, m in existing_materials.items():
                self.updated_fields.append(
                    UpdatedField(
                        name="resources.materials",
                        value=None,
                        name_display="Удален вручную добавленная материал",
                        value_display=f"{name}, кол-во - {m.quantity}, {round(m.price/100, 2)} р. за ед.",
                    )
                )
            self.request.resources.materials = resources.materials
        if self.request.resources.services or resources.services:
            resources.services = list({s.name: s for s in resources.services}.values())
            existing_services = {s.name: s for s in self.request.resources.services}
            for service in resources.services:
                if service.name not in existing_services:
                    self.updated_fields.append(
                        UpdatedField(
                            name="resources.services",
                            value=service,
                            name_display="Новая вручную добавленная услуга",
                            value_display=f"{service.name}, кол-во - {service.quantity}, {round(service.price/100, 2)} р. за ед.",
                        )
                    )
                    continue
                s = existing_services.pop(service.name)
                if service.quantity != s.quantity:
                    self.updated_fields.append(
                        UpdatedField(
                            name="resources.services.quantity",
                            value=service.quantity,
                            name_display=f"Кол-во вручную добавленной услуги {service.name}",
                            value_display=str(service.quantity),
                        )
                    )
                if service.price != s.price:
                    self.updated_fields.append(
                        UpdatedField(
                            name="resources.services.price",
                            value=service.price,
                            name_display=f"Стоимость за ед. вручную добавленной услуги {service.name}",
                            value_display=str(service.price),
                        )
                    )
            for name, s in existing_services.items():
                self.updated_fields.append(
                    UpdatedField(
                        name="resources.services",
                        value=None,
                        name_display="Удалена вручную добавленная услуга",
                        value_display=f"{name}, кол-во - {s.quantity}, {round(s.price/100, 2)} р. за ед.",
                    )
                )
            self.request.resources.services = resources.services
        if not resources.warehouses and not self.request.resources.warehouses:
            return

        existing_warehouses = {str(w.id): {str(i.id): i.quantity for i in w.items} for w in self.request.resources.warehouses}
        new_warehouses = {str(w.id): {str(i.id): i.quantity for i in w.items} for w in resources.warehouses}
        item_names_map: dict[str, str] = {str(i.id): i.name for w in self.request.resources.warehouses for i in w.items}
        warehouse_names_map: dict[str, str] = {str(w.id): w.name for w in self.request.resources.warehouses}
        if existing_warehouses == new_warehouses:
            return
        warehouses = await S300API.upsert_storage_docs_out(
            employee=self.employee,
            request_id=self.request.id,
            warehouses=new_warehouses,
        )
        self.add_rollback(
            S300API.upsert_storage_docs_out,
            request_id=self.request.id,
            provider_id=self.employee.provider.id,
            is_rollback=True,
        )
        for warehouse_index, warehouse in enumerate(warehouses):
            w = existing_warehouses.pop(str(warehouse.id), None)
            if not w:
                for item in warehouse.items:
                    self.updated_fields.append(
                        UpdatedField(
                            name=f"resources.warehouses.{warehouse_index}.items",
                            value=item,
                            name_display=f"Новый материал со склада {warehouse.name}",
                            value_display=f"{item.name}, кол-во - {item.quantity}, {round(item.price/100, 2)} р. за ед.",
                        )
                    )
                continue
            for item in warehouse.items:
                i_quantity = w.pop(str(item.id), None)
                if not i_quantity:
                    self.updated_fields.append(
                        UpdatedField(
                            name=f"resources.warehouses.{warehouse_index}.items",
                            value=item,
                            name_display=f"Новый материал со склада {warehouse.name}",
                            value_display=f"{item.name}, кол-во - {item.quantity}, {round(item.price/100, 2)} р. за ед.",
                        )
                    )
                    continue
                if item.quantity != i_quantity:
                    self.updated_fields.append(
                        UpdatedField(
                            name=f"resources.warehouses.{warehouse_index}.items",
                            value=item.quantity,
                            name_display=f"Кол-во материал со склада {warehouse.name}",
                            value_display=str(item.quantity),
                        )
                    )
            for i_id, i_quantity in w.items():
                item_name = item_names_map.get(i_id, "Неизвестный материал")
                self.updated_fields.append(
                    UpdatedField(
                        name=f"resources.warehouses.{warehouse_index}.items",
                        value=None,
                        name_display=f"Удален материал со склада {warehouse.name}",
                        value_display=f"{item_name}, кол-во - {i_quantity}",
                    )
                )
        for w_id, items in existing_warehouses.items():
            warehouse_name = warehouse_names_map.get(w_id, "Неизвестный склад")
            for i_id, i_quantity in items.items():
                item_name = item_names_map.get(i_id, "Неизвестный материал")
                self.updated_fields.append(
                    UpdatedField(
                        name="resources.warehouses",
                        value=None,
                        name_display=f"Удален материал со склада {warehouse_name}",
                        value_display=f"{item_name}, кол-во - {i_quantity}",
                    )
                )
        self.request.resources.warehouses = warehouses

    async def _update_execution_is_partially(
        self,
        is_partially: bool,
    ):
        if self.request.execution.is_partially == is_partially:
            return
        self.request.execution.is_partially = is_partially
        self.updated_fields.append(
            UpdatedField(
                name="execution.is_partially",
                value=is_partially,
                name_display="Заявка выполнена полностью",
                value_display="Нет" if is_partially else "Да",
            )
        )

    async def _update_execution_description(
        self,
        execution_description: str,
    ):
        if self.request.execution.description and self.request.execution.description == execution_description:
            return
        self.request.execution.description = execution_description
        self.updated_fields.append(
            UpdatedField(
                name="execution.description",
                value=execution_description,
                name_display="Описание работ/причины отмены/отсрочки/отказа",
                value_display=execution_description,
            )
        )

    async def _update_execution_delayed_until(
        self,
        delayed_until: datetime,
    ):
        if self.request.execution.delayed_until and self.request.execution.delayed_until == delayed_until:
            return
        self.request.execution.delayed_until = delayed_until
        self.updated_fields.append(
            UpdatedField(
                name="execution.delayed_until",
                value=delayed_until,
                name_display="Время отсрочки работ",
                value_display=delayed_until.strftime("%H:%M %d.%m.%Y"),
            )
        )

    async def _update_execution_employees(
        self,
        execution_employees: list[OnlyIdScheme],
    ):
        new = {e.id for e in execution_employees}
        old = {e.id for e in self.request.execution.employees}
        if new == old:
            return
        add_employee_ids = new - old
        deleted_employee_ids = old - new
        if deleted_employee_ids:
            new_employee_list = []
            for e in self.request.execution.employees:
                if e.id in deleted_employee_ids:
                    self.updated_fields.append(
                        UpdatedField(
                            name="execution.employees",
                            value=None,
                            name_display="Удален сотрудник на исполнение",
                            value_display=e.full_name,
                        )
                    )
                    continue
                new_employee_list.append(e)
            self.request.execution.employees = new_employee_list
        if add_employee_ids:
            for employee_id in add_employee_ids:
                employee = await EmployeeS300.get(employee_id)
                if not employee:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Employee {str(employee_id)} not found",
                    )
                if employee.provider.id != self.request.execution.provider.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Employee must be in execution provider",
                    )
                self.updated_fields.append(
                    UpdatedField(
                        name="execution.employees",
                        value=employee,
                        name_display="Добавлен сотрудник на исполнение",
                        value_display=employee.full_name,
                    )
                )
                employee_rs = EmployeeRS(**employee.model_dump(by_alias=True))
                self.request.execution.employees.append(employee_rs)

    async def _update_execution_times(
        self,
        execution_start_at: datetime,
        execution_end_at: datetime,
    ):
        if execution_start_at > execution_end_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ExecutionRS start_at can`t be after end_at",
            )
        if self.request.execution.start_at and self.request.execution.end_at and self.request.execution.start_at == execution_start_at and self.request.execution.end_at == execution_end_at:
            return
        self.request.execution.start_at = execution_start_at
        self.updated_fields.append(
            UpdatedField(
                name="execution.start_at",
                value=execution_start_at,
                name_display="Время начала работ",
                value_display=execution_start_at.strftime("%H:%M %d.%m.%Y"),
            )
        )
        self.request.execution.end_at = execution_end_at
        self.updated_fields.append(
            UpdatedField(
                name="execution.end_at",
                value=execution_end_at,
                name_display="Время окончания работ",
                value_display=execution_end_at.strftime("%H:%M %d.%m.%Y"),
            )
        )

    async def _update_execution_provider(
        self,
        execution_provider_id: PydanticObjectId,
    ):
        execution_provider = await ProviderS300.get(execution_provider_id)
        if not execution_provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ExecutionRS provider not found",
            )
        house = await HouseS300.get(self.request.id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request have invalid house",
            )
        binds = await self._get_binds(
            house=house,
            provider_id=self.request.provider.id,
            execution_provider_id=execution_provider.id,
            area_id=self.request.area.id if self.request.area else None,
        )
        execution_provider_rs = ProviderRS(
            _id=execution_provider.id,
            name=execution_provider.name,
        )
        self.request.execution.provider = execution_provider_rs
        self.request.binds = binds
        self.updated_fields.append(
            UpdatedField(
                name="execution.provider",
                value=execution_provider_rs,
                name_display="Организация-исполнитель",
                value_display=execution_provider_rs.name,
            )
        )

    async def _update_requester_attachment(
        self,
        requester_attachment: Attachment,
    ):
        file_ids = {f.id for f in requester_attachment.files}
        existing_file_ids = {f.id for f in self.request.requester_attachment.files}
        deleted_file_ids = existing_file_ids - file_ids
        if deleted_file_ids:
            requester_attachment_files = []
            for f in self.request.requester_attachment.files:
                if f.id in deleted_file_ids:
                    self.updated_fields.append(
                        UpdatedField(
                            name="requester_attachment.files",
                            value=f,
                            name_display="Удален файл от жильца",
                            value_display=f.name,
                            link=f"/dispatcher/requests/{str(self.request.id)}/requester_attachment_files/{str(f.id)}",
                        )
                    )
                    continue
                requester_attachment_files.append(f)
            self.request.requester_attachment.files = requester_attachment_files
        if requester_attachment.comment != self.request.requester_attachment.comment:
            self.updated_fields.append(
                UpdatedField(
                    name="requester_attachment.comment",
                    value=requester_attachment.comment,
                    name_display="Комментарий к файлам жильца",
                    value_display=requester_attachment.comment,
                )
            )
            self.request.requester_attachment.comment = requester_attachment.comment

    async def _update_execution_attachment(
        self,
        execution_attachment: Attachment,
    ):
        file_ids = {f.id for f in execution_attachment.files}
        existing_file_ids = {f.id for f in self.request.execution.attachment.files}
        deleted_file_ids = existing_file_ids - file_ids
        if deleted_file_ids:
            execution_attachment_files = []
            for f in self.request.execution.attachment.files:
                if f.id in deleted_file_ids:
                    self.updated_fields.append(
                        UpdatedField(
                            name="execution.attachment.files",
                            value=f,
                            name_display="Удален файл выполненных работ",
                            value_display=f.name,
                            link=f"/dispatcher/requests/{str(self.request.id)}/execution_attachment_files/{str(f.id)}",
                        )
                    )
                execution_attachment_files.append(f)
            self.request.execution.attachment.files = execution_attachment_files
        if execution_attachment.comment != self.request.execution.attachment.comment:
            self.updated_fields.append(
                UpdatedField(
                    name="execution.attachment.comment",
                    value=execution_attachment.comment,
                    name_display="Комментарий к файлам выполненных работ",
                    value_display=execution_attachment.comment,
                )
            )
            self.request.execution.attachment.comment = execution_attachment.comment

    async def _update_execution_act(
        self,
        execution_act: Attachment,
    ):
        file_ids = {f.id for f in execution_act.files}
        existing_file_ids = {f.id for f in self.request.execution.act.files}
        deleted_file_ids = existing_file_ids - file_ids
        if deleted_file_ids:
            execution_act_files = []
            for f in self.request.execution.act.files:
                if f.id in deleted_file_ids:
                    self.updated_fields.append(
                        UpdatedField(
                            name="execution.act.files",
                            value=f,
                            name_display="Удален файл акта выполненных работ",
                            value_display=f.name,
                            link=f"/dispatcher/requests/{str(self.request.id)}/execution_act_files/{str(f.id)}",
                        )
                    )
                execution_act_files.append(f)
            self.request.execution.act.files = execution_act_files
        if execution_act.comment != self.request.execution.act.comment:
            self.updated_fields.append(
                UpdatedField(
                    name="execution.act.comment",
                    value=execution_act.comment,
                    name_display="Комментарий к файлам акта выполненных работ",
                    value_display=execution_act.comment,
                )
            )
            self.request.execution.act.comment = execution_act.comment
