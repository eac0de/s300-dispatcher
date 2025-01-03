from datetime import datetime, timedelta

import aiodocker
import jwt
import pytest
from asgi_lifespan import LifespanManager
from beanie import PydanticObjectId
from client.s300.models.area import AreaS300
from client.s300.models.department import DepartmentS300, SettingsDepartmentS300
from client.s300.models.employee import EmployeeS300
from client.s300.models.house import (
    HouseS300,
    PorchHS300S,
    ServiceBindHS300S,
    SettingsHS300S,
    StandpipeHS300S,
)
from client.s300.models.provider import ProviderS300
from client.s300.models.tenant import TenantS300
from config import settings
from database import init_db
from httpx import ASGITransport, AsyncClient
from main import app
from models.appeal.appeal import Appeal
from models.appeal.constants import AppealSource, AppealStatus, AppealType
from models.appeal.embs.appealer import Appealer
from models.appeal.embs.employee import (
    DepartmentAS,
    DispatcherAS,
    EmployeeAS,
    ProviderAS,
)
from models.appeal.embs.observers import ObserversAS
from models.appeal.embs.relations import RelationsAS
from models.appeal_category.appeal_category import AppealCategory
from models.appeal_comment.appeal_comment import AppealComment, EmployeeAppealComment
from models.base.binds import DepartmentBinds, ProviderBinds, ProviderHouseGroupBinds
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
from models.request.embs.employee import DispatcherRS, EmployeeRS, ProviderRS
from models.request.embs.execution import ExecutionRS
from models.request.embs.house import HouseRS
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
from pydantic import BaseModel
from pytest_mock import MockerFixture
from services.appeal.appeal_service import AppealService


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
        TenantS300,
        EmployeeS300,
        HouseS300,
        AreaS300,
        ProviderS300,
        RequestHistory,
        CatalogItem,
        RequestTemplate,
        OtherPerson,
        OtherEmployee,
        OtherProvider,
        Appeal,
        AppealCategory,
    ]
    for model in models:
        await model.get_motor_collection().drop()
        await model.get_motor_collection().drop_indexes()


@pytest.fixture()
@pytest.mark.usefixtures("setup_db")
async def auth_employee():
    worker = EmployeeS300.model_validate(
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
            "appeal_access_level": "basic",
        }
    )
    return await worker.save()


@pytest.fixture()
async def auth_employee_cookie(auth_employee: EmployeeS300):
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
    tenant = TenantS300.model_validate(
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
async def auth_tenant_cookie(auth_tenant: TenantS300):
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
async def mock_s300_api_upsert_storage_docs_out(mocker):

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
    mocker.patch("client.s300.api.S300API.upsert_storage_docs_out", return_value=mock_return)
    return mock_data


@pytest.fixture()
async def mock_create_receipt_for_paid_request(mocker):
    mocker.patch("client.s300.api.S300API.create_receipt_for_paid_request", return_value=None)


@pytest.fixture()
async def mock_s300_api_get_house_group_ids(mocker) -> set[PydanticObjectId]:
    hg_id = PydanticObjectId()
    mocker.patch("client.s300.api.S300API.get_house_group_ids", return_value=set([hg_id]))
    return set([hg_id])


@pytest.fixture()
async def mock_s300_api_get_allowed_worker_ids(mocker: MockerFixture):
    def side_effect(**kwargs):
        return set(kwargs["worker_ids"])

    mocker.patch("client.s300.api.S300API.get_allowed_worker_ids", side_effect=side_effect)


@pytest.fixture()
async def mock_s300_api_get_allowed_house_ids(mocker: MockerFixture):
    def side_effect(**kwargs):
        return kwargs["house_ids"]

    mocker.patch("client.s300.api.S300API.get_allowed_house_ids", side_effect=side_effect)


# ------------------- Фикстуры с созданием моделей -------------------
@pytest.fixture()
async def catalog_items(auth_employee: EmployeeS300, auth_tenant: TenantS300):
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
async def requests(auth_employee: EmployeeS300, auth_tenant: TenantS300):
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
                rates=[],
                average_rating=0,
            ),
            house=HouseRS.model_validate(auth_tenant.house.model_dump(by_alias=True)),
            housing_supervision=True,
            is_public=False,
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
                rates=[],
                average_rating=0,
            ),
            house=HouseRS.model_validate(auth_tenant.house.model_dump(by_alias=True)),
            housing_supervision=True,
            is_public=False,
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
async def other_persons(auth_employee: EmployeeS300):
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
async def other_providers(auth_employee: EmployeeS300):
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
async def request_templates(auth_employee: EmployeeS300) -> list[RequestTemplate]:
    return [
        await RequestTemplate(
            _id=PydanticObjectId("6746dce7472435f22496fa74"),
            provider_id=auth_employee.provider.id,
            name="test_name",
            category=RequestCategory.BUILDING_RENOVATION,
            subcategory=RequestSubcategory.GENERAL_PROPERTY,
            _type=RequestTemplateType.REQUEST,
            body="test_body",
        ).save(),
    ]


@pytest.fixture()
async def houses(auth_tenant: TenantS300, auth_employee: EmployeeS300) -> list[HouseS300]:
    return [
        await HouseS300(
            _id=auth_tenant.house.id,
            address="г Санкт-Петербург, ул Панфилова, д. 15 корп. 8 лит. А",
            service_binds=[
                ServiceBindHS300S(
                    _id=PydanticObjectId("61b06ed7c950b1001a3a31db"),
                    provider=auth_employee.provider.id,
                    business_type=PydanticObjectId("5427dc2bf3b7d44b1ae89b0e"),
                    start_at=datetime(2000, 1, 1, 0, 0),
                    end_at=None,
                    is_public=True,
                    is_active=True,
                    group=None,
                ),
            ],
            porches=[
                PorchHS300S(
                    standpipes=[StandpipeHS300S(_id=PydanticObjectId("67442c4feb37cdbb3463ab5d"))],
                    lifts=[],
                ),
            ],
            settings=SettingsHS300S(requests_provider=auth_employee.provider.id),
        ).save(),
    ]


@pytest.fixture()
async def areas(auth_tenant: TenantS300) -> list[AreaS300]:
    return [
        await AreaS300(
            _id=auth_tenant.area.id,
            number=auth_tenant.area.number,
            formatted_number=auth_tenant.area.formatted_number,
        ).save(),
    ]


@pytest.fixture()
async def providers(auth_employee: EmployeeS300) -> list[ProviderS300]:
    return [
        await ProviderS300(
            _id=auth_employee.provider.id,
            name=auth_employee.provider.name,
        ).save(),
    ]


@pytest.fixture()
async def departments(auth_employee: EmployeeS300) -> list[DepartmentS300]:
    return [
        await DepartmentS300(
            _id=auth_employee.department.id,
            name=auth_employee.department.name,
            settings=SettingsDepartmentS300(is_accepting_appeals=True),
            provider_id=auth_employee.provider.id,
        ).save(),
    ]


@pytest.fixture()
async def appeal_categories(auth_employee: EmployeeS300) -> list[AppealCategory]:
    return [
        await AppealCategory(
            _id=PydanticObjectId("6746dce7472435f22496fa74"),
            provider_id=auth_employee.provider.id,
            name="test_name",
            description="test_description",
        ).save(),
    ]


@pytest.fixture()
async def appeals(auth_employee: EmployeeS300, auth_tenant: TenantS300) -> list[Appeal]:
    t = datetime.now()
    auth_employee_dict = auth_employee.model_dump(by_alias=True)
    return [
        await Appeal(
            _id=PydanticObjectId(),
            provider=ProviderAS.model_validate(auth_employee.provider.model_dump(by_alias=True)),
            subject="test_subject_1",
            description="test_description_1",
            created_at=t,
            dispatcher=DispatcherAS.model_validate(auth_employee_dict),
            appealer=Appealer.model_validate(auth_tenant.model_dump(by_alias=True)),
            executor=None,
            relations=RelationsAS(),
            status=AppealStatus.NEW,
            _type=AppealType.ACKNOWLEDGEMENT,
            observers=ObserversAS(departments=[DepartmentAS(_id=auth_employee.department.id, name=auth_employee.department.name)], employees=[]),
            _binds=DepartmentBinds(dp={auth_employee.department.id}),
            category_ids=set(),
            number=await AppealService._generate_number(auth_employee.provider.id, t),
            source=AppealSource.DISPATCHER,
            deadline_at=t + timedelta(days=1),
        ).save(),
        await Appeal(
            _id=PydanticObjectId(),
            provider=ProviderAS.model_validate(auth_employee.provider.model_dump(by_alias=True)),
            subject="test_subject_2",
            description="test_description_2",
            created_at=t,
            dispatcher=DispatcherAS.model_validate(auth_employee_dict),
            appealer=Appealer.model_validate(auth_tenant.model_dump(by_alias=True)),
            executor=EmployeeAS.model_validate(auth_employee.model_dump(by_alias=True)),
            relations=RelationsAS(),
            status=AppealStatus.RUN,
            _type=AppealType.CLAIM,
            observers=ObserversAS(departments=[DepartmentAS(_id=auth_employee.department.id, name=auth_employee.department.name)], employees=[]),
            _binds=DepartmentBinds(dp={auth_employee.department.id}),
            category_ids=set(),
            number=await AppealService._generate_number(auth_employee.provider.id, t),
            source=AppealSource.DISPATCHER,
            deadline_at=t + timedelta(days=1),
        ).save(),
    ]


@pytest.fixture()
async def appeal_comments(auth_employee: EmployeeS300, appeals: list[Appeal]) -> list[AppealComment]:
    t = datetime.now()
    auth_employee_dict = auth_employee.model_dump(by_alias=True)
    auth_employee_dict["position_name"] = auth_employee.position.name
    appeal = appeals[0]
    return [
        await AppealComment(
            _id=PydanticObjectId(),
            appeal_id=appeal.id,
            created_at=t,
            text="test_text_1",
            employee=EmployeeAppealComment.model_validate(auth_employee_dict),
            files=[],
            read_by={auth_employee.id},
        ).save(),
        await AppealComment(
            _id=PydanticObjectId(),
            appeal_id=appeal.id,
            created_at=t,
            text="test_text_2",
            employee=EmployeeAppealComment.model_validate(auth_employee_dict),
            read_by={auth_employee.id},
        ).save(),
    ]
