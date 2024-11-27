from httpx import AsyncClient
from starlette import status


class TestConstantsRouter:

    async def test_get_requests_constants(self, api_employee_client: AsyncClient):
        resp = await api_employee_client.get("/constants/requests/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)

    async def test_get_requests_categories_tree(self, api_employee_client: AsyncClient):
        resp = await api_employee_client.get("/constants/requests/categories_tree/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
