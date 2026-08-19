import pytest

from src.order_service import Order, OrderService, OrderStatus


def test_paid_order_can_be_cancelled():
    order = Order("O-1", OrderStatus.PAID)
    assert OrderService().cancel(order).status == OrderStatus.CANCELLED


def test_shipped_order_cannot_be_cancelled():
    order = Order("O-2", OrderStatus.SHIPPED)
    with pytest.raises(ValueError):
        OrderService().cancel(order)
