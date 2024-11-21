import aiodocker
import jwt
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from config import settings
from database import init_db
from main import app
from models.cache.area import AreaCache
from models.cache.employee import EmployeeCache
from models.cache.house import HouseCache
from models.cache.provider import ProviderCache
from models.cache.tenant import TenantCache
from models.catalog_item.catalog_item import CatalogItem
from models.other.other_employee import OtherEmployee
from models.other.other_person import OtherPerson
from models.other.other_provider import OtherProvider
from models.request.archived_request import ArchivedRequestModel
from models.request.request import RequestModel
from models.request_history.request_history import RequestHistory
from models.request_template.request_template import RequestTemplate


@pytest.fixture(scope="session", autouse=True)
def check_mode():
    if settings.MODE != "TEST":
        raise PermissionError("Для проведения тестов параметр MODE должен быть равен TEST")


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
        TenantCache,
        EmployeeCache,
        HouseCache,
        AreaCache,
        ProviderCache,
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
async def auth_employee(setup_db: None):
    _ = setup_db
    worker = EmployeeCache.model_validate(
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
async def auth_employee_cookie(auth_employee: EmployeeCache):
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
async def auth_tenant(setup_db: None):
    _ = setup_db
    tenant = TenantCache.model_validate(
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
