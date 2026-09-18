import unittest
from datetime import datetime, timedelta

from custom_components.home_battery_control.models import BatteryMapping, BatteryTelemetry
from custom_components.home_battery_control.priority import ordered_batteries


def mk(i):
    m = BatteryMapping(
        id=f"b{i}",
        name=f"B{i}",
        soc_entity="sensor.a",
        power_entity="sensor.b",
        max_charge_entity="number.c",
        max_discharge_entity="number.d",
        command_power_entity="number.e",
    )
    return BatteryTelemetry(mapping=m, soc=50, power_w=0, max_charge_w=1000, max_discharge_w=1000)


class PriorityTests(unittest.TestCase):
    def test_manual_priority(self):
        ordered = ordered_batteries([mk(1), mk(2), mk(3)], "manual", manual_priority_index=1)
        self.assertEqual([b.mapping.id for b in ordered], ["b2", "b3", "b1"])

    def test_auto_balance_rotates_each_30m(self):
        base = datetime(2026, 1, 1, 0, 0, 0)
        ordered = ordered_batteries([mk(1), mk(2), mk(3)], "auto_balance", now=base + timedelta(minutes=30), cycle_anchor=base)
        self.assertEqual([b.mapping.id for b in ordered], ["b2", "b3", "b1"])


if __name__ == "__main__":
    unittest.main()
