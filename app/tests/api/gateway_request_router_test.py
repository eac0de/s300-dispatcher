from httpx import AsyncClient
from starlette import status

from models.catalog_item.catalog_item import CatalogItem
from models.request.constants import RequestPayStatus
from models.request.embs.commerce import CatalogItemCommerceRS
from models.request.request import RequestModel
from utils.json_encoders import EnhancedJSONEncoder


class TestGatewayRequestRouter:

    async def test_get_request_for_pay(self, api_gateway_client: AsyncClient, requests: list[RequestModel], catalog_items: list[CatalogItem]):
        request = requests[0]
        resp = await api_gateway_client.get("/gateway/requests/for_pay/", params={"request_number": request.number})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

        request.commerce.pay_status = RequestPayStatus.WAIT
        catalog_item = catalog_items[0]

        request.commerce.catalog_items = [
            CatalogItemCommerceRS(
                _id=catalog_item.id,
                name=catalog_item.name,
                price=catalog_item.prices[0].amount,
                quantity=2,
            )
        ]
        await request.save()
        resp = await api_gateway_client.get("/gateway/requests/for_pay/", params={"request_number": request.number})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)

    async def test_update_pay_status(self, api_gateway_client: AsyncClient, requests: list[RequestModel]):
        request = requests[0]
        test_pay_status = RequestPayStatus.PAID
        resp = await api_gateway_client.patch(f"/gateway/requests/{request.id}/pay_status/", json=EnhancedJSONEncoder.normalize({"pay_status": test_pay_status}))
        assert resp.status_code == status.HTTP_200_OK
        await request.sync()
        assert request.commerce.pay_status == test_pay_status
