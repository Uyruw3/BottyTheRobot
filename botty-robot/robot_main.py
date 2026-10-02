"""Safe command-line console for testing Botty's physical hardware."""

import shlex
import time

from robot_hardware import RobotHardware


MOTIONS = {
    "forward": "motor_forward",
    "backward": "motor_backward",
    "left": "motor_left",
    "right": "motor_right",
}


def _run_command(hardware, line):
    try:
        parts = shlex.split(line)
    except ValueError as exc:
        print(f"Invalid command: {exc}")
        return True
    if not parts:
        return True

    command = parts[0].lower()
    if command in {"quit", "exit", "q"}:
        return False
    if command in {"help", "?"}:
        print("Commands: forward|backward|left|right [speed] [seconds], "
              "stop, distance, beep [frequency] [seconds], help, quit")
    elif command in MOTIONS:
        if len(parts) > 3:
            print("Invalid command: Use: direction [speed] [seconds]")
            return True
        try:
            speed = int(parts[1]) if len(parts) > 1 else 50
            duration = float(parts[2]) if len(parts) > 2 else 0.3
        except ValueError as exc:
            print(f"Invalid command: {exc}")
            return True
        if not 1 <= speed <= 100:
            print("Invalid command: Speed must be between 1 and 100")
            return True
        if not 0 < duration <= 2:
            print("Invalid command: Movement duration must be greater than 0 and at most 2 seconds")
            return True
        getattr(hardware, MOTIONS[command])(speed)
        try:
            time.sleep(duration)
        finally:
            hardware.motor_stop()
    elif command == "stop":
        hardware.motor_stop()
    elif command == "distance":
        distance = hardware.get_distance()
        print("No echo received." if distance < 0 else f"Distance: {distance:.1f} cm")
    elif command == "beep":
        if len(parts) > 3:
            print("Invalid command: Use: beep [frequency] [seconds]")
            return True
        try:
            frequency = int(parts[1]) if len(parts) > 1 else 1000
            duration = float(parts[2]) if len(parts) > 2 else 0.2
        except ValueError as exc:
            print(f"Invalid command: {exc}")
            return True
        if not 50 <= frequency <= 5000:
            print("Invalid command: Frequency must be between 50 and 5000 Hz")
            return True
        if not 0 < duration <= 2:
            print("Invalid command: Beep duration must be greater than 0 and at most 2 seconds")
            return True
        hardware.buzzer_beep(frequency, duration)
    else:
        print(f"Unknown command: {command}. Type 'help' for commands.")
    return True


def main():
    hardware = RobotHardware()
    print("Botty Robot hardware console. Type 'help' for commands.")
    try:
        while True:
            try:
                if not _run_command(hardware, input("botty> ")):
                    break
            except EOFError:
                break
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        hardware.cleanup()


if __name__ == "__main__":
    main()
