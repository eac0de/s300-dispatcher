import jsony
from httpx import AsyncClient
from models.appeal.appeal import Appeal
from models.appeal_category.appeal_category import AppealCategory
from starlette import status


class TestAppealCategoryRouter:

    async def test_create_appeal_category(self, api_employee_client: AsyncClient):
        data = {
            "name": "test_name",
            "description": "test_description",
        }
        resp = await api_employee_client.post("/dispatcher/appeal_categories/", json=jsony.normalize(data))
        assert resp.status_code == status.HTTP_201_CREATED
        resp_json = resp.json()
        assert isinstance(resp_json, dict)

    async def test_get_appeal_category_list(self, api_employee_client: AsyncClient, appeal_categories: list[AppealCategory]):
        appeal_category = appeal_categories[0]
        resp = await api_employee_client.get("/dispatcher/appeal_categories/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(appeal_category.id)

    async def test_update_appeal_category(self, api_employee_client: AsyncClient, appeal_categories: list[AppealCategory]):
        appeal_category = appeal_categories[0]
        test_name = "test_name_1"
        test_description = "test_body_1"
        data = {
            "name": test_name,
            "description": test_description,
        }
        resp = await api_employee_client.patch(f"/dispatcher/appeal_categories/{appeal_category.id}/", json=jsony.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await appeal_category.sync()
        assert appeal_category.name == test_name
        assert appeal_category.description == test_description

    async def test_delete_appeal_category(self, api_employee_client: AsyncClient, appeals: list[Appeal], appeal_categories: list[AppealCategory]):
        appeal_category = appeal_categories[0]
        appeal = appeals[0]

        appeal.category_ids = set([appeal_category.id])
        await appeal.save()
        resp = await api_employee_client.delete(f"/dispatcher/appeal_categories/{appeal_category.id}/")
        assert resp.status_code == status.HTTP_406_NOT_ACCEPTABLE

        appeal.category_ids = set()
        await appeal.save()
        resp = await api_employee_client.delete(f"/dispatcher/appeal_categories/{appeal_category.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        r = await AppealCategory.get(appeal_category.id)
        assert r is None
