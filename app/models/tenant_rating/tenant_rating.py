from beanie import PydanticObjectId
from pydantic import Field

from models.base_document import BaseDocument


class TenantRating(BaseDocument):
    tenant_id: PydanticObjectId = Field(
        title="Идентификатор жителя",
    )
    provider_id: PydanticObjectId = Field(
        title="Идентификатор организации",
    )
    up: set[PydanticObjectId] = Field(
        default_factory=set,
        title="Идентификатор организации",
    )
    down: set[PydanticObjectId] = Field(
        default_factory=set,
        title="Идентификатор организации",
    )
