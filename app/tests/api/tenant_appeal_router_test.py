from beanie import PydanticObjectId
from httpx import AsyncClient
from models.appeal.appeal import Appeal
from models.appeal.constants import AppealStatus
from starlette import status


class TestTenantRequestRouter:

    async def test_get_appeal_list(self, api_tenant_client: AsyncClient, appeals: list[Appeal]):
        appeal = appeals[1]
        resp = await api_tenant_client.get("/tenant/appeals/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 2
        assert resp_json[0]["_id"] == str(appeal.id)

        appeal.appealer.id = PydanticObjectId()
        await appeal.save()
        resp = await api_tenant_client.get("/tenant/appeals/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1

    async def test_get_request(self, api_tenant_client: AsyncClient, appeals: list[Appeal]):
        appeal = appeals[0]
        resp = await api_tenant_client.get(f"/tenant/appeals/{appeal.id}/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json["_id"] == str(appeal.id)

        appeal.appealer.id = PydanticObjectId()
        await appeal.save()
        resp = await api_tenant_client.get(f"/tenant/appeals/{appeal.id}/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_rate_request(self, api_tenant_client: AsyncClient, appeals: list[Appeal]):
        appeal = appeals[0]
        rate_score = 5
        params = {"score": rate_score}
        resp = await api_tenant_client.patch(f"/tenant/appeals/{appeal.id}/rate/", params=params)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

        appeal.status = AppealStatus.PERFORMED
        await appeal.save()
        resp = await api_tenant_client.patch(f"/tenant/appeals/{appeal.id}/rate/", params=params)
        assert resp.status_code == status.HTTP_200_OK
        await appeal.sync()
        assert appeal.rate == rate_score

        rate_score = 5
        params = {"score": rate_score}
        resp = await api_tenant_client.patch(f"/tenant/appeals/{appeal.id}/rate/", params=params)
        assert resp.status_code == status.HTTP_200_OK
        await appeal.sync()
        assert appeal.rate == rate_score

    async def test_upload_appealer_files(self, api_tenant_client: AsyncClient, appeals: list[Appeal]):
        appeal = appeals[0]
        files = [("files", ("file1.txt", b"file_content_1", "text/plain")), ("files", ("file2.txt", b"file_content_2", "text/plain"))]
        resp = await api_tenant_client.post(f"/tenant/appeals/{appeal.id}/appealer_files/", files=files)
        assert resp.status_code == status.HTTP_200_OK
        await appeal.sync()
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == len(files) == len(appeal.appealer_files)
