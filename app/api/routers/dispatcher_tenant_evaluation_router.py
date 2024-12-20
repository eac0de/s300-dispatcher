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

dispatcher_tenant_rating_router = APIRouter(
    tags=["dispatcher_tenant_rating"],
)


@dispatcher_tenant_rating_router.post(
    path="/",
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