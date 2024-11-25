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
    DepartmentRS,
    DispatcherRS,
    PersonInChargeRS,
    PersonInChargeType,
    PositionRS,
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
from utils.json_encoders import ObjectIdEncoder


@pytest.fixture()
async def requests(auth_employee: EmployeeCache, auth_tenant: TenantCache):
    t = datetime.now()
    return [
        await RequestModel(
            _id=PydanticObjectId("672e35893872fa7eba2e3490"),
            _binds=ProviderHouseGroupBinds(
                pr={auth_employee.provider.id},
                hg={
                    PydanticObjectId("6530efef747cd10016aa416f"),
                    PydanticObjectId("669660ef923fad9568f685cc"),
                    PydanticObjectId("660c16d28d5cf82d2c3c0756"),
                    PydanticObjectId("66d95d3eae7fcb6f3abcbe24"),
                    PydanticObjectId("66d04d913c21e9d625d08e5d"),
                    PydanticObjectId("6644baa09675039c2c5fe6a7"),
                    PydanticObjectId("66b239d303f1d65f7020ca6f"),
                    PydanticObjectId("6644c0e239acd180475adf74"),
                    PydanticObjectId("65ca3748dcee27703f3ed43d"),
                    PydanticObjectId("660c08b6eadc2c25ef00276d"),
                    PydanticObjectId("6570449feac1d60019442a2a"),
                    PydanticObjectId("6570449d141ba100195e2e90"),
                    PydanticObjectId("6703de2b0ef9db6354b2d07c"),
                    PydanticObjectId("66e7ddd9ce7ad1c1aefd3970"),
                    PydanticObjectId("65ca3746ceff5479c03e026c"),
                    PydanticObjectId("6582b252b0d09a001aee0d93"),
                    PydanticObjectId("65b1247a56113d001944df4c"),
                    PydanticObjectId("5e00a6f649a6a500016678c0"),
                    PydanticObjectId("66159730ea27672b0f699002"),
                    PydanticObjectId("66433602399a37949f4c397a"),
                    PydanticObjectId("66263c49f5d00353f46863ed"),
                    PydanticObjectId("6530eff174018700188c0fbd"),
                    PydanticObjectId("65ca367e8ac61fc71e78a3f2"),
                    PydanticObjectId("61b06eecc950b1001a3a31e8"),
                    PydanticObjectId("6644d6b4bb5bd754046f0b99"),
                    PydanticObjectId("667eb42faa833b6106449556"),
                    PydanticObjectId("667e7803a8721f4a90e8c611"),
                    PydanticObjectId("671b647bea65456772dde8ed"),
                    PydanticObjectId("66d04d92ce18a58a594a35d5"),
                    PydanticObjectId("6645b7950d2d79a3aa58d98a"),
                    PydanticObjectId("66d04d948c10448854de2171"),
                    PydanticObjectId("6614fd6800699a71cab97808"),
                    PydanticObjectId("66de9a29733a9d382b94c06c"),
                },
            ),
            _type=RequestType.AREA,
            actions=[ActionRS(start_at=t, end_at=t + timedelta(days=1), _type=ActionRSType.ELECTRICITY)],
            administrative_supervision=True,
            area=AreaRS(_id=auth_tenant.area.id, number=auth_tenant.area.number, formatted_number=auth_tenant.area.formatted_number),
            commerce=CommerceRS(pay_status=RequestPayStatus.NO_CHARGE, catalog_items=[]),
            created_at=t,
            description="test_description_1",
            dispatcher=DispatcherRS(
                _id=auth_employee.id,
                short_name=auth_employee.short_name,
                full_name=auth_employee.full_name,
                phone_numbers=auth_employee.phone_numbers,
                email=auth_employee.email,
                position=PositionRS.model_validate(auth_employee.position.model_dump(by_alias=True)),
                department=DepartmentRS.model_validate(auth_employee.department.model_dump(by_alias=True)),
                provider=ProviderRS.model_validate(auth_employee.provider.model_dump(by_alias=True)),
            ),
            execution=ExecutionRS(
                desired_start_at=None,
                desired_end_at=None,
                provider=ProviderRS(_id=auth_employee.provider.id, name=auth_employee.provider.name),
                employees=[],
                act=Attachment(files=[], comment=""),
                attachment=Attachment(files=[], comment=""),
                is_partially=False,
                rates=[],
                total_rate=0,
            ),
            house=HouseRS(_id=auth_tenant.house.id, address=auth_tenant.house.address),
            housing_supervision=True,
            is_public=False,
            monitoring=MonitoringRS(
                control_messages=[],
                persons_in_charge=[
                    PersonInChargeRS(
                        _id=auth_employee.id,
                        short_name=auth_employee.short_name,
                        full_name=auth_employee.full_name,
                        phone_numbers=auth_employee.phone_numbers,
                        email=auth_employee.email,
                        position=PositionRS.model_validate(auth_employee.position.model_dump(by_alias=True)),
                        department=DepartmentRS.model_validate(auth_employee.department.model_dump(by_alias=True)),
                        provider=ProviderRS.model_validate(auth_employee.provider.model_dump(by_alias=True)),
                        _type=PersonInChargeType.DISPATCHER,
                    )
                ],
            ),
            number="7837582401637",
            provider=ProviderRS(_id=auth_employee.provider.id, name=auth_employee.provider.name),
            relations=RelationsRS(),
            requester=TenantRequester(
                _id=auth_tenant.id,
                short_name=auth_tenant.short_name,
                full_name=auth_tenant.full_name,
                phone_numbers=auth_tenant.phone_numbers,
                email=auth_tenant.email,
                _type=RequesterType.TENANT,
                area=auth_tenant.area,
                house=auth_tenant.house,
            ),
            requester_attachment=Attachment(files=[], comment=""),
            resources=ResourcesRS(materials=[], services=[], warehouses=[]),
            source=RequestSource.DISPATCHER,
            status=RequestStatus.ACCEPTED,
            category=RequestCategory.EMERGENCY,
            subcategory=RequestSubcategory.ELECTRICITY,
            tag=RequestTag.CURRENT,
            work_area=RequestWorkArea.AREA,
        ).save(),
        # await RequestModel(
        #     name="test_name_2",
        #     description="test_description_2",
        #     code="test_code_2",
        #     measurement_unit=CatalogMeasurementUnit.PIECE,
        #     is_available=True,
        #     is_divisible=True,
        #     available_from=t,
        #     group=CatalogItemGroup.PLUMBING,
        #     provider_id=PydanticObjectId(),
        #     prices=[
        #         CatalogItemPrice(
        #             start_at=t,
        #             amount=1000,
        #         )
        #     ],
        #     house_ids={PydanticObjectId()},
        # ).save(),
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
        assert "attachments" in resp_json
        assert len(resp_json["attachments"]) == len(files)

    # Тест для download_requester_attachment_file
    async def test_download_requester_attachment_file(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        request.requester_attachment.files.append(File)
        file_id = "valid_file_id"
        resp = await api_employee_client.get(f"/dispatcher/requests/{request.id}/requester_attachment_files/{file_id}")
        assert resp.status_code == status.HTTP_200_OK
        assert "Content-Disposition" in resp.headers
        assert resp.headers["Content-Type"] == "application/octet-stream"

    # Тест для upload_execution_attachment_files
    async def test_upload_execution_attachment_files(self, api_employee_client: AsyncClient):
        request
        request_id = "valid_request_id"
        files = [("files", ("work_report.pdf", b"file_content", "application/pdf"))]
        resp = await api_employee_client.post(f"/dispatcher/requests/{request_id}/execution_attachment_files", files=files)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert "attachments" in resp_json
        assert len(resp_json["attachments"]) == len(files)

    # Тест для download_execution_attachment_file
    async def test_download_execution_attachment_file(self, api_employee_client: AsyncClient):
        request_id = "valid_request_id"
        file_id = "valid_file_id"
        resp = await api_employee_client.get(f"/dispatcher/requests/{request_id}/execution_attachment_files/{file_id}")
        assert resp.status_code == status.HTTP_200_OK
        assert "Content-Disposition" in resp.headers
        assert resp.headers["Content-Type"] == "application/octet-stream"

    # Тест для upload_execution_act_files
    async def test_upload_execution_act_files(self, api_employee_client: AsyncClient):
        request_id = "valid_request_id"
        files = [("files", ("act.pdf", b"act_content", "application/pdf"))]
        resp = await api_employee_client.post(f"/dispatcher/requests/{request_id}/execution_act_files", files=files)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert "attachments" in resp_json
        assert len(resp_json["attachments"]) == len(files)

    # Тест для download_execution_act_file
    async def test_download_execution_act_file(self, api_employee_client: AsyncClient):
        request_id = "valid_request_id"
        file_id = "valid_file_id"
        resp = await api_employee_client.get(f"/dispatcher/requests/{request_id}/execution_act_files/{file_id}")
        assert resp.status_code == status.HTTP_200_OK
        assert "Content-Disposition" in resp.headers
        assert resp.headers["Content-Type"] == "application/octet-stream"

    # Тест для get_requests_categories_tree
    async def test_get_requests_categories_tree(self, api_employee_client: AsyncClient):
        resp = await api_employee_client.get("/dispatcher/requests/constants/categories_tree")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert "categories" in resp_json
