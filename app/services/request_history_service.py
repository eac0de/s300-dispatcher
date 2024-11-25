"""
 Модуль с сервисом для работы с историей изменения заявок
"""

from client.c300.api import C300API
from client.c300.models.employee import EmployeeC300
from models.request.request import RequestModel
from models.request_history.request_history import RequestHistory
from schemes.request_history import UpdateRequestHistoryRScheme


class RequestHistoryService:
    """
    Сервис для работы с историей изменения заявок
    """

    def __init__(
        self,
        employee: EmployeeC300,
        request: RequestModel,
    ):
        """
        Инициализация сервиса

        Args:
            employee (EmployeeC300): Сотрудник работающий с историей заявки
            request (RequestModel): Заявка для отображения истории
        """
        self.employee = employee
        self.request = request

    async def get_request_history(self) -> list[UpdateRequestHistoryRScheme]:
        """
        Получение истории изменения заявки

        Returns:
            list[UpdateRequestHistoryRScheme]: Список изменений заявки
        """
        request_history = await RequestHistory.find_one({"request_id": self.request.id})
        if not request_history:
            return []
        allowed_worker_ids = await C300API.get_allowed_worker_ids(
            employee_number=self.employee.number,
            worker_ids=[ch.user.id for ch in request_history.updates],
        )
        updates: list[UpdateRequestHistoryRScheme] = []
        for update in request_history.updates:
            ch = UpdateRequestHistoryRScheme.model_validate(update.model_dump(by_alias=True))
            if update.user.id not in allowed_worker_ids and update.user.id != self.request.requester.id:
                ch.user = None
            updates.append(ch)
        return updates
