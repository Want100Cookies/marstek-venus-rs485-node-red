import unittest
from datetime import datetime, timedelta

from custom_components.home_battery_control.models import DynamicInterval
from custom_components.home_battery_control.tariffs import mark_extreme_pairs


class DynamicTests(unittest.TestCase):
    def test_marks_pair_when_spread_meets_delta(self):
        now = datetime(2026, 1, 1, 12, 0)
        intervals = [
            DynamicInterval(now - timedelta(hours=1), now, 0.20),
            DynamicInterval(now, now + timedelta(hours=1), 0.05),
            DynamicInterval(now + timedelta(hours=1), now + timedelta(hours=2), 0.30),
        ]
        result = mark_extreme_pairs(intervals, min_delta=0.1, now=now)
        marks = [i.mark for i in intervals]
        self.assertIn("low", marks)
        self.assertIn("high", marks)

    def test_no_intervals_fallback_mark(self):
        result = mark_extreme_pairs([], min_delta=0.1)
        self.assertEqual(result.mark_now, "neutral")


if __name__ == "__main__":
    unittest.main()
