import unittest
from datetime import datetime

from custom_components.home_battery_control.models import BatteryMapping, BatteryTelemetry, StrategyContext
from custom_components.home_battery_control.pid import PIDController
from custom_components.home_battery_control.strategies.full_stop import FullStopStrategy
from custom_components.home_battery_control.strategies.self_consumption import SelfConsumptionStrategy


def battery(soc=50):
    mapping = BatteryMapping(
        id="b1",
        name="Battery 1",
        soc_entity="sensor.soc",
        power_entity="sensor.power",
        max_charge_entity="number.charge",
        max_discharge_entity="number.discharge",
        command_power_entity="number.command",
    )
    return BatteryTelemetry(mapping=mapping, soc=soc, power_w=0, max_charge_w=2000, max_discharge_w=2000)


class StrategyTests(unittest.TestCase):
    def test_full_stop(self):
        result = FullStopStrategy().run(
            StrategyContext(now=datetime.now(), grid_power_w=100, selected_strategy="full_stop"),
            [battery()],
        )
        self.assertEqual(result.selected_strategy, "full_stop")
        self.assertEqual(result.commands[0].mode, "stop")

    def test_self_consumption_hysteresis(self):
        strategy = SelfConsumptionStrategy(PIDController())
        result = strategy.run(
            StrategyContext(now=datetime.now(), grid_power_w=10, selected_strategy="self_consumption", hysteresis_w=20, master_mode="full_control"),
            [battery()],
        )
        self.assertAlmostEqual(result.pid.output, 0.0)


if __name__ == "__main__":
    unittest.main()
