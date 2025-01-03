"""
Модуль с сервисами для работы с заявками для жителей
"""

from typing import Any

from beanie import PydanticObjectId
from beanie.odm.queries.find import FindMany
from client.s300.models.tenant import TenantS300
from fastapi import HTTPException, UploadFile
from file_manager import File
from models.appeal.appeal import Appeal
from models.appeal.constants import AppealStatus
from services.appeal.appeal_service import AppealService
from starlette import status


class TenantAppealService(AppealService):

    def __init__(self, tenant: TenantS300):

        super().__init__()
        self.tenant = tenant

    async def get_appeal_list(
        self,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> FindMany[Appeal]:
        query_list.append({"appealer._id": self.tenant.id})
        appeals = Appeal.find(*query_list)
        appeals.sort(*sort if sort else ["-_id"])
        appeals.skip(0 if offset is None else offset)
        appeals.limit(20 if limit is None else limit)
        return appeals

    async def get_appeal(
        self,
        appeal_id: PydanticObjectId,
    ) -> Appeal:
        query = {"_id": appeal_id, "appealer._id": self.tenant.id}
        appeal = await Appeal.find_one(query)
        if not appeal:
            raise HTTPException(
                detail="Appeal not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return appeal

    async def rate_appeal(
        self,
        appeal_id: PydanticObjectId,
        score: int,
    ) -> Appeal:
        appeal = await self.get_appeal(appeal_id)
        if appeal.status != AppealStatus.PERFORMED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appeal can only be rated once it has been performed",
            )
        appeal.rate = score
        return await appeal.save()

    async def upload_appealer_files(
        self,
        appeal_id: PydanticObjectId,
        files: list[UploadFile],
    ) -> list[File]:
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Files is required",
            )
        appeal = await self.get_appeal(appeal_id)
        try:
            for file in files:
                f = await File.create(
                    file_content=await file.read(),
                    filename=file.filename if file.filename else "Unknown",
                    tag=await self.get_filetag_for_appealer_files(appeal.id),
                )
                appeal.appealer_files.append(f)
        except:
            for f in appeal.appealer_files:
                await f.delete()
            raise
        await appeal.save()
        return appeal.appealer_files
