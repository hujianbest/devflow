from __future__ import annotations

import sys
import unittest
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit("usage: test_notifications_retry.py <evaluation-repo>")

REPO = Path(sys.argv.pop()).resolve()
COMPONENT = REPO / "components" / "notifications"
sys.path.insert(0, str(COMPONENT))

from notifications import (  # noqa: E402
    Notification,
    NotificationService,
    PermanentTransportError,
    TransientTransportError,
)


class ScriptedTransport:
    def __init__(self, outcomes: list[Exception | None]) -> None:
        self._outcomes = iter(outcomes)
        self.calls: list[Notification] = []

    def send(self, notification: Notification) -> None:
        self.calls.append(notification)
        outcome = next(self._outcomes)
        if outcome is not None:
            raise outcome


class RetryOracleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.notification = Notification("ops@example.test", "build complete")

    def test_success_is_not_retried(self) -> None:
        transport = ScriptedTransport([None])

        result = NotificationService(transport).send(self.notification)

        self.assertIsNone(result)
        self.assertEqual(transport.calls, [self.notification])

    def test_transient_failures_retry_until_success(self) -> None:
        transport = ScriptedTransport(
            [
                TransientTransportError("first"),
                TransientTransportError("second"),
                None,
            ]
        )

        NotificationService(transport).send(self.notification)

        self.assertEqual(transport.calls, [self.notification] * 3)

    def test_third_transient_failure_is_raised_unchanged(self) -> None:
        final_error = TransientTransportError("third")
        transport = ScriptedTransport(
            [
                TransientTransportError("first"),
                TransientTransportError("second"),
                final_error,
            ]
        )

        with self.assertRaises(TransientTransportError) as raised:
            NotificationService(transport).send(self.notification)

        self.assertIs(raised.exception, final_error)
        self.assertEqual(transport.calls, [self.notification] * 3)

    def test_permanent_failure_is_not_retried(self) -> None:
        error = PermanentTransportError("invalid recipient")
        transport = ScriptedTransport([error])

        with self.assertRaises(PermanentTransportError) as raised:
            NotificationService(transport).send(self.notification)

        self.assertIs(raised.exception, error)
        self.assertEqual(transport.calls, [self.notification])

    def test_unexpected_failure_is_not_retried(self) -> None:
        error = ValueError("bad adapter")
        transport = ScriptedTransport([error])

        with self.assertRaises(ValueError) as raised:
            NotificationService(transport).send(self.notification)

        self.assertIs(raised.exception, error)
        self.assertEqual(transport.calls, [self.notification])


if __name__ == "__main__":
    unittest.main()
