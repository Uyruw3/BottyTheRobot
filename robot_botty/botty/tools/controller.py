"""
Controller module — lee mandos Xbox, PS4, PS5, Switch Pro, etc.
via pygame.joystick.

Botones compatibles:
  - Bluetooth: Xbox Wireless, PS4/PS5 DualSense, Switch Pro
  - USB: Xbox 360/One, Logitech F710, cualquier mando USB-HID
"""

import pygame
from botty.config import Config


# Default button map (Xbox layout via xpad driver)
# Index: [A, B, X, Y, LB, RB, Back, Start, Guide, L3, R3]
BUTTON_NAMES = {
    0: "A", 1: "B", 2: "X", 3: "Y",
    4: "LB", 5: "RB", 6: "Back", 7: "Start", 8: "Guide",
    9: "L3", 10: "R3",
}


class ControllerAction:
    NONE = "none"
    TALK = "talk"              # A: iniciar conversacion
    STOP_MUSIC = "stop_music"  # B: parar musica
    DRIVE_MODE = "drive_mode"  # X: activar/desactivar modo conduccion
    LISTEN = "listen"          # Y: escuchar comando
    EXPR_HAPPY = "happy"       # D-up: expresion feliz
    EXPR_SAD = "sad"           # D-down: expresion triste
    EXPR_ANGRY = "angry"       # D-left: expresion enojado
    EXPR_SURPRISED = "surprised"  # D-right: expresion sorprendido
    WAKE = "wake"              # Start: despertar
    SLEEP = "sleep"            # Back: dormir
    SPEED_UP = "speed_up"      # RB: +velocidad
    SPEED_DOWN = "speed_down"  # LB: -velocidad
    LOOK_AROUND = "look"       # Right stick: mirar alrededor


_BUTTON_MAP = {
    0: ControllerAction.TALK,
    1: ControllerAction.STOP_MUSIC,
    2: ControllerAction.DRIVE_MODE,
    3: ControllerAction.LISTEN,
    4: ControllerAction.SPEED_DOWN,
    5: ControllerAction.SPEED_UP,
    6: ControllerAction.SLEEP,
    7: ControllerAction.WAKE,
}

_HAT_MAP = {
    (0, 1):  ControllerAction.EXPR_HAPPY,
    (0, -1): ControllerAction.EXPR_SAD,
    (-1, 0): ControllerAction.EXPR_ANGRY,
    (1, 0):  ControllerAction.EXPR_SURPRISED,
}


class Controller:
    def __init__(self):
        self.joystick = None
        self.name = ""
        self.connected = False
        self._prev_buttons = {}
        self._prev_hat = (0, 0)
        self.actions = []          # actions triggered this frame
        self.drive_mode = False    # manual drive active
        self.speed_mult = 1.0

    def init(self):
        pygame.joystick.init()
        count = pygame.joystick.get_count()
        if count == 0:
            print("  [Mando] No detectado — conecta uno por USB o Bluetooth")
            return

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.name = self.joystick.get_name()
        self.connected = True
        print(f"  [Mando] Conectado: {self.name}")
        print(f"    Axes: {self.joystick.get_numaxes()}, "
              f"Botones: {self.joystick.get_numbuttons()}, "
              f"Hats: {self.joystick.get_numhats()}")

    def update(self, dt: float):
        """Lee el estado del mando y genera acciones."""
        if not self.connected:
            return

        self.actions = []

        # ── Axes (movimiento continuo) ──
        for i in range(min(self.joystick.get_numaxes(), 6)):
            val = self.joystick.get_axis(i)
            if abs(val) < Config.CONTROLLER_DEADZONE:
                val = 0.0
            # store in a dict for easy access
            setattr(self, f"_axis_{i}", val)

        # ── Buttons (flanco de subida) ──
        for i in range(self.joystick.get_numbuttons()):
            pressed = self.joystick.get_button(i)
            was_pressed = self._prev_buttons.get(i, False)
            if pressed and not was_pressed:
                action = _BUTTON_MAP.get(i)
                if action:
                    self.actions.append(action)
            self._prev_buttons[i] = pressed

        # ── Hat / D-Pad ──
        if self.joystick.get_numhats() > 0:
            hat = self.joystick.get_hat(0)
            if hat != self._prev_hat and hat != (0, 0):
                action = _HAT_MAP.get(hat)
                if action:
                    self.actions.append(action)
            self._prev_hat = hat

    def get_axis(self, index: int) -> float:
        return getattr(self, f"_axis_{index}", 0.0)

    # ── High-level helpers ──

    def get_movement(self) -> tuple[float, float]:
        """
        Returns (speed, turn) both in -1..1.
        Left stick: axis 0 = turn, axis 1 = fwd/bwd.
        """
        if not self.connected:
            return 0.0, 0.0
        speed = -self.get_axis(1)
        turn = self.get_axis(0)
        speed *= self.speed_mult
        return speed, turn

    def get_look(self) -> tuple[float, float]:
        """
        Returns (look_x, look_y) for eye direction.
        Right stick: axis 2 = X, axis 3 = Y.
        """
        if not self.connected:
            return 0.0, 0.0
        return self.get_axis(2), -self.get_axis(3)

    def is_driving(self) -> bool:
        speed, turn = self.get_movement()
        return self.drive_mode and (abs(speed) > 0.05 or abs(turn) > 0.05)

    def has_action(self, action: str) -> bool:
        return action in self.actions

    def cleanup(self):
        self.connected = False
        if self.joystick:
            try:
                self.joystick.quit()
            except Exception:
                pass
