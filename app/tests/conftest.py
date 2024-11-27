from datetime import datetime, timedelta

import aiodocker
import jwt
import pytest
from asgi_lifespan import LifespanManager
from beanie import PydanticObjectId
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from client.c300.models.area import AreaC300
from client.c300.models.employee import EmployeeC300
from client.c300.models.house import HouseC300
from client.c300.models.provider import ProviderC300
from client.c300.models.tenant import TenantC300
from config import settings
from database import init_db
from main import app
from models.base.binds import ProviderBinds, ProviderHouseGroupBinds
from models.catalog_item.catalog_item import CatalogItem, CatalogItemPrice
from models.catalog_item.constants import CatalogItemGroup, CatalogMeasurementUnit
from models.extra.attachment import Attachment
from models.extra.phone_number import PhoneNumber, PhoneType
from models.other.other_employee import OtherEmployee
from models.other.other_person import OtherPerson
from models.other.other_provider import OtherProvider
from models.request.archived_request import ArchivedRequestModel
from models.request.categories_tree import (
    RequestCategory,
    RequestSubcategory,
    RequestWorkArea,
)
from models.request.constants import (
    RequestPayStatus,
    RequestSource,
    RequestStatus,
    RequestTag,
    RequestType,
)
from models.request.embs.action import ActionRS, ActionRSType
from models.request.embs.area import AreaRS
from models.request.embs.commerce import CommerceRS
from models.request.embs.employee import (
    DispatcherRS,
    EmployeeRS,
    PersonInChargeRS,
    PersonInChargeType,
    ProviderRS,
)
from models.request.embs.execution import ExecutionRS
from models.request.embs.house import HouseRS
from models.request.embs.monitoring import MonitoringRS
from models.request.embs.relations import RelationsRS
from models.request.embs.requester import RequesterType, TenantRequester
from models.request.embs.resources import (
    ItemWarehouseResourcesRS,
    ResourcesRS,
    WarehouseResourcesRS,
)
from models.request.request import RequestModel
from models.request_history.request_history import RequestHistory
from models.request_template.constants import RequestTemplateType
from models.request_template.request_template import RequestTemplate


@pytest.fixture(scope="session", autouse=True)
def check_mode():
    if settings.MODE != "TEST":
        raise PermissionError(
            f"Для проведения тестов параметр MODE должен быть равен TEST. Текущий MODE = {settings.MODE}. Внимание! Запрещено менять MODE вручную. Он должен автоматически измениться из среды окружения созданной для тестов!"
        )


@pytest.fixture(scope="session", autouse=True)
async def create_db_container():
    docker = aiodocker.Docker()
    try:
        await docker.images.inspect("mongo:latest")
    except aiodocker.DockerError:
        await docker.images.pull("mongo:latest")
    container = await docker.containers.create_or_replace(
        name="mongodb",
        config={
            "Image": "mongo:latest",
            "Ports": {"27017/tcp": {}},  # Проброс порта 27017
            "HostConfig": {"PortBindings": {"27017/tcp": [{"HostPort": "27017"}]}},  # Проброс на локальный порт 27017
        },
    )
    await container.start()
    yield
    await container.stop()
    await container.delete()
    volumes_info = await docker.volumes.list()
    volumes = volumes_info.get("Volumes", [])
    for v_dict in volumes:
        volume = await docker.volumes.get(v_dict["Name"])
        await volume.delete()


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
    models = [
        RequestModel,
        ArchivedRequestModel,
        TenantC300,
        EmployeeC300,
        HouseC300,
        AreaC300,
        ProviderC300,
        RequestHistory,
        CatalogItem,
        RequestTemplate,
        OtherPerson,
        OtherEmployee,
        OtherProvider,
    ]
    for model in models:
        await model.get_motor_collection().drop()
        await model.get_motor_collection().drop_indexes()


@pytest.fixture()
@pytest.mark.usefixtures("setup_db")
async def auth_employee():
    worker = EmployeeC300.model_validate(
        {
            "_id": "6343c35a80fa3d001a9a4c9e",
            "binds_permissions": {"pr": "61b06a693b6d6e0019260942", "hg": "61b06eecc950b1001a3a31e8"},
            "department": {"_id": "6266a359af0f82000fcada27", "name": "Бухгалтерский отдел"},
            "email": "tester@roscluster.ru",
            "external_control": None,
            "full_name": "Тестовый Пользователь",
            "is_super": False,
            "number": "7806766325120",
            "phone_numbers": [],
            "position": {"_id": "6266a35e0714690018b76001", "name": "Иванова Ирина Ивановна"},
            "provider": {"_id": "61b06a693b6d6e0019260942", "name": 'ТСЖ "На Примере"'},
            "short_name": "Тестовый П..",
        }
    )
    return await worker.save()


@pytest.fixture()
async def auth_employee_cookie(auth_employee: EmployeeC300):
    token = jwt.encode(
        payload={
            "profile": auth_employee.number,
            "username": auth_employee.number,
            "type": 1,
            "is_superuser": False,
        },
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return {"access_token": token}


@pytest.fixture()
async def api_employee_client(auth_employee_cookie: dict[str, str]):
    async with LifespanManager(app, startup_timeout=100, shutdown_timeout=100):
        server_name = "http://localhost"
        async with AsyncClient(transport=ASGITransport(app=app), base_url=server_name, cookies=auth_employee_cookie) as ac:  # type: ignore
            yield ac


@pytest.fixture()
@pytest.mark.usefixtures("setup_db")
async def auth_tenant():
    tenant = TenantC300.model_validate(
        {
            "_id": "64bf8629a236cf0019a7b473",
            "binds_permissions": {"pr": "61b06a693b6d6e0019260942", "hg": "61b06eecc950b1001a3a31e8"},
            "department": {"_id": "6266a359af0f82000fcada27", "name": "Бухгалтерский отдел"},
            "email": "tester@roscluster.ru",
            "area": {
                "_id": "61b06eecc950b1001a3a31e6",
                "number": "1",
                "formatted_number": "кв. 1",
            },
            "house": {
                "_id": "61b06eebc950b1001a3a31dd",
                "address": "г Санкт-Петербург, ул Панфилова, д. 15 корп. 8 лит. А",
            },
            "short_name": "Иванов И.И.",
            "full_name": "Иванов Иван Иванович",
            "number": "7839508253182",
            "phone_numbers": [],
        }
    )
    return await tenant.save()


@pytest.fixture()
async def auth_tenant_cookie(auth_tenant: TenantC300):
    token = jwt.encode(
        payload={
            "profile": auth_tenant.number,
            "username": auth_tenant.number,
            "type": 0,
            "is_superuser": False,
        },
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return {"access_token": token}


@pytest.fixture()
async def api_tenant_client(auth_tenant_cookie: dict[str, str]):
    async with LifespanManager(app, startup_timeout=100, shutdown_timeout=100):
        server_name = "http://localhost"
        async with AsyncClient(transport=ASGITransport(app=app), base_url=server_name, cookies=auth_tenant_cookie) as ac:  # type: ignore
            yield ac


@pytest.fixture()
async def api_gateway_client():
    async with LifespanManager(app, startup_timeout=100, shutdown_timeout=100):
        server_name = "http://localhost"
        async with AsyncClient(transport=ASGITransport(app=app), base_url=server_name, headers={"Authorization": settings.SECURITY_TOKEN}) as ac:  # type: ignore
            yield ac


# ------------------- Фикстуры с моками -------------------
@pytest.fixture()
async def mock_c300_api_upsert_storage_docs_out(mocker):

    class MockData(BaseModel):
        warehouse_id: PydanticObjectId = PydanticObjectId()
        warehouse_item_id: PydanticObjectId = PydanticObjectId()
        test_quantity: float = 55
        test_price: int = 999
        test_warehouse_name: str = "Замоканный склад"
        test_warehouse_item_name: str = "Замоканная позиция склада"

    mock_data = MockData()
    mock_return = [
        WarehouseResourcesRS(
            _id=mock_data.warehouse_id,
            name=mock_data.test_warehouse_name,
            items=[ItemWarehouseResourcesRS(_id=mock_data.warehouse_item_id, name=mock_data.test_warehouse_item_name, price=mock_data.test_price, quantity=mock_data.test_quantity)],
        )
    ]
    mocker.patch("client.c300.api.C300API.upsert_storage_docs_out", return_value=mock_return)
    return mock_data


@pytest.fixture()
async def mock_house_get(mocker, auth_tenant: TenantC300, auth_employee: EmployeeC300):
    mock_house = HouseC300.model_validate(
        {
            "_id": auth_tenant.house.id,
            "address": "г Санкт-Петербург, ул Панфилова, д. 15 корп. 8 лит. А",
            "service_binds": [
                {
                    "_id": PydanticObjectId("61b06ed7c950b1001a3a31db"),
                    "provider": auth_employee.provider.id,
                    "business_type": PydanticObjectId("5427dc2bf3b7d44b1ae89b0e"),
                    "start_at": datetime(2000, 1, 1, 0, 0),
                    "end_at": None,
                    "is_public": True,
                    "is_active": True,
                    "group": None,
                },
            ],
            "porches": [{"standpipes": [{"_id": PydanticObjectId("67442c4feb37cdbb3463ab5d")}], "lifts": []}],
            "settings": {"requests_provider": auth_employee.provider.id},
        }
    )
    await mock_house.save()
    mocker.patch("client.c300.models.house.HouseC300.get", return_value=mock_house)
    return mock_house


# ------------------- Фикстуры с созданием моделей -------------------
@pytest.fixture()
async def catalog_items(auth_employee: EmployeeC300, auth_tenant: TenantC300):
    t = datetime.now()
    return [
        await CatalogItem(
            name="test_name_1",
            description="test_description_1",
            code="test_code_1",
            measurement_unit=CatalogMeasurementUnit.PIECE,
            is_available=True,
            is_divisible=False,
            available_from=t,
            group=CatalogItemGroup.ELECTRICS,
            provider_id=auth_employee.provider.id,
            prices=[
                CatalogItemPrice(
                    start_at=t,
                    amount=1000,
                )
            ],
            house_ids={auth_tenant.house.id},
        ).save(),
        await CatalogItem(
            name="test_name_2",
            description="test_description_2",
            code="test_code_2",
            measurement_unit=CatalogMeasurementUnit.PIECE,
            is_available=True,
            is_divisible=True,
            available_from=t,
            group=CatalogItemGroup.PLUMBING,
            provider_id=PydanticObjectId(),
            prices=[
                CatalogItemPrice(
                    start_at=t,
                    amount=1000,
                )
            ],
            house_ids={PydanticObjectId()},
        ).save(),
    ]


@pytest.fixture()
async def requests(auth_employee: EmployeeC300, auth_tenant: TenantC300):
    t = datetime.now()
    auth_employee_dict = auth_employee.model_dump(by_alias=True)
    auth_tenant_dict = auth_tenant.model_dump(by_alias=True)
    execution_start_at = t.replace(hour=0, minute=30, second=0, microsecond=0)
    return [
        await RequestModel(
            _id=PydanticObjectId("672e35893872fa7eba2e3490"),
            _binds=ProviderHouseGroupBinds(
                pr={auth_employee.binds_permissions.pr},
                hg={auth_employee.binds_permissions.hg},
            ),
            _type=RequestType.AREA,
            actions=[ActionRS(start_at=t, end_at=t + timedelta(days=1), _type=ActionRSType.ELECTRICITY)],
            administrative_supervision=True,
            area=AreaRS.model_validate(auth_tenant.area.model_dump(by_alias=True)),
            commerce=CommerceRS(pay_status=RequestPayStatus.NO_CHARGE, catalog_items=[]),
            created_at=t,
            description="test_description_1",
            dispatcher=DispatcherRS.model_validate(auth_employee_dict),
            execution=ExecutionRS(
                desired_start_at=None,
                desired_end_at=None,
                provider=ProviderRS.model_validate(auth_employee.provider.model_dump(by_alias=True)),
                employees=[],
                act=Attachment(files=[], comment=""),
                attachment=Attachment(files=[], comment=""),
                is_partially=False,
                evaluations=[],
                total_rate=0,
            ),
            house=HouseRS.model_validate(auth_tenant.house.model_dump(by_alias=True)),
            housing_supervision=True,
            is_public=False,
            monitoring=MonitoringRS(
                control_messages=[],
                persons_in_charge=[PersonInChargeRS.model_validate({**auth_employee_dict, "_type": PersonInChargeType.DISPATCHER})],
            ),
            number="7837582401630",
            provider=ProviderRS.model_validate(auth_employee.provider.model_dump(by_alias=True)),
            relations=RelationsRS(),
            requester=TenantRequester.model_validate({**auth_tenant_dict, "_type": RequesterType.TENANT}),
            requester_attachment=Attachment(files=[], comment=""),
            resources=ResourcesRS(materials=[], services=[], warehouses=[]),
            source=RequestSource.DISPATCHER,
            status=RequestStatus.ACCEPTED,
            category=RequestCategory.EMERGENCY,
            subcategory=RequestSubcategory.ELECTRICITY,
            tag=RequestTag.CURRENT,
            work_area=RequestWorkArea.AREA,
        ).save(),
        await RequestModel(
            _id=PydanticObjectId("542ab92b4826e960e42bcaef"),
            _binds=ProviderHouseGroupBinds(
                pr={auth_employee.binds_permissions.pr},
                hg={auth_employee.binds_permissions.hg},
            ),
            _type=RequestType.AREA,
            actions=[ActionRS(start_at=t, end_at=t + timedelta(days=1), _type=ActionRSType.ELECTRICITY)],
            administrative_supervision=True,
            area=AreaRS.model_validate(auth_tenant.area.model_dump(by_alias=True)),
            commerce=CommerceRS(pay_status=RequestPayStatus.NO_CHARGE, catalog_items=[]),
            created_at=t,
            description="test_description_1",
            dispatcher=DispatcherRS.model_validate(auth_employee_dict),
            execution=ExecutionRS(
                desired_start_at=None,
                desired_end_at=None,
                start_at=execution_start_at,
                end_at=execution_start_at + timedelta(days=2),
                provider=ProviderRS.model_validate(auth_employee.provider.model_dump(by_alias=True)),
                employees=[EmployeeRS.model_validate(auth_employee_dict)],
                act=Attachment(files=[], comment=""),
                attachment=Attachment(files=[], comment=""),
                is_partially=False,
                evaluations=[],
                total_rate=0,
            ),
            house=HouseRS.model_validate(auth_tenant.house.model_dump(by_alias=True)),
            housing_supervision=True,
            is_public=False,
            monitoring=MonitoringRS(
                control_messages=[],
                persons_in_charge=[PersonInChargeRS.model_validate({**auth_employee_dict, "_type": PersonInChargeType.DISPATCHER})],
            ),
            number="7837582401631",
            provider=ProviderRS.model_validate(auth_employee.provider.model_dump(by_alias=True)),
            relations=RelationsRS(),
            requester=TenantRequester.model_validate({**auth_tenant_dict, "_type": RequesterType.TENANT}),
            requester_attachment=Attachment(files=[], comment=""),
            resources=ResourcesRS(materials=[], services=[], warehouses=[]),
            source=RequestSource.DISPATCHER,
            status=RequestStatus.RUN,
            category=RequestCategory.EMERGENCY,
            subcategory=RequestSubcategory.ELECTRICITY,
            tag=RequestTag.CURRENT,
            work_area=RequestWorkArea.AREA,
        ).save(),
    ]


@pytest.fixture()
async def other_persons(auth_employee: EmployeeC300):
    return [
        await OtherPerson(
            short_name="f1 i. o.",
            full_name="f1 i o",
            _binds=ProviderBinds(pr={auth_employee.provider.id}),
        ).save(),
        await OtherPerson(
            short_name="f2 i.",
            full_name="f2 i",
            email="email@example.com",
            phone_numbers=[
                PhoneNumber(
                    _type=PhoneType.CELL,
                    number="9998887766",
                    add="4321",
                )
            ],
            _binds=ProviderBinds(pr={PydanticObjectId()}),
        ).save(),
    ]


@pytest.fixture()
async def other_providers(auth_employee: EmployeeC300):
    return [
        await OtherProvider(
            name="name_1",
            inn="1111111111111",
            ogrn="111111111111111",
            _binds=ProviderBinds(pr={auth_employee.provider.id}),
        ).save(),
        await OtherProvider(
            name="name_2",
            inn="2222222222222222",
            ogrn="222222222222222",
            _binds=ProviderBinds(pr={PydanticObjectId()}),
        ).save(),
    ]


@pytest.fixture()
async def other_employees(other_providers: list[OtherProvider]):
    return [
        await OtherEmployee(
            short_name="f1 i. o.",
            full_name="f1 i o",
            position_name="pos_name_1",
            provider_id=other_providers[0].id,
            _binds=other_providers[0].binds,
        ).save(),
        await OtherEmployee(
            short_name="f2 i.",
            full_name="f2 i",
            position_name="pos_name_1",
            provider_id=other_providers[1].id,
            _binds=other_providers[1].binds,
            email="email@example.com",
            phone_numbers=[
                PhoneNumber(
                    _type=PhoneType.CELL,
                    number="9998887766",
                    add="4321",
                )
            ],
        ).save(),
    ]


@pytest.fixture()
async def request_templates():
    return [
        await RequestTemplate(
            _id=PydanticObjectId("6746dce7472435f22496fa74"),
            provider_id=PydanticObjectId("61b06a693b6d6e0019260942"),
            name="test_name",
            category=RequestCategory.BUILDING_RENOVATION,
            subcategory=RequestSubcategory.GENERAL_PROPERTY,
            _type=RequestTemplateType.REQUEST,
            body="test_body",
        ).save(),
    ]
