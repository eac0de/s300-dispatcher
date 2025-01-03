import pytest
from httpx import AsyncClient
from models.catalog_item.catalog_item import CatalogItem
from starlette import status


class TestTenantCatalogItemRouter:

    @pytest.mark.usefixtures("houses")
    async def test_get_catalog_item_list(self, api_tenant_client: AsyncClient, catalog_items: list[CatalogItem]):
        catalog_item = catalog_items[0]
        resp = await api_tenant_client.get("/tenant/catalog/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(catalog_item.id)

        resp = await api_tenant_client.get("/tenant/catalog/", params={"group": catalog_item.group.value})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(catalog_item.id)

        resp = await api_tenant_client.get("/tenant/catalog/", params={"group": "test_no_group"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.usefixtures("houses")
    async def test_get_catalog_item_groups(self, api_tenant_client: AsyncClient, catalog_items: list[CatalogItem]):
        resp = await api_tenant_client.get("/tenant/catalog/groups/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0] == catalog_items[0].group.value
