"""
OLED eye renderer — pixel-art simplificado para SSD1306 128x64.
Mapea las expresiones EMO-style al display monocromo.
"""

import time
import random
from botty.eyes.animations import EyeExpression, EXPRESSIONS
from botty.config import Config


class OLEDEyes:
    def __init__(self, oled):
        self.oled = oled
        self.expression = EyeExpression.IDLE
        self._transition = 1.0
        self._target_expr = EyeExpression.IDLE
        self._blink_timer = 0.0
        self._look_x = 0.0
        self._look_y = 0.0

    def set_expression(self, expr: EyeExpression, speed: float = 6.0):
        self._target_expr = expr
        self._transition = 0.0

    def set_look_target(self, x: float, y: float):
        self._look_x = max(-1, min(1, x))
        self._look_y = max(-1, min(1, y))

    def update(self, dt: float):
        self._transition = min(1.0, self._transition + dt * 6.0)
        if self._transition >= 1.0:
            self.expression = self._target_expr
        self._blink_timer += dt
        if self._blink_timer > Config.EYE_BLINK_INTERVAL:
            self._blink_timer = 0.0

    def _get_state(self):
        if self.expression in EXPRESSIONS:
            return EXPRESSIONS[self.expression]
        return EXPRESSIONS[EyeExpression.IDLE]

    def render(self):
        if not self.oled or not self.oled.ready:
            return
        self.oled.display(lambda draw: self._draw(draw))

    def _draw(self, draw):
        w, h = self.oled.width, self.oled.height
        state = self._get_state()

        eye_spacing = 16
        eye_r = 12
        cx1 = w // 2 - eye_spacing
        cx2 = w // 2 + eye_spacing
        cy = h // 2

        blinking = self._blink_timer < 0.15
        scale_y = state.scaleY if not blinking else 0.05

        for cx in (cx1, cx2):
            self._draw_eye(draw, cx, cy, eye_r, state, scale_y)

    def _draw_eye(self, draw, cx, cy, r, state, scale_y):
        # Fully closed
        if scale_y < 0.15:
            draw.line([cx - r, cy, cx + r, cy], fill=255, width=1)
            return

        visible_r = r * min(1.0, scale_y)
        if visible_r < 2:
            draw.line([cx - r, cy, cx + r, cy], fill=255, width=1)
            return

        # Eye body (white rounded rect approximation)
        body_w = visible_r * 2
        body_h = visible_r * 1.4
        draw.ellipse([
            cx - body_w // 2, cy - body_h // 2,
            cx + body_w // 2, cy + body_h // 2
        ], outline=255, fill=255)

        # Iris
        iris_r = visible_r * 0.45
        ix = cx + int(self._look_x * r * 0.3)
        iy = cy + int(self._look_y * r * 0.3)
        if iris_r > 2:
            draw.ellipse(
                [ix - iris_r, iy - iris_r, ix + iris_r, iy + iris_r],
                outline=0, fill=0
            )

        # Pupil highlight
        hl_r = max(1, int(iris_r * 0.35))
        px = ix - int(iris_r * 0.15)
        py = iy - int(iris_r * 0.15)
        draw.ellipse(
            [px - hl_r, py - hl_r, px + hl_r, py + hl_r],
            outline=255, fill=255
        )

        # Squint line (top)
        if state.squint > 0.05:
            sq_h = int(body_h * state.squint * 0.4)
            draw.line([cx - body_w // 2, cy - body_h // 2 + sq_h,
                       cx + body_w // 2, cy - body_h // 2 + sq_h],
                      fill=255, width=1)
