"""
Модуль для обновления заявки сотрудником
"""

from beanie import PydanticObjectId
from fastapi import HTTPException, UploadFile, status

from client.s300.models.department import DepartmentS300
from client.s300.models.employee import EmployeeS300
from models.appeal.appeal import Appeal
from models.appeal.constants import AppealStatus
from models.appeal.embs.observers import EmployeeObserverAS
from models.extra.attachment import EmployeeExpandedAttachment, ExpandedAttachment
from schemes.appeal.dispatcher_appeal import AppealUCScheme
from schemes.extra.attachment import (
    ExpandedAttachmentCScheme,
    ExpandedAttachmentUWithoutCommentScheme,
)
from services.appeal.appeal_service import AppealService


class DispatcherAppealUpdateService(AppealService):

    def __init__(
        self,
        employee: EmployeeS300,
        appeal: Appeal,
    ):
        super().__init__()
        self.employee = employee
        self.appeal = appeal

    async def update_appeal(self, scheme: AppealUCScheme):
        """
        Обновление обращения
        """
        if self.appeal.executor and self.appeal.executor.id != self.employee.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not executor of this request",
            )
        updated_appeal = self.appeal.model_copy(
            deep=True,
            update=scheme.model_dump(
                by_alias=True,
                exclude_unset=True,
                exclude={"observers"},
            ),
        )
        if new_category_ids := set(updated_appeal.category_ids) - set(self.appeal.category_ids):
            await self._check_categories(new_category_ids, self.employee.provider.id)

        existing_observers_employee_ids = set(e.id for e in self.appeal.observers.employees)
        existing_observers_department_ids = set(d.id for d in self.appeal.observers.departments)
        updated_observers_employee_ids = set(e.id for e in updated_appeal.observers.employees)
        updated_observers_department_ids = set(d.id for d in updated_appeal.observers.departments)
        if added_observers_employee_ids := updated_observers_employee_ids - existing_observers_employee_ids:
            for employee_id in added_observers_employee_ids:
                employee = await EmployeeS300.get(employee_id)
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
                self.appeal.observers.employees.append(EmployeeObserverAS.model_validate(employee.model_dump(by_alias=True)))
                self.appeal.binds.dp.add(employee.department.id)
        if added_observers_departments := updated_observers_department_ids - existing_observers_department_ids:
            for department_id in added_observers_departments:
                department = await DepartmentS300.get(department_id)
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
                self.appeal.observers.employees.append(EmployeeObserverAS.model_validate(employee.model_dump(by_alias=True)))
                self.appeal.binds.dp.add(department.id)
        if deleted_observers_employee_ids := existing_observers_employee_ids - updated_observers_employee_ids:
            self.appeal.observers.employees = [e for e in self.appeal.observers.employees if e.id not in deleted_observers_employee_ids]
        if deleted_observers_department_ids := existing_observers_department_ids - updated_observers_department_ids:
            self.appeal.observers.departments = [d for d in self.appeal.observers.departments if d.id not in deleted_observers_department_ids]
        return await self.appeal.save()

    async def answer_appeal(self, answer_scheme: ExpandedAttachmentCScheme):
        if self.appeal.executor and self.appeal.executor.id != self.employee.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not executor of this request",
            )
        answer = ExpandedAttachment(
            employee=EmployeeExpandedAttachment.model_validate(self.employee),
            comment=answer_scheme.comment,
        )
        if self.appeal.answer:
            self.appeal.add_answers.append(answer)
        else:
            self.appeal.answer = answer
            self.appeal.status = AppealStatus.PERFORMED
        return await self.appeal.save()

    async def update_appeal_answer(self, answer_id: PydanticObjectId, answer_scheme: ExpandedAttachmentUWithoutCommentScheme) -> Appeal:
        if not self.appeal.answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found",
            )
        if self.appeal.answer.id == answer_id:
            if self.appeal.answer.employee.id != self.employee.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You are not creator of this answer",
                )
            deleted_file_ids = set(f.id for f in self.appeal.answer.files) - set(f.id for f in answer_scheme.files)
            if not deleted_file_ids:
                return self.appeal
            new_answer_files = []
            for file in self.appeal.answer.files:
                if file.id in deleted_file_ids:
                    await file.delete()
                    continue
                new_answer_files.append(file)
            self.appeal.answer.files = new_answer_files
            return await self.appeal.save()
        for answer in self.appeal.add_answers:
            if answer.id != answer_id:
                continue
            if answer.employee.id != self.employee.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You are not creator of this answer",
                )
            deleted_file_ids = set(f.id for f in answer.files) - set(f.id for f in answer_scheme.files)
            if not deleted_file_ids:
                return self.appeal
            new_answer_files = []
            for file in answer.files:
                if file.id in deleted_file_ids:
                    await file.delete()
                    continue
                new_answer_files.append(file)
            answer.files = new_answer_files
            break
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found",
            )
        return await self.appeal.save()

    async def upload_answer_files(
        self,
        answer_id: PydanticObjectId,
        files: list[UploadFile],
    ) -> list[File]:
        rollbacker = Rollbacker()
        if not files or [file for file in files if file.size == 0]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A file is required, and it cannot be empty (0 bytes)",
            )

        if not self.appeal.answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found",
            )
        if self.appeal.answer.id == answer_id:
            for file in self.appeal.answer.files:
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

    async def _create_files(files: list[UploadFile], rollbacker: Rollbacker,) -> list[File]:
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
