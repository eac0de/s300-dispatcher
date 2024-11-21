from datetime import datetime, timedelta

from celery_app import celery_app
from config import settings
from models.request.archived_request import ArchivedRequestModel, ArchiverType
from models.request.constants import RequestPayStatus, RequestSource
from models.request.request import RequestModel


@celery_app.task
async def archive_unpaid_requests():
    """
    Задача на архивирование неоплаченных заявок
    """
    before_unpaid_request_lifetime = datetime.now() - timedelta(minutes=settings.UNPAID_REQUEST_LIFETIME_MINUTE)
    requests = RequestModel.find(
        {
            "source": RequestSource.CATALOG,
            "commerce.pay_status": RequestPayStatus.WAIT,
            "created_at": {"$lte": before_unpaid_request_lifetime},
        },
    )
    async for request in requests:
        await ArchivedRequestModel(
            archiver_type=ArchiverType.SYSTEM,
            **request.model_dump(by_alias=True),
        ).save()

    await requests.delete()
