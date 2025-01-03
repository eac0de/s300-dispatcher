"""
Модуль для обновления заявки сотрудником
"""

import asyncio

from beanie import PydanticObjectId
from client.s300.models.department import DepartmentS300
from client.s300.models.employee import EmployeeS300
from fastapi import HTTPException, UploadFile, status
from file_manager import File
from models.appeal.appeal import Appeal
from models.appeal.constants import AppealStatus
from models.appeal.embs.answer import AnswerAS, EmployeeAnswerAS
from models.appeal.embs.employee import EmployeeAS
from models.appeal.embs.observers import EmployeeObserverAS
from models.appeal_comment.appeal_comment import AppealComment, EmployeeAppealComment
from schemes.appeal.appeal_answer import AnswerAppealDCScheme, AnswerAppealDUScheme
from schemes.appeal.appeal_comment import AppealCommentDCScheme, AppealCommentDUScheme
from schemes.appeal.dispatcher_appeal import AppealUCScheme
from services.appeal.appeal_service import AppealService
from utils.rollbacker import Rollbacker


class DispatcherAppealUpdateService(AppealService):

    def __init__(
        self,
        employee: EmployeeS300,
        appeal: Appeal,
    ):
        super().__init__()
        self.employee = employee
        self.appeal = appeal

    async def update_appeal(self, scheme: AppealUCScheme) -> Appeal:
        """
        Обновление обращения
        """
        if self.appeal.executor and self.appeal.executor.id != self.employee.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not executor of this appeal",
            )
        if scheme.executor and scheme.executor.id != self.employee.id:
            await self._update_executor(scheme.executor.id)
            return await self.appeal.save()
        updated_appeal = self.appeal.model_copy(
            deep=True,
            update=scheme.model_dump(
                exclude_unset=True,
                exclude={"observers", "executor"},
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
                updated_appeal.observers.employees.append(EmployeeObserverAS.model_validate(employee.model_dump(by_alias=True)))
                updated_appeal.binds.dp.add(employee.department.id)
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
                updated_appeal.observers.employees.append(EmployeeObserverAS.model_validate(employee.model_dump(by_alias=True)))
                updated_appeal.binds.dp.add(department.id)
        if deleted_observers_employee_ids := existing_observers_employee_ids - updated_observers_employee_ids:
            updated_appeal.observers.employees = [e for e in self.appeal.observers.employees if e.id not in deleted_observers_employee_ids]
        if deleted_observers_department_ids := existing_observers_department_ids - updated_observers_department_ids:
            updated_appeal.observers.departments = [d for d in self.appeal.observers.departments if d.id not in deleted_observers_department_ids]
        return await updated_appeal.save()

    async def _update_executor(self, new_executor_id: PydanticObjectId):
        if self.appeal.answer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't pass on an appeal after a answer",
            )
        new_executor = await EmployeeS300.get(new_executor_id)
        if not new_executor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee not found",
            )
        if new_executor.provider.id != self.employee.provider.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee from another provider",
            )
        self.appeal.executor = EmployeeAS.model_validate(new_executor.model_dump(by_alias=True))
        self.appeal.binds.dp.add(new_executor.department.id)
        if self.appeal.answer and not self.appeal.answer.is_published:
            self.appeal.answer = None
        if self.appeal.add_answers:
            self.appeal.add_answers = [a for a in self.appeal.add_answers if a.is_published]

    async def upload_appealer_files(
        self,
        files: list[UploadFile],
    ) -> list[File]:
        if not files or [file for file in files if file.size == 0]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A file is required, and it cannot be empty (0 bytes)",
            )
        new_files = []
        rollbacker = Rollbacker()
        try:
            for file in files:
                f = await File.create(
                    file_content=await file.read(),
                    filename=file.filename,
                    tag=await self.get_filetag_for_appealer_files(self.appeal.id),
                )
                rollbacker.add_rollback(f.delete)
                new_files.append(f)
            self.appeal.appealer_files.extend(new_files)
            await self.appeal.save()
        except:
            await rollbacker.rollback()
            raise
        return self.appeal.appealer_files

    async def accept_appeal(self) -> Appeal:
        if self.appeal.status != AppealStatus.NEW:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="To be accepted, the appeal must be in an 'accepted' status",
            )
        self.appeal.status = AppealStatus.RUN
        self.appeal.executor = EmployeeAS.model_validate(self.employee.model_dump(by_alias=True))
        return await self.appeal.save()

    async def answer_appeal(self, scheme: AnswerAppealDCScheme) -> Appeal:
        if not self.appeal.executor or self.appeal.executor.id != self.employee.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not executor of this appeal",
            )
        if self.appeal.answer and not self.appeal.answer.is_published or [a for a in self.appeal.add_answers if not a.is_published]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't create a answer without publishing the previous one",
            )
        answer = AnswerAS(
            employee=EmployeeAnswerAS.model_validate(self.employee.model_dump(by_alias=True)),
            text=scheme.text,
        )
        if self.appeal.answer:
            self.appeal.add_answers.append(answer)
        else:
            self.appeal.answer = answer
        return await self.appeal.save()

    async def publish_answer_appeal(
        self,
        answer_id: PydanticObjectId,
    ) -> Appeal:
        answer = await self._get_answer(answer_id)
        if answer.is_published:
            return self.appeal
        answer.is_published = True
        self.appeal.status = AppealStatus.PERFORMED
        return await self.appeal.save()

    async def upload_answer_files(
        self,
        answer_id: PydanticObjectId,
        files: list[UploadFile],
    ) -> Appeal:
        answer = await self._get_answer(answer_id)
        if answer.is_published:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can't update a published appeal",
            )
        if not files or [file for file in files if file.size == 0]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A file is required, and it cannot be empty (0 bytes)",
            )
        new_files = []
        rollbacker = Rollbacker()
        try:
            for file in files:
                f = await File.create(
                    file_content=await file.read(),
                    filename=file.filename,
                    tag=await self.get_filetag_for_answer(self.appeal.id),
                )
                rollbacker.add_rollback(f.delete)
                new_files.append(f)
            answer.files.extend(new_files)
            return await self.appeal.save()
        except:
            await rollbacker.rollback()
            raise

    async def update_appeal_answer(
        self,
        answer_id: PydanticObjectId,
        scheme: AnswerAppealDUScheme,
    ) -> Appeal:
        answer = await self._get_answer(answer_id)
        if answer.is_published:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can't update a published appeal",
            )
        if scheme.files is not None:
            deleted_file_ids = set(f.id for f in answer.files) - set(f.id for f in scheme.files)
            if deleted_file_ids:
                new_answer_files = []
                for file in answer.files:
                    if file.id in deleted_file_ids:
                        asyncio.create_task(file.delete())
                        continue
                    new_answer_files.append(file)
                answer.files = new_answer_files
        if scheme.text is not None:
            answer.text = scheme.text
        return await self.appeal.save()

    async def _get_answer(self, answer_id: PydanticObjectId) -> AnswerAS:
        if not self.appeal.answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found",
            )
        answer = None
        if self.appeal.answer.id == answer_id:
            answer = self.appeal.answer
        for a in self.appeal.add_answers:
            if a.id == answer_id:
                answer = a
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found",
            )
        if answer.employee.id != self.employee.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not creator of this answer",
            )
        return answer

    async def comment_appeal(self, scheme: AppealCommentDCScheme) -> AppealComment:
        if (
            (self.appeal.executor and self.appeal.executor.id != self.employee.id)
            and self.employee.department.id not in set(od.id for od in self.appeal.observers.departments)
            and self.employee.id not in set(oe.id for oe in self.appeal.observers.employees)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ensure the employee is either the executor or an observer of the appeal",
            )

        comment = AppealComment(
            employee=EmployeeAppealComment(
                _id=self.employee.id,
                position_name=self.employee.position.name,
                short_name=self.employee.short_name,
            ),
            appeal_id=self.appeal.id,
            text=scheme.text,
            read_by={self.employee.id},
        )
        return await comment.save()

    async def update_appeal_comment(
        self,
        comment_id: PydanticObjectId,
        scheme: AppealCommentDUScheme,
    ) -> AppealComment:
        comment = await self._get_comment(comment_id)
        if scheme.files is not None:
            deleted_file_ids = set(f.id for f in comment.files) - set(f.id for f in scheme.files)
            if not deleted_file_ids:
                return comment
            new_comment_files = []
            for file in comment.files:
                if file.id in deleted_file_ids:
                    asyncio.create_task(file.delete())
                    continue
                new_comment_files.append(file)
            comment.files = new_comment_files
        if scheme.text is not None:
            comment.text = scheme.text
        await comment.save()
        comment.read_by = {self.employee.id} if self.employee.id in comment.read_by else set()
        return comment

    async def upload_comment_files(
        self,
        comment_id: PydanticObjectId,
        files: list[UploadFile],
    ) -> list[File]:
        if not files or [file for file in files if file.size == 0]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A file is required, and it cannot be empty (0 bytes)",
            )
        comment = await self._get_comment(comment_id)
        new_files = []
        rollbacker = Rollbacker()
        try:
            for file in files:
                f = await File.create(
                    file_content=await file.read(),
                    filename=file.filename,
                    tag=await self.get_filetag_for_answer(self.appeal.id),
                )
                rollbacker.add_rollback(f.delete)
                new_files.append(f)
            comment.files.extend(new_files)
            await comment.save()
        except:
            await rollbacker.rollback()
            raise
        return comment.files

    async def read_appeal_comment(
        self,
        comment_id: PydanticObjectId,
    ) -> AppealComment:
        comment = await self._get_comment(comment_id)
        comment.read_by.add(self.employee.id)
        await comment.save()
        comment.read_by = {self.employee.id}
        return comment

    async def _get_comment(self, comment_id: PydanticObjectId) -> AppealComment:
        comment = await AppealComment.find_one({"_id": comment_id, "appeal_id": self.appeal.id})
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        if comment.employee.id != self.employee.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not creator of this comment",
            )
        return comment
