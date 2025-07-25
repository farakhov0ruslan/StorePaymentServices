from fastapi import FastAPI
from api_gateway.routers.orders import router as orders_router
from api_gateway.routers.payments import router as payments_router
from api_gateway.routers.grpc_orders import router as grpc_router

app = FastAPI(
    title="API Gateway",
    description="Aggregates Orders и Payments микросервисы",
)

app.include_router(orders_router, prefix="/orders", tags=["orders"])
app.include_router(payments_router, prefix="/payments", tags=["payments"])
app.include_router(grpc_router, prefix="/grpc/orders", tags=["grpc-orders"])
