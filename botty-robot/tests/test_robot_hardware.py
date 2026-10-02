import builtins

from robot_hardware import RobotHardware


def test_hardware_falls_back_to_safe_simulation(monkeypatch):
    original_import = builtins.__import__

    def import_without_gpio(name, *args, **kwargs):
        if name == "RPi.GPIO":
            raise ImportError("GPIO unavailable in test")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_gpio)
    hardware = RobotHardware()

    assert hardware.get_distance() == -1
    hardware.motor_forward(100)
    hardware.motor_backward(100)
    hardware.motor_left(100)
    hardware.motor_right(100)
    hardware.motor_stop()
    hardware.buzzer_on()
    hardware.buzzer_beep()
    hardware.buzzer_off()
    hardware.cleanup()
    hardware.cleanup()
