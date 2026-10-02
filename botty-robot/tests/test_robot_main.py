import robot_main


class FakeHardware:
    def __init__(self):
        self.calls = []

    def motor_forward(self, speed):
        self.calls.append(("forward", speed))

    def motor_stop(self):
        self.calls.append(("stop",))

    def get_distance(self):
        return 12.5


def test_movement_command_stops_after_requested_duration(monkeypatch):
    hardware = FakeHardware()
    sleeps = []
    monkeypatch.setattr(robot_main.time, "sleep", sleeps.append)

    assert robot_main._run_command(hardware, "forward 70 0.1")

    assert hardware.calls == [("forward", 70), ("stop",)]
    assert sleeps == [0.1]


def test_unsafe_movement_duration_is_rejected():
    hardware = FakeHardware()

    assert robot_main._run_command(hardware, "forward 70 2.1")
    assert hardware.calls == []


def test_quit_exits_console():
    assert not robot_main._run_command(FakeHardware(), "quit")


def test_hardware_errors_are_not_hidden():
    class BrokenHardware(FakeHardware):
        def motor_forward(self, speed):
            raise ValueError("GPIO failure")

    import pytest

    with pytest.raises(ValueError, match="GPIO failure"):
        robot_main._run_command(BrokenHardware(), "forward 50")
