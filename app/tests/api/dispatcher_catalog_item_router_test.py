from datetime import timedelta

from beanie import PydanticObjectId
import pytest
from client.s300.models.employee import EmployeeS300
from client.s300.models.tenant import TenantS300
from config import settings
from httpx import AsyncClient
from models.catalog_item.catalog_item import CatalogItem
from starlette import status

TEST_FILEPATH = f"{settings.PROJECT_DIR}/tests/static/"
TEST_FILENAME = "test_image.jpeg"


class TestDispatcherCatalogItemRouter:

    async def test_get_catalog_item_list(self, api_employee_client: AsyncClient, catalog_items: list[CatalogItem]):
        catalog_item = catalog_items[0]
        resp = await api_employee_client.get("/dispatcher/catalog/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(catalog_item.id)

        resp = await api_employee_client.get("/dispatcher/catalog/", params={"name": catalog_item.name[:1]})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(catalog_item.id)

        resp = await api_employee_client.get("/dispatcher/catalog/", params={"name": "test_no_name"})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 0

        resp = await api_employee_client.get("/dispatcher/catalog/", params={"group": catalog_item.group.value})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(catalog_item.id)

        resp = await api_employee_client.get("/dispatcher/catalog/", params={"group": "test_no_group"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_catalog_item_groups(self, api_employee_client: AsyncClient, catalog_items: list[CatalogItem]):
        resp = await api_employee_client.get("/dispatcher/catalog/groups/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0] == catalog_items[0].group.value

    @pytest.mark.usefixtures("mock_s300_api_get_allowed_house_ids")
    async def test_create_catalog_item(self, api_employee_client: AsyncClient, auth_employee: EmployeeS300, auth_tenant: TenantS300):
        test_name = "test_name"
        test_code = "test_code"
        tenant_house_id = auth_tenant.house.id
        data = {
            "name": test_name,
            "description": "test_description",
            "code": test_code,
            "measurement_unit": "liter",
            "is_available": True,
            "is_divisible": True,
            "available_from": "2024-11-07T14:48:58.768Z",
            "available_until": None,
            "group": "electrics",
            "prices": [{"start_at": "2024-11-07T14:48:58.768Z", "amount": 100}],
            "house_ids": [str(tenant_house_id)],
            "house_group_ids": [],
            "fias": [],
        }
        resp = await api_employee_client.post("/dispatcher/catalog/", json=data)
        assert resp.status_code == status.HTTP_201_CREATED
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        catalog_item = await CatalogItem.get(PydanticObjectId(resp_json["_id"]))
        assert catalog_item is not None
        assert catalog_item.code == test_code
        assert catalog_item.name == test_name
        assert catalog_item.provider_id == auth_employee.provider.id
        assert len(catalog_item.house_ids) == 1
        assert list(catalog_item.house_ids)[0] == tenant_house_id

        resp = await api_employee_client.post("/dispatcher/catalog/", json=data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

        data["available_from"] = "2024-10-07T14:48:58.768Z"
        data["name"] = "new_name"
        data["code"] = "new_code"
        resp = await api_employee_client.post("/dispatcher/catalog/", json=data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_catalog_item(self, api_employee_client: AsyncClient, catalog_items: list[CatalogItem]):
        catalog_item = catalog_items[0]
        test_name = "test_name"
        test_code = "test_code"
        data = {
            "name": test_name,
            "description": "test_description",
            "code": test_code,
            "measurement_unit": "liter",
            "is_available": True,
            "is_divisible": True,
            "available_from": catalog_item.available_from.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "available_until": None,
            "group": "electrics",
            "prices": [
                {"start_at": "2024-09-07T14:48:58.768", "amount": 123},
                {"start_at": "2024-10-07T14:48:58.768", "amount": 145},
                {"start_at": "2024-11-07T14:48:58.768", "amount": 167},
            ],
            "house_ids": [],
            "house_group_ids": [],
            "fias": [],
            "image": None,
        }
        resp = await api_employee_client.patch(f"/dispatcher/catalog/{catalog_item.id}/", json=data)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await catalog_item.sync()
        assert catalog_item.name == test_name
        assert len(catalog_item.house_ids) == 0
        assert len(catalog_item.prices) == 1

        data["prices"] = [{"start_at": (catalog_item.available_from + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3], "amount": 200}]
        resp = await api_employee_client.patch(f"/dispatcher/catalog/{catalog_item.id}/", json=data)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await catalog_item.sync()
        assert len(catalog_item.prices) == 2

        catalog_item = catalog_items[1]
        resp = await api_employee_client.patch(f"/dispatcher/catalog/{catalog_item.id}/", json=data)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_catalog_item(self, api_employee_client: AsyncClient, catalog_items: list[CatalogItem]):
        catalog_item = catalog_items[0]
        resp = await api_employee_client.delete(f"/dispatcher/catalog/{catalog_item.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert await CatalogItem.get(catalog_item.id) is None

        catalog_item = catalog_items[1]
        resp = await api_employee_client.delete(f"/dispatcher/catalog/{catalog_item.id}/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_catalog_item_image(self, api_employee_client: AsyncClient, catalog_items: list[CatalogItem]):
        catalog_item = catalog_items[0]
        resp = await api_employee_client.get(f"/dispatcher/catalog/{catalog_item.id}/image/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        with open(TEST_FILEPATH + TEST_FILENAME, "rb") as file:
            file_content = file.read()
        resp = await api_employee_client.post(f"/dispatcher/catalog/{catalog_item.id}/image/", files={"file": (TEST_FILENAME, file_content, "image/jpeg")})
        assert resp.status_code == status.HTTP_200_OK
        await catalog_item.sync()
        assert catalog_item.image is not None
        assert catalog_item.image.name == TEST_FILENAME

        resp = await api_employee_client.get(f"/dispatcher/catalog/{catalog_item.id}/image/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.headers["Content-Disposition"] == f"attachment; filename*=UTF-8''{TEST_FILENAME}"
        assert resp.headers["Content-Type"] == "image/jpeg"
        assert resp.content == file_content

        data = {
            "name": "test_name",
            "description": "test_description",
            "code": "test_code",
            "measurement_unit": "liter",
            "is_available": True,
            "is_divisible": True,
            "available_from": catalog_item.available_from.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "available_until": None,
            "group": "electrics",
            "prices": [],
            "house_ids": [],
            "house_group_ids": [],
            "fias": [],
            "image": None,
        }
        resp = await api_employee_client.patch(f"/dispatcher/catalog/{catalog_item.id}/", json=data)
        assert resp.status_code == status.HTTP_200_OK
        await catalog_item.sync()
        assert catalog_item.image is None

        catalog_item = catalog_items[1]
        resp = await api_employee_client.post(f"/dispatcher/catalog/{catalog_item.id}/image/", files={"file": (TEST_FILENAME, file_content, "image/jpeg")})
        assert resp.status_code == status.HTTP_404_NOT_FOUND
