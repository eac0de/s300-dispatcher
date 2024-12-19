import jsony
from httpx import AsyncClient
from starlette import status

from models.request.categories_tree import RequestCategory, RequestSubcategory
from models.request.request import RequestModel
from models.request_template.constants import RequestTemplateType
from models.request_template.request_template import RequestTemplate


class TestRequestTemplateRouter:

    async def test_create_request_template(self, api_employee_client: AsyncClient):
        data = {
            "name": "test_name",
            "category": RequestCategory.BUILDING_RENOVATION,
            "subcategory": RequestSubcategory.GENERAL_PROPERTY,
            "_type": RequestTemplateType.REQUEST,
            "body": "test_body",
        }
        resp = await api_employee_client.post("/dispatcher/request_templates/", json=jsony.normalize(data))
        assert resp.status_code == status.HTTP_201_CREATED
        resp_json = resp.json()
        assert isinstance(resp_json, dict)

    async def test_get_request_template_list(self, api_employee_client: AsyncClient, request_templates: list[RequestTemplate]):
        request_template = request_templates[0]
        resp = await api_employee_client.get("/dispatcher/request_templates/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(request_template.id)
        

    async def test_update_request_template(self, api_employee_client: AsyncClient, request_templates: list[RequestTemplate]):
        request_template = request_templates[0]
        test_name = "test_name_1"
        test_body = "test_body_1"
        data = {
            "name": test_name,
            "category": request_template.category,
            "subcategory": request_template.subcategory,
            "_type": request_template.type,
            "body": test_body,
        }
        resp = await api_employee_client.patch(f"/dispatcher/request_templates/{request_template.id}/", json=jsony.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await request_template.sync()
        assert request_template.name == test_name
        assert request_template.body == test_body

    async def test_delete(self, api_employee_client: AsyncClient, requests: list[RequestModel], request_templates: list[RequestTemplate]):
        request_template = request_templates[0]
        request = requests[0]
        request.relations.template_id = request_template.id
        await request.save()
        resp = await api_employee_client.delete(f"/dispatcher/request_templates/{request_template.id}/")
        assert resp.status_code == status.HTTP_406_NOT_ACCEPTABLE

        request.relations.template_id = None
        await request.save()
        resp = await api_employee_client.delete(f"/dispatcher/request_templates/{request_template.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        r = await RequestTemplate.get(request_template.id)
        assert r is None
