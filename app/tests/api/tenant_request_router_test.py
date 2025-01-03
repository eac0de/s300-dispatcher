import jsony
import pytest
from beanie import PydanticObjectId
from client.s300.models.tenant import TenantS300
from httpx import AsyncClient
from models.catalog_item.catalog_item import CatalogItem
from models.request.constants import RequestStatus
from models.request.request import RequestModel
from starlette import status


class TestTenantRequestRouter:

    @pytest.mark.usefixtures("houses", "providers", "areas", "mock_s300_api_get_house_group_ids")
    async def test_create_request(self, api_tenant_client: AsyncClient):
        data = {
            "_type": "area",
            "description": "test_description",
            "execution": {"desired_start_at": "2024-10-09T12:22:54.270", "desired_end_at": "2024-11-09T12:22:54.270"},
        }
        resp = await api_tenant_client.post("/tenant/requests/", json=data)
        assert resp.status_code == status.HTTP_201_CREATED
        resp_json = resp.json()
        assert isinstance(resp_json, dict)

    @pytest.mark.usefixtures("houses", "providers", "areas", "mock_s300_api_get_house_group_ids")
    async def test_create_catalog_request(self, api_tenant_client: AsyncClient, catalog_items: list[CatalogItem]):
        catalog_item = catalog_items[0]
        data = {
            "description": "test_description",
            "commerce": {"catalog_items": [{"_id": catalog_item.id, "quantity": 1}]},
        }
        resp = await api_tenant_client.post("/tenant/requests/catalog/", json=jsony.normalize(data))
        assert resp.status_code == status.HTTP_201_CREATED
        resp_json = resp.json()
        assert isinstance(resp_json, dict)

    async def test_get_request_list(self, api_tenant_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        resp = await api_tenant_client.get("/tenant/requests/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 2
        assert resp_json[0]["_id"] == str(request.id)

        request.requester.id = PydanticObjectId()
        await request.save()
        resp = await api_tenant_client.get("/tenant/requests/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1

        request.is_public = True
        await request.save()
        resp = await api_tenant_client.get("/tenant/requests/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 2

    async def test_get_request(self, api_tenant_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        resp = await api_tenant_client.get(f"/tenant/requests/{request.id}/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json["_id"] == str(request.id)

        request.requester.id = PydanticObjectId()
        await request.save()
        resp = await api_tenant_client.get(f"/tenant/requests/{request.id}/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        request.is_public = True
        await request.save()
        resp = await api_tenant_client.get(f"/tenant/requests/{request.id}/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json["_id"] == str(request.id)

    async def test_rate_request(self, api_tenant_client: AsyncClient, auth_tenant: TenantS300, requests: list[RequestModel]):
        request = requests[0]
        rate_score = 5
        params = {
            "score": rate_score,
        }
        resp = await api_tenant_client.patch(f"/tenant/requests/{request.id}/rate/", params=params)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

        request.status = RequestStatus.PERFORMED
        await request.save()
        resp = await api_tenant_client.patch(f"/tenant/requests/{request.id}/rate/", params=params)
        assert resp.status_code == status.HTTP_200_OK
        await request.sync()
        assert len(request.execution.rates) == 1
        rate = request.execution.rates[0]
        assert rate.tenant_id == auth_tenant.id
        assert rate.score == rate_score

        params = {"score": 0}
        resp = await api_tenant_client.patch(f"/tenant/requests/{request.id}/rate/", params=params)
        assert resp.status_code == status.HTTP_200_OK
        await request.sync()
        assert len(request.execution.rates) == 0

    # Тест для upload_requester_attachment_files
    async def test_upload_requester_attachment_files(self, api_tenant_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        files = [("files", ("file1.txt", b"file_content_1", "text/plain")), ("files", ("file2.txt", b"file_content_2", "text/plain"))]
        resp = await api_tenant_client.post(f"/tenant/requests/{request.id}/requester_attachment_files/", files=files)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == len(files)
