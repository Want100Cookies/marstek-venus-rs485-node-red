import unittest

from custom_components.home_battery_control.pid import PIDConfig, PIDController, INTEGRAL_CLAMP_WS


class PIDTests(unittest.TestCase):
    def test_bumpless_ki_change_preserves_i_output(self):
        controller = PIDController(PIDConfig(kp=0, ki=0.5, kd=0, input_dampening=0, output_dampening=0))
        controller.calculate(error=100, dt=1)
        old_i = controller.config.ki * controller.runtime.integral_ws
        controller.apply_ki_change(0.25)
        new_i = controller.config.ki * controller.runtime.integral_ws
        self.assertAlmostEqual(old_i, new_i, places=6)

    def test_integral_clamped(self):
        controller = PIDController(PIDConfig(kp=0, ki=1, kd=0, input_dampening=0, output_dampening=0))
        for _ in range(100000):
            controller.calculate(error=100, dt=1)
        self.assertLessEqual(controller.runtime.integral_ws, INTEGRAL_CLAMP_WS)


if __name__ == "__main__":
    unittest.main()
