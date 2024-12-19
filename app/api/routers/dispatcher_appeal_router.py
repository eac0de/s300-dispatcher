from beanie import PydanticObjectId
from fastapi import APIRouter, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from file_manager import File

from api.dependencies.auth import EmployeeDep
from api.qp_translators.appeal_qp_translator import (
    DispatcherAppealCommentsQPTranslator,
    DispatcherAppealsQPTranslator,
)
from models.appeal.appeal import Appeal
from models.appeal_comment.appeal_comment import AppealComment
from schemes.appeal.appeal_answer import AnswerAppealDCScheme, AnswerAppealDUScheme
from schemes.appeal.appeal_comment import AppealCommentDCScheme, AppealCommentDUScheme
from schemes.appeal.appeal_stats import AppealStats
from schemes.appeal.dispatcher_appeal import (
    AppealCommentStats,
    AppealDCScheme,
    AppealDRLScheme,
    AppealUAcceptScheme,
    AppealUCScheme,
)
from services.appeal.dispatcher_appeal_service import DispatcherAppealService
from services.appeal.dispatcher_appeal_update_service import (
    DispatcherAppealUpdateService,
)
from utils.document_paginator import DocumentPagination

dispatcher_appeal_router = APIRouter(
    tags=["dispatcher_appeals"],
)


@dispatcher_appeal_router.get(
    path="/stats/",
    status_code=status.HTTP_200_OK,
    response_model=AppealStats,
)
async def get_appeal_stats(
    employee: EmployeeDep,
):
    """
    Получения статистики по обращениям сотрудником.
    """
    service = DispatcherAppealService(employee)
    result = await service.get_appeal_stats()
    return result


@dispatcher_appeal_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=AppealDRLScheme,
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
    return {**appeal.model_dump(by_alias=True), "comment_stats": AppealCommentStats(all=0, unread=0)}


@dispatcher_appeal_router.get(
    path="/",
    description="Получения списка обращений сотрудником.<br>" + DispatcherAppealsQPTranslator.get_docs(),
    status_code=status.HTTP_200_OK,
    response_model=DocumentPagination[AppealDRLScheme],
)
async def get_appeal_list(
    employee: EmployeeDep,
    req: Request,
):
    """
    Получения списка обращений сотрудником.
    Для фильтрации есть определенные фильтры см. в модуле api/filters/appeal_qp_translator
    """

    params = await DispatcherAppealsQPTranslator.parse(req.query_params)
    service = DispatcherAppealService(employee)
    appeals = await service.get_appeals(
        query_list=params.query_list,
        sort=params.sort,
    )
    pagination = await DocumentPagination[Appeal].from_find(
        find=appeals,
        limit=params.limit if params.limit else 100,
        offset=params.offset,
    )
    comment_stats_dict = await service.get_comment_stats_dict(
        appeal_ids=[a.id for a in pagination.result],
        employee_id=employee.id,
    )
    pagination.result = [  # type: ignore
        {
            **a.model_dump(by_alias=True),
            "comment_stats": comment_stats_dict.get(a.id, AppealCommentStats(all=0, unread=0)),
        }
        for a in pagination.result
    ]
    return pagination


@dispatcher_appeal_router.get(
    path="/{appeal_id}/",
    status_code=status.HTTP_200_OK,
    response_model=AppealDRLScheme,
)
async def get_appeal(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
):
    """
    Получение обращения по идентификатору сотрудником
    """

    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    comment_stats_dict = await service.get_comment_stats_dict(
        appeal_ids=[appeal.id],
        employee_id=employee.id,
    )
    return {**appeal.model_dump(by_alias=True), "comment_stats": comment_stats_dict.get(appeal.id, AppealCommentStats(all=0, unread=0))}


@dispatcher_appeal_router.patch(
    path="/{appeal_id}/",
    status_code=status.HTTP_200_OK,
    response_model=AppealDRLScheme,
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
    update_service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    appeal = await update_service.update_appeal(scheme)
    comment_stats_dict = await service.get_comment_stats_dict(
        appeal_ids=[appeal.id],
        employee_id=employee.id,
    )
    return {**appeal.model_dump(by_alias=True), "comment_stats": comment_stats_dict.get(appeal.id, AppealCommentStats(all=0, unread=0))}


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


@dispatcher_appeal_router.patch(
    path="/{appeal_id}/accept/",
    status_code=status.HTTP_200_OK,
    response_model=AppealDRLScheme,
)
async def accept_appeal(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    scheme: AppealUAcceptScheme,
):
    """
    Принятие обращения
    """

    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    update_service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    appeal = await update_service.accept_appeal(scheme)
    comment_stats_dict = await service.get_comment_stats_dict(
        appeal_ids=[appeal.id],
        employee_id=employee.id,
    )
    return {**appeal.model_dump(by_alias=True), "comment_stats": comment_stats_dict.get(appeal.id, AppealCommentStats(all=0, unread=0))}


@dispatcher_appeal_router.post(
    path="/{appeal_id}/answers/",
    status_code=status.HTTP_200_OK,
    response_model=AppealDRLScheme,
)
async def answer_appeal(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    scheme: AnswerAppealDCScheme,
):
    """
    Получение обращения по идентификатору сотрудником
    """

    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    update_service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    appeal = await update_service.answer_appeal(scheme)
    comment_stats_dict = await service.get_comment_stats_dict(
        appeal_ids=[appeal.id],
        employee_id=employee.id,
    )
    return {**appeal.model_dump(by_alias=True), "comment_stats": comment_stats_dict.get(appeal.id, AppealCommentStats(all=0, unread=0))}


@dispatcher_appeal_router.patch(
    path="/{appeal_id}/answers/{answer_id}/",
    status_code=status.HTTP_200_OK,
    response_model=AppealDRLScheme,
)
async def update_appeal_answer(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    answer_id: PydanticObjectId,
    scheme: AnswerAppealDUScheme,
):
    """
    Получение обращения по идентификатору сотрудником
    """

    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    update_service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    appeal = await update_service.update_appeal_answer(answer_id, scheme)
    comment_stats_dict = await service.get_comment_stats_dict(
        appeal_ids=[appeal.id],
        employee_id=employee.id,
    )
    return {**appeal.model_dump(by_alias=True), "comment_stats": comment_stats_dict.get(appeal.id, AppealCommentStats(all=0, unread=0))}


@dispatcher_appeal_router.post(
    path="/{appeal_id}/answers/{answer_id}/",
    status_code=status.HTTP_200_OK,
    response_model=AppealDRLScheme,
)
async def upload_answer_files(
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
    appeal = await update_service.upload_answer_files(answer_id=answer_id, files=files)
    comment_stats_dict = await service.get_comment_stats_dict(
        appeal_ids=[appeal.id],
        employee_id=employee.id,
    )
    return {**appeal.model_dump(by_alias=True), "comment_stats": comment_stats_dict.get(appeal.id, AppealCommentStats(all=0, unread=0))}


@dispatcher_appeal_router.get(
    path="/{appeal_id}/answers/{answer_id}/files/{file_id}/",
    status_code=status.HTTP_200_OK,
)
async def download_answer_file(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    answer_id: PydanticObjectId,
    file_id: PydanticObjectId,
):

    service = DispatcherAppealService(employee)
    file = await service.download_answer_file(
        appeal_id=appeal_id,
        answer_id=answer_id,
        file_id=file_id,
    )
    response = StreamingResponse(await file.open_stream(), media_type=file.content_type)
    response.headers["Content-Disposition"] = f"attachment; filename={file.name}"
    return response


@dispatcher_appeal_router.post(
    path="/{appeal_id}/comments/",
    status_code=status.HTTP_200_OK,
    response_model=AppealComment,
)
async def comment_appeal(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    scheme: AppealCommentDCScheme,
):

    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    return await service.comment_appeal(scheme)


@dispatcher_appeal_router.get(
    path="/{appeal_id}/comments/",
    status_code=status.HTTP_200_OK,
    response_model=list[AppealComment],
)
async def get_appeal_comment_list(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    req: Request,
):

    params = await DispatcherAppealCommentsQPTranslator.parse(req.query_params)
    service = DispatcherAppealService(employee)
    appeal_comment_list = await service.get_appeal_comments(
        appeal_id=appeal_id,
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit if params.limit and params.limit < 20 else 20,
        sort=params.sort,
    )
    return appeal_comment_list


@dispatcher_appeal_router.patch(
    path="/{appeal_id}/comments/{comment_id}/read/",
    status_code=status.HTTP_200_OK,
    response_model=AppealComment,
)
async def read_appeal_comment(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    comment_id: PydanticObjectId,
):

    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    return await service.read_appeal_comment(comment_id)


@dispatcher_appeal_router.patch(
    path="/{appeal_id}/comments/{comment_id}/",
    status_code=status.HTTP_200_OK,
    response_model=AppealComment,
)
async def update_appeal_comment(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    comment_id: PydanticObjectId,
    scheme: AppealCommentDUScheme,
):

    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    return await service.update_appeal_comment(
        comment_id=comment_id,
        scheme=scheme,
    )


@dispatcher_appeal_router.post(
    path="/{appeal_id}/comments/{comment_id}/files/",
    status_code=status.HTTP_200_OK,
    response_model=list[File],
)
async def upload_comment_files(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    comment_id: PydanticObjectId,
    files: list[UploadFile],
):
    service = DispatcherAppealService(employee)
    appeal = await service.get_appeal(appeal_id)
    update_service = DispatcherAppealUpdateService(
        employee=employee,
        appeal=appeal,
    )
    return await update_service.upload_comment_files(
        comment_id=comment_id,
        files=files,
    )


@dispatcher_appeal_router.get(
    path="/{appeal_id}/comments/{comment_id}/files/{file_id}/",
    status_code=status.HTTP_200_OK,
)
async def download_comment_file(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
    comment_id: PydanticObjectId,
    file_id: PydanticObjectId,
):

    service = DispatcherAppealService(employee)
    file = await service.download_comment_file(
        appeal_id=appeal_id,
        comment_id=comment_id,
        file_id=file_id,
    )
    response = StreamingResponse(await file.open_stream(), media_type=file.content_type)
    response.headers["Content-Disposition"] = f"attachment; filename={file.name}"
    return response
