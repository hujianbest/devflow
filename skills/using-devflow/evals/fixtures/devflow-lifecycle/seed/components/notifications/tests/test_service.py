import unittest

from notifications import (
    Notification,
    NotificationService,
    PermanentTransportError,
    TransientTransportError,
)


class RecordingTransport:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.notifications: list[Notification] = []

    def send(self, notification: Notification) -> None:
        self.notifications.append(notification)
        if self.error is not None:
            raise self.error


class NotificationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.notification = Notification("ops@example.test", "build complete")

    def test_success_delegates_once(self) -> None:
        transport = RecordingTransport()

        result = NotificationService(transport).send(self.notification)

        self.assertIsNone(result)
        self.assertEqual(transport.notifications, [self.notification])

    def test_transient_error_propagates_unchanged(self) -> None:
        error = TransientTransportError("temporarily unavailable")
        transport = RecordingTransport(error)

        with self.assertRaises(TransientTransportError) as raised:
            NotificationService(transport).send(self.notification)

        self.assertIs(raised.exception, error)
        self.assertEqual(transport.notifications, [self.notification])

    def test_permanent_error_propagates_unchanged(self) -> None:
        error = PermanentTransportError("invalid recipient")
        transport = RecordingTransport(error)

        with self.assertRaises(PermanentTransportError) as raised:
            NotificationService(transport).send(self.notification)

        self.assertIs(raised.exception, error)
        self.assertEqual(transport.notifications, [self.notification])


if __name__ == "__main__":
    unittest.main()
