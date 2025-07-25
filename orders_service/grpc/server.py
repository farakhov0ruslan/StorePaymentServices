import grpc
from grpc import aio

from orders_service.grpc import order_service_pb2, order_service_pb2_grpc
from orders_service.application.schemas import OrderCreate
from orders_service.application.use_cases import (
    CreateOrderUseCase,
    GetOrderUseCase,
    ListOrdersUseCase
)
from orders_service.infrastructure.repository import (
    SQLAlchemyOrderRepository,
    SQLAlchemyOutboxRepository
)


class OrderServiceServicer(order_service_pb2_grpc.OrderServiceServicer):
    def __init__(self):
        # инициализируем репозитории один раз при старте сервиса
        self._order_repo = SQLAlchemyOrderRepository()
        self._outbox_repo = SQLAlchemyOutboxRepository()

    async def CreateOrder(self, request, context):
        # собираем Pydantic‑DTO из gRPC‑запроса
        dto = OrderCreate(
            user_id=request.user_id,
            amount=request.amount,
            description=request.description,
        )
        # вызываем use-case точно так же, как в REST‑эндоинте
        use_case = CreateOrderUseCase(self._order_repo, self._outbox_repo)
        order_out = await use_case.execute(dto)

        # возвращаем gRPC‑ответ
        return order_service_pb2.Order(
            order_id=order_out.order_id,
            user_id=order_out.user_id,
            amount=order_out.amount,
            description=order_out.description,
            status=order_out.status,
        )

    async def GetOrder(self, request, context):
        use_case = GetOrderUseCase(self._order_repo)
        order_out = await use_case.execute(request.order_id)
        if not order_out:
            # если не найден — возвращаем gRPC‑статус NOT_FOUND
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Order not found")
            return order_service_pb2.Order()  # пустой объект
        return order_service_pb2.Order(
            order_id=order_out.order_id,
            user_id=order_out.user_id,
            amount=order_out.amount,
            description=order_out.description,
            status=order_out.status,
        )

    async def ListOrders(self, request, context):
        use_case = ListOrdersUseCase(self._order_repo)
        orders = await use_case.execute()
        return order_service_pb2.ListOrdersResponse(
            orders=[
                order_service_pb2.Order(
                    order_id=o.order_id,
                    user_id=o.user_id,
                    amount=o.amount,
                    description=o.description,
                    status=o.status,
                )
                for o in orders
            ]
        )


async def serve_grpc():
    """
    Запускает асинхронный gRPC‑сервер на порту 50051
    вместе с FastAPI в том же event loop.
    """
    server = aio.server()
    order_service_pb2_grpc.add_OrderServiceServicer_to_server(
        OrderServiceServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    await server.start()
    return server
