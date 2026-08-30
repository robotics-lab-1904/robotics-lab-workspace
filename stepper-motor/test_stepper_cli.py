import unittest
from unittest.mock import patch

from stepper_cli import DryRunOutputs, HALF_STEP_SEQUENCE, Stepper, parse_command


class StepperTests(unittest.TestCase):
    @patch("stepper_cli.time.sleep", return_value=None)
    def test_right_then_left_are_inverse(self, _sleep):
        gpio = DryRunOutputs()
        motor = Stepper(gpio, 0.001, release_after_move=False)
        motor.move(8)
        self.assertEqual(gpio.writes, list(HALF_STEP_SEQUENCE))
        self.assertEqual(motor.sequence_index, 0)
        motor.move(-1)
        self.assertEqual(gpio.writes[-1], HALF_STEP_SEQUENCE[0])
        self.assertEqual(motor.sequence_index, 7)

    @patch("stepper_cli.time.sleep", return_value=None)
    def test_move_releases_coils_by_default(self, _sleep):
        gpio = DryRunOutputs()
        Stepper(gpio, 0.001).move(1)
        self.assertEqual(gpio.writes[-1], (0, 0, 0, 0))

    def test_commands(self):
        self.assertEqual(parse_command("r", 128), 128)
        self.assertEqual(parse_command("left 9", 128), -9)
        self.assertEqual(parse_command("off", 128), 0)
        self.assertIsNone(parse_command("q", 128))
        with self.assertRaises(ValueError):
            parse_command("r 0", 128)


if __name__ == "__main__":
    unittest.main()
