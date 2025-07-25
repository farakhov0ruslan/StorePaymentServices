
## Краткое описание проекта

Проект реализует два микросервиса для интернет-магазина:

* **Order Service** — отвечает за создание заказов и отслеживание их статусов.
* **Payments Service** — отвечает за управление пользователями-счётами: создание счёта, пополнение, списание средств.

Все внешние запросы проходят через **API Gateway**, которое маршрутизирует HTTP-запросы к нужному бэкенду.

## За что отвечает каждый сервис

* **API Gateway**

  * Принимает HTTP-запросы от клиента.
  * Перенаправляет их в Orders Service или Payments Service.
  * Можно настроить зависимость «ожидать» запуска RabbitMQ / баз данных перед открытием порта (см. `wait-for-it.sh`).

* **Order Service**

  * `POST /orders` — создание нового заказа.
  * `GET  /orders` — список всех заказов.
  * `GET  /orders/{id}` — статус конкретного заказа.
  * Внутри при создании заказа в рамках **одной транзакции** сохраняет запись в таблице `orders` и одновременно пишет событие `order_created` в свою таблицу `outbox`.

* **Payments Service**

  * `POST   /accounts?user_id=…`             — создать счёт.
  * `POST   /accounts/{user_id}/deposit`     — пополнить баланс.
  * `GET    /accounts/{user_id}/balance`     — посмотреть баланс.
  * Фоновая задача (consumer) читает из очереди `order_created`, выполняет списание через `ProcessPayment` (**exactly-once**) и в той же транзакции пишет в таблицы:

    1. `inbox` — пометка о пришедшем `message_id`
    2. `accounts` — обновлённый баланс
    3. `outbox`   — событие `payment_success` или `payment_failed`

## Основные пользовательские сценарии

### 1. Создание заказа и автоплатёж

1. Клиент → API Gateway: `POST /orders { user_id, amount, description }`.
2. Order Service в **транзакции**:

   * сохраняет новый заказ со статусом `PENDING`,
   * пишет в `outbox` запись `order_created`.
3. Фоновая задача-outbox в Order Service публикует сообщения `order_created` в RabbitMQ.
4. Payments Service (consumer) забирает `order_created`, проверяет аккаунт, списывает деньги и в **той же транзакции**:

   * помечает `inbox` (idempotency-ключ),
   * обновляет `accounts.balance`,
   * пишет в `outbox` событие `payment_success` или `payment_failed`.
5. Фоновая задача-outbox в Payments Service публикует соответствующее событие.
6. Order Service (consumer) получает `payment_success/payment_failed` и обновляет статус заказа (`PAID` или `FAILED`).

### 2. Работа со счётом

* `Создать счёт`
* `Пополнить счёт`
* `Посмотреть баланс`

## Применение паттернов

* **Transactional Outbox** в Order Service

  * При цепочке «запись заказа + запись в outbox» используется одна БД-транзакция.
* **Transactional Inbox + Outbox** в Payments Service

  * Inbox предотвращает повторную обработку одного и того же сообщения.
  * Outbox гарантирует, что событие успешно попадёт в очередь после изменения баланса.
* **Exactly-once semantics** при списании

  * За счёт комбинации уникального `message_id` в inbox и атомарных операций в одной транзакции.

## Использование брокера сообщений

* RabbitMQ как центральный шина обмена.
* Две основные очереди:

  * `order_created`  — от Order → Payments
  * `payment_success` / `payment_failed` — от Payments → Order
* Все publish/consume выполняются через `aio_pika.connect_robust` и `default_exchange`.
* 
## Интеграция gRPC

Помимо HTTP/REST API, в проекте реализовано **внутреннее взаимодействие по gRPC** между сервисами:

- **gRPC‑роутер API Gateway** (`/grpc/orders`):
  - `POST /grpc/orders/` — создание заказа через gRPC.
  - `GET  /grpc/orders/` — получение списка заказов через gRPC.
  - `GET  /grpc/orders/{id}` — получение заказа по ID через gRPC.

- **gRPC‑сервер Order Service**:
  - Сервис `OrderService` с методами:
    - `CreateOrder(CreateOrderRequest) returns (Order)`
    - `GetOrder(GetOrderRequest) returns (Order)`
    - `ListOrders(Empty) returns (ListOrdersResponse)`
  - Запускается на порту `50051` параллельно с HTTP API.
- **Proto‑файлы**:
  - `orders_service/protos/order_service.proto`
  - Используйте `protoc` и `grpc_tools` для генерации Python‑stub’ов (`*_pb2.py`, `*_pb2_grpc.py`).
- **Конфигурация**:
  - В API Gateway включается через переменные окружения:
    ```bash
    ORDER_SERVICE_GRPC=order-service:50051
    ```

## Запуск всех сервисов

1. В корне репозитория лежит `docker-compose.yml`.
2. Для гарантии того, что сервисы не стартуют до готовности БД и RabbitMQ, в entrypoint каждого сервиса используется `wait-for-it.sh`:

   ```bash
   ./wait-for-it.sh rabbitmq:5672 -- \
    -- uvicorn payments_service.main:app ...
   ```

   Он ждёт, пока указанные хосты/порты откроются.
3. По умолчанию в `docker-compose.yml` закомментированы порты API Gateway (чтобы защитить внутреннюю сеть от ранних запросов), при желании их можно раскомментировать.
4. Сборка и запуск:

   ```bash
   docker-compose up --build
   ```
5. затем перейдите по адресу: http://localhost:8000/docs
Протестировать основную логику можно так.
- Создать paymant баланс
- Начать создавать заказы с user_id, связанный с paymant баланс
- В зависимости от условий заказы будут отклонены или оплачены(например если нет денег, заказ сначала будет в обработке, а немного позже станет failed)
- Действия с заказами также можно выполнить и через gRPC

## Тестирование

* У каждого сервиса есть **pytest**-суппорт и покрытие > 65%.
* Для всех публичных API подготовлена коллекция  **Swagger UI**, демонстрирующая:

  * создание и просмотр заказов,
  * создание/пополнение счёта и запрос баланса.
  
  
   ### Через docker-compose CLI:
- Зайти в контейнер Payments Service:
```bash
- docker-compose exec payments_service sh
```

 - Перейти в папку сервиса и запустить тесты:
```bash
cd payment_service
pytest --maxfail=1 --disable-warnings -q
```
-  Зайти в контейнер Order Service:
```bash
docker-compose exec order_service sh
```
 - Перейти и запустить тесты:
```bash
cd orders_service
pytest --maxfail=1 --disable-warnings -q
```

### Через Docker Desktop (UI):
 1. Выберите контейнер payments_service или order_service и откройте Exec/Terminal.
 2. Выполните:
```bash
cd <название_сервиса>
pytest --maxfail=1 --disable-warnings -q \
       --cov=<название_сервиса> --cov-report=term-missing --cov-report=html
```

## Архитектурные подходы

* **Чистая архитектура** :

  * `domain` — бизнес-логика,
  * `application` — use-cases,
  * `infrastructure` — репозитории, модели, коннекты, брокер, миграции, логгинг,
  * `presentation` — FastAPI-роуты, схемы.
* **wait-for-it.sh** нужен, чтобы при старте контейнера дождаться готовности зависимостей (RabbitMQ, Postgres), иначе consumer или миграции упадут.

## Использованные технологии, фреймворки и паттерны

* **Python 3.11**, **FastAPI**, **SQLAlchemy**, **Alembic**, **pytest**
* **RabbitMQ** + **aio\_pika**
* **Docker**, **docker-compose**, **wait-for-it.sh**
* Паттерны:

  * Transactional Outbox (Order Service)
  * Transactional Inbox + Outbox (Payments Service)
  * Exactly-once semantics при списании
  * API Gateway для маршрутизации

