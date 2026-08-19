from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    order_id: str
    status: OrderStatus


class OrderService:
    def cancel(self, order: Order) -> Order:
        if order.status not in {OrderStatus.CREATED, OrderStatus.PAID}:
            raise ValueError("order cannot be cancelled in current status")
        order.status = OrderStatus.CANCELLED
        return order
