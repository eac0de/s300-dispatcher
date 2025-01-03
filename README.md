# Документация к сервису dispatcher

_Сервис для работы с заявками, каталогом услуг и пока все._

## [API](./app/api)

API сервиса можно посмотреть запустив сервер(либо уже поднятый сервер) и перейти по адресу `/api/docs/`.

### [Аутентификация и авторизация внутри сервиса](./app/api/dependencies/auth.py)

Сделана посредством _зависимостей(dependency)_. Проверяется токен, после достается идентификаторы пользователя и делается запрос на получение его данных.

## [Периодические задачи Celery](./app/celery_app.py)

Отсутствуют

## [Модели](./app/models)

- [**Request** (**RequestModel**)](./app/models/request) - модель заявки.

- [**ArchivedRequest** (**ArchivedRequestModel**)](./app/models/request) - модель заархивированной заявки. При удалении заявки, создается заархивированная с возможностью восстановления. Раз в некоторое время запускается периодическая задача для удаления заархивированных заявок.

- [**RequestHistory**](./app/models/request_history) - модель истории заявки. Для отслеживания изменений связанных с
  заявкой.

- [**RequestTemplate**](./app/models/request_template) - модель шаблона заявок. Нужна для предзаполнения тела заявок, описания работ, и причин отказа от заявки. Также служит фильтром для заявок созданных с помощью шаблона.

- [**CatalogItem**](./app/models/catalog_item) - модель позиции каталога. Необходима для работы с каталогами реализуемых
  материалов и услуг.

- [**OtherEmployee, OtherPerson, OtherProvider**](./app/models/other) - модели сторонних лиц, сотрудников и организаций.
  Нужны для работы с неизвестными субъектами.

## [Взаимодействие с другими сервисами](./app/client)

### [С300](./app/client/s300)

Реализован [клиент](./app/client/s300/client.py) для взаимодействия с основной системой S300 и
уже [готовые запросы](./app/client/s300/api.py).

Для удобства работы с моделями из S300 разработаны [модели](./app/client/s300/models) которые наследуются от
DocumentCache.

## [Тестирование](./app/tests)

Созданы тесты, работающие непосредственно с _api_. По мере необходимости добавляются новые кейсы для тестирования.

Для тестирования необходимо перейти в каталог app `cd app` и выполнить `pytest`(Или просто в корневой папке выполнить `make test`).
