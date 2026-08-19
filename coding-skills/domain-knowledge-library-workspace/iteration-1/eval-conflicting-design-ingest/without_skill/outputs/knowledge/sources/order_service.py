from enum import Enum


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


def can_cancel(status: OrderStatus) -> bool:
    return status in {OrderStatus.CREATED, OrderStatus.PAID}
