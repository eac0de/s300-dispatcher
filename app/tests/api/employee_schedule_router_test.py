from datetime import datetime, timedelta

import pytest
from beanie import PydanticObjectId
from httpx import AsyncClient
from starlette import status

from models.base.binds import ProviderHouseGroupBinds
from models.cache.employee import EmployeeCache
from models.cache.tenant import TenantCache
from models.extra.attachment import Attachment
from models.request.categories_tree import (
    RequestCategory,
    RequestSubcategory,
    RequestWorkArea,
)
from models.request.constants import (
    RequestPayStatus,
    RequestSource,
    RequestStatus,
    RequestTag,
    RequestType,
)
from models.request.embs.action import ActionRS, ActionRSType
from models.request.embs.area import AreaRS
from models.request.embs.commerce import CommerceRS
from models.request.embs.employee import (
    DispatcherRS,
    EmployeeRS,
    PersonInChargeRS,
    PersonInChargeType,
    ProviderRS,
)
from models.request.embs.execution import ExecutionRS
from models.request.embs.house import HouseRS
from models.request.embs.monitoring import MonitoringRS
from models.request.embs.relations import RelationsRS
from models.request.embs.requester import RequesterType, TenantRequester
from models.request.embs.resources import ResourcesRS
from models.request.request import RequestModel


@pytest.fixture()
async def requests_for_employee_schedule(auth_employee: EmployeeCache, auth_tenant: TenantCache):
    t = datetime.now()
    auth_employee_dict = auth_employee.model_dump(by_alias=True)
    auth_tenant_dict = auth_tenant.model_dump(by_alias=True)
    execution_start_at = t.replace(hour=0, minute=30, second=0, microsecond=0)
    return [
        await RequestModel(
            _id=PydanticObjectId("672e35893872fa7eba2e3490"),
            _binds=ProviderHouseGroupBinds(
                pr={auth_employee.binds_permissions.pr},
                hg={
                    auth_employee.binds_permissions.hg,
                },
            ),
            _type=RequestType.AREA,
            actions=[ActionRS(start_at=t, end_at=t + timedelta(days=1), _type=ActionRSType.ELECTRICITY)],
            administrative_supervision=True,
            area=AreaRS.model_validate(auth_tenant.area.model_dump(by_alias=True)),
            commerce=CommerceRS(pay_status=RequestPayStatus.NO_CHARGE, catalog_items=[]),
            created_at=t,
            description="test_description_1",
            dispatcher=DispatcherRS.model_validate(auth_employee_dict),
            execution=ExecutionRS(
                desired_start_at=None,
                desired_end_at=None,
                start_at=execution_start_at,
                end_at=execution_start_at + timedelta(days=2),
                provider=ProviderRS.model_validate(auth_employee.provider.model_dump(by_alias=True)),
                employees=[EmployeeRS.model_validate(auth_employee_dict)],
                act=Attachment(files=[], comment=""),
                attachment=Attachment(files=[], comment=""),
                is_partially=False,
                rates=[],
                total_rate=0,
            ),
            house=HouseRS.model_validate(auth_tenant.house.model_dump(by_alias=True)),
            housing_supervision=True,
            is_public=False,
            monitoring=MonitoringRS(
                control_messages=[],
                persons_in_charge=[PersonInChargeRS.model_validate({**auth_employee_dict, "_type": PersonInChargeType.DISPATCHER})],
            ),
            number="7837582401637",
            provider=ProviderRS(_id=auth_employee.provider.id, name=auth_employee.provider.name),
            relations=RelationsRS(),
            requester=TenantRequester.model_validate({**auth_tenant_dict, "_type": RequesterType.TENANT}),
            requester_attachment=Attachment(files=[], comment=""),
            resources=ResourcesRS(materials=[], services=[], warehouses=[]),
            source=RequestSource.DISPATCHER,
            status=RequestStatus.RUN,
            category=RequestCategory.EMERGENCY,
            subcategory=RequestSubcategory.ELECTRICITY,
            tag=RequestTag.CURRENT,
            work_area=RequestWorkArea.AREA,
        ).save(),
    ]


class TestDispatcherRequestRouter:

    @pytest.mark.usefixtures("requests_for_employee_schedule")
    async def test_get_request_employee_weekly_schedules(self, api_employee_client: AsyncClient, auth_employee: EmployeeCache):
        resp = await api_employee_client.get("/dispatcher/employee_schedules/weekly", params={"start_at": datetime.now().isoformat(), "employee_ids": [str(auth_employee.id)]})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        schedule = resp_json[0]
        assert schedule["employee_id"] == str(auth_employee.id)
        assert len(schedule["workload"]) == 7
        assert schedule["workload"] == [1, 1, 1, 0, 0, 0, 0]

    async def test_get_request_employee_daily_schedules(self, api_employee_client: AsyncClient, auth_employee: EmployeeCache, requests_for_employee_schedule: list[RequestModel]):
        resp = await api_employee_client.get("/dispatcher/employee_schedules/daily", params={"start_at": datetime.now().isoformat(), "employee_ids": [str(auth_employee.id)]})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        print(resp_json)
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        schedule = resp_json[0]
        assert schedule["employee_id"] == str(auth_employee.id)
        assert len(schedule["workload"]) == 96
        request = requests_for_employee_schedule[0]
        for i in range(2):
            assert schedule["workload"][i] == []
        for i in range(2, 96):
            assert schedule["workload"][i][0] == request.number
