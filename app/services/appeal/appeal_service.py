from datetime import datetime

from beanie import PydanticObjectId
from fastapi import HTTPException
from starlette import status

from models.appeal.appeal import Appeal
from models.appeal_category.appeal_category import AppealCategory


class AppealService:

    async def _check_categories(self, category_ids: set[PydanticObjectId], provider_id: PydanticObjectId):
        existing_categories_count = await AppealCategory.find({"_id": {"$in": category_ids}, "provider_id": provider_id}).count()
        if existing_categories_count != len(category_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some categories not found",
            )

    async def _generate_number(self, provider_id: PydanticObjectId, current_time: datetime) -> str:
        start_of_year = current_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_next_year = start_of_year.replace(year=start_of_year.year + 1)

        existing_appeal_count = await Appeal.find(
            {
                "provider._id": provider_id,
                "created_at": {"$gte": start_of_year, "$lt": start_of_next_year},
            }
        ).count()
        return f"{existing_appeal_count+1}-{current_time.strftime('%m')}/{current_time.year}"

    @staticmethod
    async def get_filetag_for_answer(appeal_id: PydanticObjectId) -> str:
        return f"appeal answer {str(appeal_id)}"
