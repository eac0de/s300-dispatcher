from client.s300.models.tenant import TenantS300
from httpx import AsyncClient
from starlette import status


class TestDispatcherTenantRatingRouter:

    async def test_tenant_rating(self, api_employee_client: AsyncClient, auth_tenant: TenantS300):
        resp = await api_employee_client.get(f"/dispatcher/tenant_rating/{auth_tenant.id}/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json.get("current_rate") is None
        assert resp_json.get("up") == 0
        assert resp_json.get("down") == 0

        resp = await api_employee_client.patch(f"/dispatcher/tenant_rating/{auth_tenant.id}/", params={"rate": "up"})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json.get("current_rate") == "up"
        assert resp_json.get("up") == 1
        assert resp_json.get("down") == 0

        resp = await api_employee_client.patch(f"/dispatcher/tenant_rating/{auth_tenant.id}/", params={"rate": "down"})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json.get("current_rate") == "down"
        assert resp_json.get("up") == 0
        assert resp_json.get("down") == 1

        resp = await api_employee_client.patch(f"/dispatcher/tenant_rating/{auth_tenant.id}/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json.get("current_rate") is None
        assert resp_json.get("up") == 0
        assert resp_json.get("down") == 0
