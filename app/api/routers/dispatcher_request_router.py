"""
Модуль с роутером для работы с заявками для сотрудников
"""

from beanie import PydanticObjectId
from fastapi import APIRouter, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from file_manager import File
from file_manager.constants import ContentType

from api.dependencies.auth import EmployeeDep
from api.qp_translators.request_qp_translator import (
    DispatcherRequestQPTranslator,
    DispatcherRequestReportQPTranslator,
)
from models.request.request import RequestModel
from schemes.request.dispatcher_request import (
    RequestDCScheme,
    RequestDLScheme,
    RequestDRScheme,
    RequestDUScheme,
)
from schemes.request.request_stats import RequestStats
from schemes.request.request_status import RequestDStatusUScheme
from schemes.request_history import UpdateRequestHistoryRScheme
from services.request.dispatcher_request_report_service import (
    DispatcherRequestReportService,
)
from services.request.dispatcher_request_service import DispatcherRequestService
from services.request.dispatcher_request_update_service import (
    DispatcherRequestUpdateService,
)
from services.request_history_service import RequestHistoryService

dispatcher_request_router = APIRouter(
    tags=["dispatcher_requests"],
)


@dispatcher_request_router.get(
    path="/blank/",
    status_code=status.HTTP_200_OK,
)
async def download_pdf_blanks_zip(
    employee: EmployeeDep,
    req: Request,
):
    params = await DispatcherRequestReportQPTranslator.parse(req.query_params)
    request_service = DispatcherRequestService(employee)
    requests = await request_service.get_requests(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit if params.limit and params.limit < 1000 else 1000,
        sort=params.sort,
    )
    date = ""
    request = await requests.first_or_none()
    if request:
        date = "_" + request.created_at.strftime("%d.%M.%Y")
    report_service = DispatcherRequestReportService(employee)
    headers = {"Content-Disposition": f"attachment; filename={f"request_blanks{date}.zip"}"}
    response = StreamingResponse(report_service.generate_pdf_blanks_zip(requests), media_type=ContentType.ZIP.value, headers=headers)
    return response


@dispatcher_request_router.get(
    path="/{request_id}/blank/",
    status_code=status.HTTP_200_OK,
)
async def download_pdf_blank(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
):
    request_service = DispatcherRequestService(employee)
    request = await request_service.get_request(request_id)
    report_service = DispatcherRequestReportService(employee)
    headers = {"Content-Disposition": f"attachment; filename={f"Бланк заявки №{request.number}.pdf"}"}
    response = StreamingResponse(report_service.generate_pdf_blank(request), media_type=ContentType.PDF.value, headers=headers)
    return response


@dispatcher_request_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model_exclude={"binds"},
    response_model=RequestModel,
)
async def create_request(
    employee: EmployeeDep,
    scheme: RequestDCScheme,
):
    """
    Создание заявки сотрудником
    """

    service = DispatcherRequestService(employee)
    request = await service.create_request(scheme)
    return request


@dispatcher_request_router.get(
    path="/stats/",
    status_code=status.HTTP_200_OK,
    response_model=RequestStats,
)
async def get_request_stats(
    employee: EmployeeDep,
):
    """
    Получения статистики по заявкам сотрудником.
    """
    service = DispatcherRequestService(employee)
    result = await service.get_request_stats()
    return result


@dispatcher_request_router.get(
    path="/",
    description="Получения списка заявок сотрудником.<br>" + DispatcherRequestQPTranslator.get_docs(),
    status_code=status.HTTP_200_OK,
    response_model=list[RequestDLScheme],
)
async def get_request_list(
    employee: EmployeeDep,
    req: Request,
):
    """
    Получения списка заявок сотрудником.
    Для фильтрации есть определенные фильтры см. в модуле api/filters/request_qp_translator
    """

    params = await DispatcherRequestQPTranslator.parse(req.query_params)
    service = DispatcherRequestService(employee)
    requests = await service.get_requests(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit if params.limit and params.limit < 20 else 20,
        sort=params.sort,
    )
    return await requests.to_list()


@dispatcher_request_router.get(
    path="/{request_id}/",
    status_code=status.HTTP_200_OK,
    response_model=RequestDRScheme,
)
async def get_request(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
):
    """
    Получение заявки по идентификатору сотрудником
    """

    service = DispatcherRequestService(employee)
    return await service.get_request(request_id)


@dispatcher_request_router.patch(
    path="/{request_id}/",
    status_code=status.HTTP_200_OK,
    response_model=RequestDRScheme,
)
async def update_request(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
    scheme: RequestDUScheme,
):
    """
    Обновление заявки(кроме изменения статуса и соответствующих статусу полей) сотрудником
    """
    service = DispatcherRequestService(employee)
    request = await service.get_request(request_id)
    update_service = DispatcherRequestUpdateService(
        employee=employee,
        request=request,
    )
    request = await update_service.update_request(scheme)
    return request


@dispatcher_request_router.patch(
    path="/{request_id}/status/",
    status_code=status.HTTP_200_OK,
    response_model=RequestDRScheme,
)
async def update_request_status(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
    scheme: RequestDStatusUScheme,
):
    """
    Обновление статуса и соответствующих статусу полей заявки сотрудником
    """
    service = DispatcherRequestService(employee)
    request = await service.get_request(request_id)
    update_service = DispatcherRequestUpdateService(
        employee=employee,
        request=request,
    )
    request = await update_service.update_request_status(scheme)
    return request


@dispatcher_request_router.get(
    path="/{request_id}/history/",
    status_code=status.HTTP_200_OK,
    response_model=list[UpdateRequestHistoryRScheme],
)
async def get_request_history(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
):
    """
    Обновление статуса и соответствующих статусу полей заявки сотрудником
    """

    service = DispatcherRequestService(employee)
    request = await service.get_request(request_id)

    history_service = RequestHistoryService(
        employee=employee,
        request=request,
    )
    return await history_service.get_request_history()


@dispatcher_request_router.delete(
    path="/{request_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_request(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
):
    """
    Архивирование заявки сотрудником
    """

    service = DispatcherRequestService(employee)
    await service.delete_request(request_id)


@dispatcher_request_router.post(
    path="/{request_id}/restore/",
    status_code=status.HTTP_200_OK,
    response_model=RequestModel,
)
async def reset_request(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
):
    """
    Восстановление заявки суперпользователем
    """

    service = DispatcherRequestService(employee)
    return await service.restore_request(request_id)


@dispatcher_request_router.post(
    path="/{request_id}/requester_attachment_files/",
    status_code=status.HTTP_200_OK,
    response_model=list[File],
)
async def upload_requester_attachment_files(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
    files: list[UploadFile],
):
    """
    Загрузка файлов вложения жителя к заявке сотрудником
    """

    service = DispatcherRequestService(employee)
    request = await service.get_request(request_id)
    update_service = DispatcherRequestUpdateService(
        employee=employee,
        request=request,
    )
    return await update_service.upload_requester_attachment_files(files=files)


@dispatcher_request_router.get(
    path="/{request_id}/requester_attachment_files/{file_id}/",
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


@dispatcher_request_router.post(
    path="/{request_id}/execution_attachment_files/",
    status_code=status.HTTP_200_OK,
    response_model=list[File],
)
async def upload_execution_attachment_files(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
    files: list[UploadFile],
):
    """
    Загрузка файлов вложения выполненных работ к заявке сотрудником
    """

    service = DispatcherRequestService(employee)
    request = await service.get_request(request_id)
    update_service = DispatcherRequestUpdateService(
        employee=employee,
        request=request,
    )
    return await update_service.upload_execution_attachment_files(files=files)


@dispatcher_request_router.get(
    path="/{request_id}/execution_attachment_files/{file_id}/",
    status_code=status.HTTP_200_OK,
)
async def download_execution_attachment_file(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
    file_id: PydanticObjectId,
):
    """
    Скачивание файла вложения выполненных работ к заявке сотрудником
    """

    service = DispatcherRequestService(employee)
    file = await service.download_execution_attachment_file(
        request_id=request_id,
        file_id=file_id,
    )
    response = StreamingResponse(await file.open_stream(), media_type=file.content_type)
    response.headers["Content-Disposition"] = f"attachment; filename={file.name}"
    return response


@dispatcher_request_router.post(
    path="/{request_id}/execution_act_files/",
    status_code=status.HTTP_200_OK,
    response_model=list[File],
)
async def upload_execution_act_files(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
    files: list[UploadFile],
):
    """
    Загрузка файлов акта выполненных работ к заявке сотрудником
    """

    service = DispatcherRequestService(employee)
    request = await service.get_request(request_id)
    update_service = DispatcherRequestUpdateService(
        employee=employee,
        request=request,
    )
    return await update_service.upload_execution_act_files(files=files)


@dispatcher_request_router.get(
    path="/{request_id}/execution_act_files/{file_id}/",
    status_code=status.HTTP_200_OK,
)
async def download_execution_act_file(
    employee: EmployeeDep,
    request_id: PydanticObjectId,
    file_id: PydanticObjectId,
):
    """
    Скачивание файла акта выполненных работ к заявке сотрудником
    """

    service = DispatcherRequestService(employee)
    file = await service.download_execution_act_file(
        request_id=request_id,
        file_id=file_id,
    )
    response = StreamingResponse(await file.open_stream(), media_type=file.content_type)
    response.headers["Content-Disposition"] = f"attachment; filename={file.name}"
    return response
