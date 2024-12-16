from beanie import PydanticObjectId
from fastapi import APIRouter, Request, UploadFile, status
from file_manager import File

from api.dependencies.auth import EmployeeDep
from api.qp_translators.appeal_qp_translator import DispatcherAppealsQPTranslator
from api.qp_translators.request_qp_translator import DispatcherRequestQPTranslator
from schemes.appeal.dispatcher_appeal import (
    AppealDCScheme,
    AppealDLScheme,
    AppealDRScheme,
    AppealUCScheme,
)
from schemes.extra.attachment import (
    ExpandedAttachmentCScheme,
    ExpandedAttachmentUWithoutCommentScheme,
)
from services.appeal.dispatcher_appeal_service import DispatcherAppealService
from services.appeal.dispatcher_appeal_update_service import (
    DispatcherAppealUpdateService,
)

dispatcher_appeal_router = APIRouter(
    tags=["dispatcher_appeals"],
)


@dispatcher_appeal_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=AppealDRScheme,
)
async def create_appeal(
    employee: EmployeeDep,
    scheme: AppealDCScheme,
):
    """
    Создание обращения сотрудником
    """

    service = DispatcherAppealService(employee)
    appeal = await service.create_appeal(scheme)
    return appeal


@dispatcher_appeal_router.get(
    path="/",
    description="Получения списка обращений сотрудником.<br>" + DispatcherAppealsQPTranslator.get_docs(),
    status_code=status.HTTP_200_OK,
    response_model=list[AppealDLScheme],
)
async def get_appeal_list(
    employee: EmployeeDep,
    req: Request,
):
    """
    Получения списка обращений сотрудником.
    Для фильтрации есть определенные фильтры см. в модуле api/filters/appeal_qp_translator
    """

    params = await DispatcherRequestQPTranslator.parse(req.query_params)
    service = DispatcherAppealService(employee)
    appeals = await service.get_appeals(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit if params.limit and params.limit < 20 else 20,
        sort=params.sort,
    )
    return await appeals.to_list()


@dispatcher_appeal_router.get(
    path="/{appeal_id}/",
    status_code=status.HTTP_200_OK,
    response_model=AppealDRScheme,
)
async def get_appeal(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
):
    """
    Получение обращения по идентификатору сотрудником
    """

    service = DispatcherAppealService(employee)
    return await service.get_appeal(appeal_id)


@dispatcher_appeal_router.patch(
    path="/{appeal_id}/",
    status_code=status.HTTP_200_OK,
    response_model=AppealDRScheme,
)
async def update_appeal(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    scheme: AppealUCScheme,
):
    """
    Получение обращения по идентификатору сотрудником
    """

    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    return await service.update_appeal(scheme)


@dispatcher_appeal_router.delete(
    path="/{appeal_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_appeal(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
):
    """
    Получение обращения по идентификатору сотрудником
    """

    service = DispatcherAppealService(employee)
    await service.delete_appeal(appeal_id)


@dispatcher_appeal_router.post(
    path="/{appeal_id}/answer/",
    status_code=status.HTTP_200_OK,
    response_model=AppealDRScheme,
)
async def answer_appeal(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    answer_scheme: ExpandedAttachmentCScheme,
):
    """
    Получение обращения по идентификатору сотрудником
    """

    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    return await service.answer_appeal(answer_scheme)


@dispatcher_appeal_router.patch(
    path="/{appeal_id}/answer/{answer_id}/",
    status_code=status.HTTP_200_OK,
    response_model=AppealDRScheme,
)
async def update_appeal_answer(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    answer_id: PydanticObjectId,
    answer_scheme: ExpandedAttachmentUWithoutCommentScheme,
):
    """
    Получение обращения по идентификатору сотрудником
    """

    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    return await service.update_appeal_answer(answer_id, answer_scheme)


@dispatcher_appeal_router.post(
    path="/{appeal_id}/answer/{answer_id}/",
    status_code=status.HTTP_200_OK,
    response_model=list[File],
)
async def upload_requester_attachment_files(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    answer_id: PydanticObjectId,
    files: list[UploadFile],
):
    """
    Загрузка файлов вложения жителя к заявке сотрудником
    """

    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    update_service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    return await update_service.upload_answer_files(answer_id=answer_id, files=files)


@dispatcher_appeal_router.get(
    path="/{appeal_id}/answer/{answer_id}/files/{file_id}/",
    status_code=status.HTTP_200_OK,
)
async def download_requester_attachment_file(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
    file_id: PydanticObjectId,
):
    """
    Скачивание файла вложения жителя к заявке сотрудником
    """

    service = DispatcherRequestService(employee)
    file = await service.download_requester_attachment_file(
        request_id=request_id,
        file_id=file_id,
    )
    response = StreamingResponse(await file.open_stream(), media_type=file.content_type)
    response.headers["Content-Disposition"] = f"attachment; filename={file.name}"
    return response
