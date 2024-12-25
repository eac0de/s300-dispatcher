from pydantic import BaseModel, Field


class TenantRequestStats(BaseModel):
    tenant: int = Field(
        title="Долги жителя",
    )
    area: int = Field(
        title="Долги жителя",
    )
    house: int = Field(
        title="Долги жителя",
    )
    type_area: int = Field(
        title="Долги жителя",
    )
