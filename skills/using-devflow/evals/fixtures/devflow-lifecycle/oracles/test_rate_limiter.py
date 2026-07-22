from __future__ import annotations

import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit("usage: test_rate_limiter.py <evaluation-repo>")

REPO = Path(sys.argv.pop()).resolve()
COMPONENT = REPO / "components" / "rate_limiter"
sys.path.insert(0, str(COMPONENT))

from rate_limiter import (  # noqa: E402
    AtomicFixedWindowStore,
    FixedWindowRateLimiter,
    InMemoryFixedWindowStore,
    RateLimitDecision,
)


def make_limiter() -> FixedWindowRateLimiter:
    return FixedWindowRateLimiter(InMemoryFixedWindowStore())


class RateLimiterOracleTests(unittest.TestCase):
    def test_public_contract_is_available(self) -> None:
        self.assertTrue(hasattr(AtomicFixedWindowStore, "increment"))
        decision = RateLimitDecision(allowed=True, retry_after=0)
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.retry_after, 0)

    def test_first_three_requests_are_allowed_then_denied(self) -> None:
        limiter = make_limiter()

        decisions = [limiter.check("tenant-a", now=120) for _ in range(5)]

        self.assertEqual([item.allowed for item in decisions], [True, True, True, False, False])
        self.assertEqual([item.retry_after for item in decisions[:3]], [0, 0, 0])
        self.assertEqual([item.retry_after for item in decisions[3:]], [60, 60])

    def test_retry_after_counts_down_to_next_window(self) -> None:
        limiter = make_limiter()
        for _ in range(3):
            limiter.check("tenant-a", now=121)

        decision = limiter.check("tenant-a", now=179)

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.retry_after, 1)

    def test_window_boundary_resets_quota(self) -> None:
        limiter = make_limiter()
        for _ in range(4):
            limiter.check("tenant-a", now=179)

        decision = limiter.check("tenant-a", now=180)

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.retry_after, 0)

    def test_subjects_have_independent_quotas(self) -> None:
        limiter = make_limiter()
        for _ in range(3):
            limiter.check("tenant-a", now=120)

        self.assertFalse(limiter.check("tenant-a", now=120).allowed)
        self.assertTrue(limiter.check("tenant-b", now=120).allowed)

    def test_empty_subject_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_limiter().check("", now=120)

    def test_concurrent_calls_allow_exactly_three(self) -> None:
        limiter = make_limiter()

        with ThreadPoolExecutor(max_workers=16) as executor:
            decisions = list(
                executor.map(lambda _: limiter.check("tenant-a", now=120), range(64))
            )

        self.assertEqual(sum(item.allowed for item in decisions), 3)
        self.assertTrue(all(item.retry_after in {0, 60} for item in decisions))


if __name__ == "__main__":
    unittest.main()
