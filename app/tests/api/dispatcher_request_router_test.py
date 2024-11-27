from datetime import datetime, timedelta

from httpx import AsyncClient
from starlette import status

from client.c300.models.employee import EmployeeC300
from client.c300.models.tenant import TenantC300
from models.request.request import RequestModel
from utils.grid_fs.file import File
from utils.json_encoders import EnhancedJSONEncoder


class TestDispatcherRequestRouter:

    async def test_create_request(self, api_employee_client: AsyncClient, auth_tenant: TenantC300, requests: list[RequestModel]):
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

    async def test_get_request_stats(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        resp = await api_employee_client.get("/dispatcher/requests/stats")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json == {"accepted": 1, "run": 1, "overdue": 0, "emergency": 2}

        request = requests[1]
        t = datetime.now() - timedelta(days=2)
        request.execution.start_at = t
        request.execution.end_at = t + timedelta(days=1)
        await request.save()
        resp = await api_employee_client.get("/dispatcher/requests/stats")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json == {"accepted": 1, "run": 1, "overdue": 1, "emergency": 2}

    async def test_get_request_list(self, api_employee_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        resp = await api_employee_client.get("/dispatcher/requests/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 2

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
        assert len(resp_json) == 2
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
        resp = await api_employee_client.patch(f"/dispatcher/requests/{request.id}", json=EnhancedJSONEncoder.normalize(data))
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

    async def test_update_request_status(self, api_employee_client: AsyncClient, auth_employee: EmployeeC300, requests: list[RequestModel], mock_c300_api_upsert_storage_docs_out):
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
        resp = await api_employee_client.patch(f"/dispatcher/requests/{request.id}/status", json=EnhancedJSONEncoder.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await request.sync()
        assert request.execution.description is None
        assert request.execution.is_partially is False
        assert request.execution.employees[0].short_name == auth_employee.short_name

        data["resources"]["warehouses"] = [
            {
                "_id": mock_c300_api_upsert_storage_docs_out.warehouse_id,
                "items": [{"_id": mock_c300_api_upsert_storage_docs_out.warehouse_item_id, "quantity": mock_c300_api_upsert_storage_docs_out.test_quantity}],
            },
        ]
        resp = await api_employee_client.patch(f"/dispatcher/requests/{request.id}/status", json=EnhancedJSONEncoder.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        await request.sync()
        assert len(request.resources.warehouses) == 1
        warehouse = request.resources.warehouses[0]
        assert warehouse.id == mock_c300_api_upsert_storage_docs_out.warehouse_id
        assert warehouse.name == mock_c300_api_upsert_storage_docs_out.test_warehouse_name
        assert len(warehouse.items) == 1
        warehouse_item = warehouse.items[0]
        assert warehouse_item.id == mock_c300_api_upsert_storage_docs_out.warehouse_item_id
        assert warehouse_item.name == mock_c300_api_upsert_storage_docs_out.test_warehouse_item_name
        assert warehouse_item.quantity == mock_c300_api_upsert_storage_docs_out.test_quantity
        assert warehouse_item.price == mock_c300_api_upsert_storage_docs_out.test_price

    async def test_get_request_history(self, api_employee_client: AsyncClient, auth_employee: EmployeeC300, requests: list[RequestModel]):
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
        resp = await api_employee_client.patch(f"/dispatcher/requests/{request.id}", json=EnhancedJSONEncoder.normalize(data))
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
