from datetime import datetime

import pytest
from client.s300.models.employee import EmployeeS300
from httpx import AsyncClient
from models.request.request import RequestModel
from starlette import status


class TestEmployeeScheduleRouter:

    @pytest.mark.usefixtures("requests", "mock_s300_api_get_allowed_worker_ids")
    async def test_get_request_employee_weekly_schedules(self, api_employee_client: AsyncClient, auth_employee: EmployeeS300):
        resp = await api_employee_client.get("/dispatcher/employee_schedules/weekly/", params={"start_at": datetime.now().isoformat(), "employee_ids": [str(auth_employee.id)]})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        schedule = resp_json[0]
        assert schedule["employee_id"] == str(auth_employee.id)
        assert len(schedule["workload"]) == 7
        assert schedule["workload"] == [1, 1, 1, 0, 0, 0, 0]

    @pytest.mark.usefixtures("mock_s300_api_get_allowed_worker_ids")
    async def test_get_request_employee_daily_schedules(self, api_employee_client: AsyncClient, auth_employee: EmployeeS300, requests: list[RequestModel]):
        resp = await api_employee_client.get("/dispatcher/employee_schedules/daily/", params={"start_at": datetime.now().isoformat(), "employee_ids": [str(auth_employee.id)]})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1
        schedule = resp_json[0]
        assert schedule["employee_id"] == str(auth_employee.id)
        assert len(schedule["workload"]) == 96
        request = requests[1]
        for i in range(2):
            assert schedule["workload"][i] == []
        for i in range(2, 96):
            assert schedule["workload"][i][0] == request.number
