import pytest
from beanie import PydanticObjectId
from httpx import AsyncClient
from starlette import status

from models.base.binds import ProviderBinds
from models.cache.employee import EmployeeCache
from models.extra.phone_number import PhoneNumber, PhoneType
from models.other.other_employee import OtherEmployee
from models.other.other_person import OtherPerson
from models.other.other_provider import OtherProvider
from utils.json_encoders import ObjectIdEncoder


@pytest.fixture()
async def other_persons(auth_employee: EmployeeCache):
    return [
        await OtherPerson(
            short_name="short_`1",
            full_name="full_1",
            _binds=ProviderBinds(pr={auth_employee.provider.id}),
        ).save(),
        await OtherPerson(
            short_name="short_2",
            full_name="full_2",
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
async def other_providers(auth_employee: EmployeeCache):
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
            short_name="short_`1",
            full_name="full_1",
            position_name="pos_name_1",
            provider_id=other_providers[0].id,
            _binds=other_providers[0].binds,
        ).save(),
        await OtherEmployee(
            short_name="short_`1",
            full_name="full_1",
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


class TestOtherRouter:

    async def test_get_other_persons_list(self, api_employee_client: AsyncClient, other_persons: list[OtherPerson]):
        resp = await api_employee_client.get("/dispatcher/other/persons")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(other_persons[0].id)

    async def test_create_other_person(self, api_employee_client: AsyncClient):
        test_short_name = "test_short_name"
        test_phone_numbers = [{"_type": "cell", "number": "9944022019", "add": "4321"}]
        data = {
            "short_name": test_short_name,
            "full_name": "test_full_name",
            "phone_numbers": test_phone_numbers,
            "email": "user@example.com",
        }
        resp = await api_employee_client.post("/dispatcher/other/persons", json=data)
        assert resp.status_code == status.HTTP_201_CREATED
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        other_person = await OtherPerson.get(PydanticObjectId(resp_json["_id"]))
        assert other_person is not None
        assert other_person.short_name == test_short_name
        assert len(other_person.phone_numbers) == len(test_phone_numbers)

    async def test_update_other_person(self, api_employee_client: AsyncClient, other_persons: list[OtherPerson]):
        other_person = other_persons[0]
        test_short_name = "test_short_name"
        test_phone_numbers = [{"_type": "cell", "number": "9944022019", "add": "4321"}]
        data = {
            "short_name": test_short_name,
            "full_name": "test_full_name",
            "phone_numbers": test_phone_numbers,
            "email": "user@example.com",
        }
        resp = await api_employee_client.put(f"/dispatcher/other/persons/{other_person.id}", json=data)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)

        await other_person.sync()
        assert other_person.short_name == test_short_name
        assert len(other_person.phone_numbers) == len(test_phone_numbers)

        other_person = other_persons[1]
        resp = await api_employee_client.put(f"/dispatcher/other/persons/{other_person.id}", json=data)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_other_person(self, api_employee_client: AsyncClient, other_persons: list[OtherPerson]):
        other_person = other_persons[0]

        resp = await api_employee_client.delete(f"/dispatcher/other/persons/{other_person.id}")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert await OtherPerson.get(other_person.id) is None

        other_person = other_persons[1]
        resp = await api_employee_client.delete(f"/dispatcher/other/persons/{other_person.id}")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_other_employees_list(self, api_employee_client: AsyncClient, other_employees: list[OtherEmployee]):
        resp = await api_employee_client.get("/dispatcher/other/employees")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(other_employees[0].id)

    async def test_create_other_employee(self, api_employee_client: AsyncClient, other_providers: list[OtherProvider]):
        other_provider = other_providers[0]
        test_short_name = "test_short_name"
        test_phone_numbers = [{"_type": "cell", "number": "9944022019", "add": "4321"}]
        data = {
            "short_name": test_short_name,
            "full_name": "test_full_name",
            "phone_numbers": test_phone_numbers,
            "email": "user@example.com",
            "provider_id": other_provider.id,
            "position_name": "test_position_name",
        }
        resp = await api_employee_client.post("/dispatcher/other/employees", json=ObjectIdEncoder.normalize(data))
        assert resp.status_code == status.HTTP_201_CREATED
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        other_employee = await OtherEmployee.get(PydanticObjectId(resp_json["_id"]))
        assert other_employee is not None
        assert other_employee.short_name == test_short_name
        assert len(other_employee.phone_numbers) == len(test_phone_numbers)

        other_provider = other_providers[1]
        data["provider_id"] = str(other_provider.id)
        resp = await api_employee_client.post("/dispatcher/other/employees", json=data)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_other_employee(self, api_employee_client: AsyncClient, other_employees: list[OtherEmployee]):
        other_employee = other_employees[0]
        test_short_name = "test_short_name"
        test_phone_numbers = [{"_type": "cell", "number": "9944022019", "add": "4321"}]
        data = {
            "short_name": test_short_name,
            "full_name": "test_full_name",
            "phone_numbers": test_phone_numbers,
            "email": "user@example.com",
            "position_name": "test_position_name",
            "provider_id": other_employee.provider_id,
        }
        resp = await api_employee_client.put(f"/dispatcher/other/employees/{other_employee.id}", json=ObjectIdEncoder.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await other_employee.sync()
        assert other_employee.short_name == test_short_name
        assert len(other_employee.phone_numbers) == len(test_phone_numbers)

        other_employee = other_employees[1]
        resp = await api_employee_client.put(f"/dispatcher/other/employees/{other_employee.id}", json=ObjectIdEncoder.normalize(data))
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_other_employee(self, api_employee_client: AsyncClient, other_employees: list[OtherEmployee]):
        other_employee = other_employees[0]
        resp = await api_employee_client.delete(f"/dispatcher/other/employees/{other_employee.id}")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert await OtherPerson.get(other_employee.id) is None

        other_employee = other_employees[1]
        resp = await api_employee_client.delete(f"/dispatcher/other/employees/{other_employee.id}")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_other_providers_list(self, api_employee_client: AsyncClient, other_providers: list[OtherProvider]):
        resp = await api_employee_client.get("/dispatcher/other/providers")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        assert resp_json[0]["_id"] == str(other_providers[0].id)

    async def test_create_other_provider(self, api_employee_client: AsyncClient):
        test_name = "test_name"
        data = {
            "name": test_name,
            "inn": "33333333333333",
            "ogrn": "33333333333333",
        }
        resp = await api_employee_client.post("/dispatcher/other/providers", json=data)
        assert resp.status_code == status.HTTP_201_CREATED
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        other_provider = await OtherProvider.get(PydanticObjectId(resp_json["_id"]))
        assert other_provider is not None
        assert other_provider.name == test_name

    async def test_update_other_provider(self, api_employee_client: AsyncClient, other_providers: list[OtherProvider]):
        other_provider = other_providers[0]
        test_name = "test_name"
        data = {
            "name": test_name,
            "inn": "33333333333333",
            "ogrn": "33333333333333",
        }
        resp = await api_employee_client.put(f"/dispatcher/other/providers/{other_provider.id}", json=data)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await other_provider.sync()
        assert other_provider.name == test_name

        other_provider = other_providers[1]
        resp = await api_employee_client.put(f"/dispatcher/other/providers/{other_provider.id}", json=data)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_other_provider(self, api_employee_client: AsyncClient, other_providers: list[OtherProvider]):
        other_provider = other_providers[0]
        resp = await api_employee_client.delete(f"/dispatcher/other/providers/{other_provider.id}")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert await OtherProvider.get(other_provider.id) is None

        other_provider = other_providers[1]
        resp = await api_employee_client.delete(f"/dispatcher/other/providers/{other_provider.id}")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
