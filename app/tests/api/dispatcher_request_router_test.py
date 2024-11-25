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
    PersonInChargeRS,
    PersonInChargeType,
    ProviderRS,
)
from models.request.embs.execution import ExecutionRS
from models.request.embs.house import HouseRS
from models.request.embs.monitoring import MonitoringRS
from models.request.embs.relations import RelationsRS
from models.request.embs.requester import RequesterType, TenantRequester
from models.request.embs.resources import (
    ItemWarehouseResourcesRS,
    ResourcesRS,
    WarehouseResourcesRS,
)
from models.request.request import RequestModel
from utils.grid_fs.file import File
from utils.json_encoders import ObjectIdEncoder


@pytest.fixture()
async def requests(auth_employee: EmployeeCache, auth_tenant: TenantCache):
    t = datetime.now()
    auth_employee_dict = auth_employee.model_dump(by_alias=True)
    auth_tenant_dict = auth_tenant.model_dump(by_alias=True)
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
                provider=ProviderRS.model_validate(auth_employee.provider.model_dump(by_alias=True)),
                employees=[],
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
            status=RequestStatus.ACCEPTED,
            category=RequestCategory.EMERGENCY,
            subcategory=RequestSubcategory.ELECTRICITY,
            tag=RequestTag.CURRENT,
            work_area=RequestWorkArea.AREA,
        ).save(),
    ]


class TestDispatcherRequestRouter:

    async def test_create_request(self, api_employee_client: AsyncClient, auth_tenant: TenantCache, requests: list[RequestModel]):
        data = {
            "_type": "area",
            "area": {"_id": str(auth_tenant.area.id)},
            "house": {"_id": str(auth_tenant.house.id)},
            "requester": {"_id": str(auth_tenant.id), "_type": "tenant"},
            "description": "test_description",
            "category": "emergency",
            "subcategory": "electricity",
            "work_area": "area",
            "actions": [{"start_at": "2024-10-09T12:22:54.270", "end_at": "2024-11-09T12:22:54.270", "_type": "electricity"}],
            "administrative_supervision": True,
            "housing_supervision": False,
            "tag": "current",
            "relations": {"requests": [{"_id": str(requests[0].id)}], "template_id": None},
            "is_public": False,
            "execution": {"desired_start_at": "2024-10-09T12:22:54.270", "desired_end_at": "2024-11-09T12:22:54.270"},
        }
        resp = await api_employee_client.post("/dispatcher/requests/", json=data)
        assert resp.status_code == status.HTTP_201_CREATED
        resp_json = resp.json()
        assert isinstance(resp_json, dict)

    async def test_get_requests_list(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        resp = await api_employee_client.get("/dispatcher/requests/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(request.id)

        resp = await api_employee_client.get("/dispatcher/requests/", params={"status__in": request.status.value})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(request.id)

        resp = await api_employee_client.get("/dispatcher/requests/", params={"status__in": "test_no_status__in"})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 0

        resp = await api_employee_client.get("/dispatcher/requests/", params={"area_range": request.area.number if request.area else "1"})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(request.id)

        resp = await api_employee_client.get("/dispatcher/requests/", params={"area_range": "test_no_area_range"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_request(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        resp = await api_employee_client.get(f"/dispatcher/requests/{request.id}")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json["_id"] == str(request.id)

    async def test_update_request(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        test_description = "test_description"
        test_category = "building_renovation"
        test_subcategory = "current_repair"
        test_tag = "urgent"
        test_bool = False
        data = {
            "description": test_description,
            "category": test_category,
            "subcategory": test_subcategory,
            "work_area": None,
            "actions": [],
            "administrative_supervision": test_bool,
            "housing_supervision": test_bool,
            "tag": test_tag,
            "relations": {"requests": [], "template_id": None},
            "is_public": True,
            "execution": {"desired_start_at": None, "desired_end_at": None, "act": {"files": [], "comment": ""}, "attachment": {"files": [], "comment": ""}},
            "requester_attachment": {"files": [], "comment": ""},
        }
        resp = await api_employee_client.patch(f"/dispatcher/requests/{request.id}", json=ObjectIdEncoder.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await request.sync()
        assert request.description == test_description
        assert request.category == test_category
        assert request.subcategory == test_subcategory
        assert request.tag == test_tag
        assert request.administrative_supervision == test_bool
        assert request.housing_supervision == test_bool

    async def test_update_request_status(self, mocker, api_employee_client: AsyncClient, auth_employee: EmployeeCache, requests: list[RequestModel]):
        request = requests[0]
        test_execution_description = "test_execution_description"
        data = {
            "status": "run",
            "execution": {
                "start_at": "2024-10-09T12:22:54.270",
                "end_at": "2024-10-10T12:22:54.270",
                "provider": {"_id": auth_employee.provider.id},
                "employees": [{"_id": auth_employee.id}],
                "description": test_execution_description,
                "is_partially": True,
                "warranty_until": None,
                "delayed_until": None,
            },
            "resources": {"materials": [], "services": [], "warehouses": []},
        }
        resp = await api_employee_client.patch(f"/dispatcher/requests/{request.id}/status", json=ObjectIdEncoder.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await request.sync()
        assert request.execution.description is None
        assert request.execution.is_partially is False
        assert request.execution.employees[0].short_name == auth_employee.short_name

        warehouse_id = PydanticObjectId()
        warehouse_item_id = PydanticObjectId()
        test_quantity = 1000
        test_price = 1000
        test_warehouse_name = "Замоканный склад"
        test_warehouse_item_name = "Замоканная позиция склада"
        mock_return = [
            WarehouseResourcesRS(
                _id=warehouse_id,
                name=test_warehouse_name,
                items=[ItemWarehouseResourcesRS(_id=warehouse_item_id, name=test_warehouse_item_name, price=test_price, quantity=test_quantity)],
            )
        ]
        mocker.patch("client.c300_api.C300API.upsert_storage_docs_out", return_value=mock_return)
        data["resources"]["warehouses"] = [
            {"_id": warehouse_id, "items": [{"_id": warehouse_item_id, "quantity": test_quantity}]},
        ]
        resp = await api_employee_client.patch(f"/dispatcher/requests/{request.id}/status", json=ObjectIdEncoder.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        await request.sync()
        assert len(request.resources.warehouses) == 1
        warehouse = request.resources.warehouses[0]
        assert warehouse.id == warehouse_id
        assert warehouse.name == test_warehouse_name
        assert len(warehouse.items) == 1
        warehouse_item = warehouse.items[0]
        assert warehouse_item.id == warehouse_item_id
        assert warehouse_item.name == test_warehouse_item_name
        assert warehouse_item.quantity == test_quantity
        assert warehouse_item.price == test_price

    async def test_get_request_history(self, api_employee_client: AsyncClient, auth_employee: EmployeeCache, requests: list[RequestModel]):
        request = requests[0]
        request.created_at = datetime.now() - timedelta(days=1)  # Заявка если только создана не создает историю а просто перезаписывает поля
        await request.save()
        resp = await api_employee_client.get(f"/dispatcher/requests/{request.id}/history")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 0
        test_description = "test_description"
        data = request.model_dump(by_alias=True)
        data["description"] = test_description
        resp = await api_employee_client.patch(f"/dispatcher/requests/{request.id}", json=ObjectIdEncoder.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp = await api_employee_client.get(f"/dispatcher/requests/{request.id}/history")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        update = resp_json[0]
        update_user = update.get("user", {})
        update_user_id = update_user.get("_id", "")
        assert update_user_id == str(auth_employee.id)
        update_fields = update.get("updated_fields", [])
        assert len(update_fields) == 1
        assert update_fields[0].get("value_display", "") == test_description

    # Тест для reset_request
    async def test_delete_and_reset_request(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        resp = await api_employee_client.delete(f"/dispatcher/requests/{request.id}")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        r = await RequestModel.get(request.id)
        assert r is None
        resp = await api_employee_client.post(f"/dispatcher/requests/{request.id}/restore")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Тест для upload_requester_attachment_files
    async def test_upload_requester_attachment_files(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        files = [("files", ("file1.txt", b"file_content_1", "text/plain")), ("files", ("file2.txt", b"file_content_2", "text/plain"))]
        resp = await api_employee_client.post(f"/dispatcher/requests/{request.id}/requester_attachment_files", files=files)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == len(files)

    # Тест для download_requester_attachment_file
    async def test_download_requester_attachment_file(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        file_content = b"file_content_1"
        file = await File.create(file_content, "file1.txt", f"requester_attachment {request.id}")
        request.requester_attachment.files.append(file)
        await request.save()
        resp = await api_employee_client.get(f"/dispatcher/requests/{request.id}/requester_attachment_files/{file.id}")
        assert resp.status_code == status.HTTP_200_OK
        assert "Content-Disposition" in resp.headers
        assert "text/plain" in resp.headers["Content-Type"]
        assert await resp.aread() == file_content

    # Тест для upload_execution_attachment_files
    async def test_upload_execution_attachment_files(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        files = [("files", ("file1.txt", b"file_content_1", "text/plain")), ("files", ("file2.txt", b"file_content_2", "text/plain"))]
        resp = await api_employee_client.post(f"/dispatcher/requests/{request.id}/execution_attachment_files", files=files)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == len(files)

    # Тест для download_execution_attachment_file
    async def test_download_execution_attachment_file(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        file_content = b"file_content_1"
        file = await File.create(file_content, "file1.txt", f"execution_attachment {request.id}")
        request.requester_attachment.files.append(file)
        await request.save()
        resp = await api_employee_client.get(f"/dispatcher/requests/{request.id}/execution_attachment_files/{file.id}")
        assert resp.status_code == status.HTTP_200_OK
        assert "Content-Disposition" in resp.headers
        assert "text/plain" in resp.headers["Content-Type"]
        assert await resp.aread() == file_content

    # Тест для upload_execution_act_files
    async def test_upload_execution_act_files(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        files = [("files", ("file1.txt", b"file_content_1", "text/plain")), ("files", ("file2.txt", b"file_content_2", "text/plain"))]
        resp = await api_employee_client.post(f"/dispatcher/requests/{request.id}/execution_act_files", files=files)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == len(files)

    # Тест для download_execution_act_file
    async def test_download_execution_act_file(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        file_content = b"file_content_1"
        file = await File.create(file_content, "file1.txt", f"execution_act {request.id}")
        request.requester_attachment.files.append(file)
        await request.save()
        resp = await api_employee_client.get(f"/dispatcher/requests/{request.id}/execution_act_files/{file.id}")
        assert resp.status_code == status.HTTP_200_OK
        assert "Content-Disposition" in resp.headers
        assert "text/plain" in resp.headers["Content-Type"]
        assert await resp.aread() == file_content
