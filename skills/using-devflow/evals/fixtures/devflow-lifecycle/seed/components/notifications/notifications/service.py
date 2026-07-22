from dataclasses import dataclass
from typing import Protocol


class NotificationError(Exception):
    """Base class for expected notification delivery errors."""


class TransientTransportError(NotificationError):
    """The transport may succeed when called again."""


class PermanentTransportError(NotificationError):
    """The transport cannot deliver this notification."""


@dataclass(frozen=True)
class Notification:
    recipient: str
    body: str


class NotificationTransport(Protocol):
    def send(self, notification: Notification) -> None:
        """Deliver one notification or raise a transport error."""


class NotificationService:
    def __init__(self, transport: NotificationTransport) -> None:
        self._transport = transport

    def send(self, notification: Notification) -> None:
        self._transport.send(notification)
