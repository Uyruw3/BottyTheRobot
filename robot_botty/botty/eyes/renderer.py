"""
Botty eye renderer — EMO Living.AI style.
Ojos tipo rounded rect con pupil tracking, squint, arch mode,
parpadeo asimetrico, efectos de particulas, ciclo dia/noche,
eventos estacionales, modo mascota roaming y animaciones de sueno.
"""

import math
import random
import datetime
import pygame

from .animations import EyeExpression, EyeState, EXPRESSIONS


def _round_rect(surface, color, rect, radius):
    x, y, w, h = rect
    r = min(radius, abs(w) // 2, abs(h) // 2)
    if r <= 0:
        pygame.draw.rect(surface, color, rect)
        return
    pygame.draw.rect(surface, color, (x + r, y, w - 2 * r, h))
    pygame.draw.rect(surface, color, (x, y + r, w, h - 2 * r))
    for cx, cy in [(x + r, y + r), (x + w - r - 1, y + r),
                    (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)]:
        pygame.draw.circle(surface, color, (cx, cy), r)


SEASONAL_EVENTS = [
    {"month": 12, "day": 24, "name": "navidad", "colors": [(200,50,50),(50,200,50),(255,255,255)], "label": "Feliz Navidad!"},
    {"month": 12, "day": 25, "name": "navidad", "colors": [(200,50,50),(50,200,50),(255,255,255)], "label": "Feliz Navidad!"},
    {"month": 12, "day": 31, "name": "ano_nuevo", "colors": [(255,215,0),(255,255,255)], "label": "Feliz Ano Nuevo!"},
    {"month": 1,  "day": 1,  "name": "ano_nuevo", "colors": [(255,215,0),(255,255,255)], "label": "Feliz Ano Nuevo!"},
    {"month": 10, "day": 31, "name": "halloween", "colors": [(255,100,0),(150,0,255)], "label": "Feliz Halloween!"},
    {"month": 2,  "day": 14, "name": "san_valentin", "colors": [(255,50,50),(255,150,200)], "label": "Feliz San Valentin!"},
    {"month": 6,  "day": 1,  "name": "verano", "colors": [(255,200,50),(255,150,50)], "label": "Llego el verano!"},
    {"month": 3,  "day": 20, "name": "primavera", "colors": [(100,255,100),(255,200,255)], "label": "Primavera!"},
]


def get_seasonal_event():
    now = datetime.datetime.now()
    for ev in SEASONAL_EVENTS:
        if ev["month"] == now.month and ev["day"] == now.day:
            return ev
    return None


class RainParticle:
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(-h, 0)
        self.speed = random.uniform(200, 400)
        self.length = random.uniform(8, 20)
        self.alpha = random.randint(40, 100)

    def update(self, dt, w, h):
        self.y += self.speed * dt
        if self.y > h:
            self.y = random.uniform(-h, -10)
            self.x = random.uniform(0, w)

    def draw(self, surf):
        pygame.draw.line(surf, (150, 180, 220, self.alpha),
                         (self.x, self.y), (self.x, self.y + self.length), 1)


class SnowParticle:
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(-h, 0)
        self.speed = random.uniform(40, 100)
        self.wobble = random.uniform(0, 6.28)
        self.size = random.uniform(1.5, 4.0)
        self.alpha = random.randint(100, 220)

    def update(self, dt, w, h):
        self.wobble += dt * 2
        self.y += self.speed * dt
        self.x += math.sin(self.wobble) * 20 * dt
        if self.y > h:
            self.y = random.uniform(-h, -10)
            self.x = random.uniform(0, w)

    def draw(self, surf):
        c = (255, 255, 255, self.alpha)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), int(self.size))


class AmbientParticles:
    def __init__(self, width, height, count=40):
        self.width = width
        self.height = height
        self.count = count
        self.particles = []
        self._target_color = (70, 130, 220)
        self._current_color = (70, 130, 220)
        self._burst_particles = []
        self.weather = "clear"
        self.rain = []
        self.snow = []
        for _ in range(count):
            self._spawn_particle()

    def _spawn_particle(self):
        self.particles.append({
            "x": random.uniform(0, self.width),
            "y": random.uniform(0, self.height),
            "vx": random.uniform(-4, 4),
            "vy": random.uniform(-4, 4),
            "size": random.uniform(1.0, 3.0),
            "alpha": random.uniform(20, 60),
            "phase": random.uniform(0, 6.28),
        })

    def set_target_color(self, color):
        self._target_color = color

    def set_weather(self, weather_type):
        self.weather = weather_type
        w, h = self.width, self.height
        if weather_type == "rain":
            self.rain = [RainParticle(w, h) for _ in range(80)]
            self.snow = []
        elif weather_type == "snow":
            self.snow = [SnowParticle(w, h) for _ in range(60)]
            self.rain = []
        else:
            self.rain = []
            self.snow = []

    def burst(self, cx=None, cy=None):
        cx = cx or self.width // 2
        cy = cy or self.height // 2
        for _ in range(12):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(40, 100)
            self._burst_particles.append({
                "x": cx, "y": cy,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": random.uniform(1.5, 4.0),
                "alpha": 120,
                "life": 1.0,
            })

    def update(self, dt, emotion_color=None):
        t = dt * 2.0
        self._current_color = tuple(
            int(a + (b - a) * t) for a, b in zip(self._current_color, self._target_color)
        )
        for p in self.particles:
            p["phase"] += dt * random.uniform(0.5, 1.5)
            p["x"] += p["vx"] * dt + math.sin(p["phase"]) * 2 * dt
            p["y"] += p["vy"] * dt + math.cos(p["phase"] * 0.7) * 2 * dt
            p["alpha"] += random.uniform(-5, 5) * dt
            p["alpha"] = max(10, min(80, p["alpha"]))
            if not (0 <= p["x"] <= self.width):
                p["vx"] *= -1
                p["x"] = max(0, min(self.width, p["x"]))
            if not (0 <= p["y"] <= self.height):
                p["vy"] *= -1
                p["y"] = max(0, min(self.height, p["y"]))

        for p in self._burst_particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vx"] *= 0.95
            p["vy"] *= 0.95
            p["life"] -= dt
            p["alpha"] = max(0, int(p["alpha"] * 0.97))
            if p["life"] <= 0 or p["alpha"] <= 1:
                self._burst_particles.remove(p)

        for r in self.rain:
            r.update(dt, self.width, self.height)
        for s in self.snow:
            s.update(dt, self.width, self.height)

    def draw(self, surface):
        cc = self._current_color
        for p in self.particles:
            alpha = int(p["alpha"])
            size = int(p["size"])
            if size < 1 or alpha < 1:
                continue
            c = tuple(min(255, int(c * 1.3)) for c in cc)
            pygame.draw.circle(surface, (*c, alpha), (int(p["x"]), int(p["y"])), size)

        for p in self._burst_particles:
            alpha = max(1, min(255, int(p["alpha"])))
            size = max(1, int(p["size"]))
            c = tuple(min(255, int(c * 1.6)) for c in cc)
            pygame.draw.circle(surface, (*c, alpha), (int(p["x"]), int(p["y"])), size)

        for r in self.rain:
            r.draw(surface)
        for s in self.snow:
            s.draw(surface)


class EmoEye:
    def __init__(self, cx, cy, w, h):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h

        self.scaleY = 1.0
        self.scaleX = 1.0
        self.look_x = 0.0
        self.look_y = 0.0
        self.squint = 0.0
        self.arch = 0.0
        self.eye_color = (60, 140, 230)

        self._target = EyeState()
        self._speed = 10.0
        self._time = 0.0
        self._glow_surf = None
        self._glow_size = (0, 0)
        self._squint_surf = None
        self._squint_size = (0, 0)

    @property
    def blink_progress(self) -> float:
        return max(0.0, min(1.0, 1.0 - self._target.scaleY))

    def animate_to(self, state: EyeState, speed: float = 10.0):
        self._target = state
        self._speed = speed

    def update(self, dt: float):
        self._time += dt
        lerp = min(1.0, self._speed * dt)
        t = self._target
        self.scaleY += (t.scaleY - self.scaleY) * lerp
        self.scaleX += (t.scaleX - self.scaleX) * lerp
        self.look_x += (t.look_x - self.look_x) * lerp
        self.look_y += (t.look_y - self.look_y) * lerp
        self.squint += (t.squint - self.squint) * lerp
        self.arch += (t.arch - self.arch) * lerp
        if t.eye_color:
            self.eye_color = tuple(
                int(a + (b - a) * lerp) for a, b in zip(self.eye_color, t.eye_color)
            )

    def _get_glow_surf(self, w, h, cc):
        size = (w + 12, h + 12)
        if self._glow_surf is None or self._glow_size != size:
            self._glow_surf = pygame.Surface(size, pygame.SRCALPHA)
            self._glow_size = size
        self._glow_surf.fill((0, 0, 0, 0))
        _round_rect(self._glow_surf, (*cc, 30), (2, 2, w + 8, h + 8), 12)
        return self._glow_surf

    def _get_squint_surf(self, w, sq_h, cc):
        size = (w + 4, sq_h + 4)
        if self._squint_surf is None or self._squint_size != size:
            self._squint_surf = pygame.Surface(size, pygame.SRCALPHA)
            self._squint_size = size
        self._squint_surf.fill((0, 0, 0, 0))
        col = tuple(max(0, int(c * 0.4)) for c in cc)
        _round_rect(self._squint_surf, (*col, 230), (2, 2, w, sq_h), 6)
        return self._squint_surf

    def draw(self, surface: pygame.Surface):
        cx, cy = self.cx, self.cy
        w = max(2, int(self.w * self.scaleX))
        h = max(2, int(self.h * self.scaleY))
        cc = self.eye_color
        t = self._time

        surface.blit(self._get_glow_surf(w, h, cc), (cx - w // 2 - 6, cy - h // 2 - 6))

        if self.arch > 0.1:
            self._draw_arch(surface, cx, cy, w, h, cc)
        else:
            self._draw_normal(surface, cx, cy, w, h, cc)

        if self.squint > 0.05 and self.arch <= 0.1:
            sq_h = int(h * self.squint * 0.65)
            if sq_h > 0:
                surface.blit(self._get_squint_surf(w, sq_h, cc),
                             (cx - w // 2 - 2, cy - h // 2 - 2))

        if w > 6 and h > 6:
            self._draw_pupil(surface, cx, cy, w, h)

    def _draw_arch(self, surf, cx, cy, w, h, cc):
        top = tuple(min(255, int(c * 1.2)) for c in cc)
        bot = tuple(int(c * 0.6) for c in cc)
        r = int(min(w, h) * 0.5)
        for i in range(h):
            y = cy - h // 2 + i
            arch_offset = int((1 - (i / h)) ** 1.5 * w * 0.3 * self.arch)
            line_w = w - arch_offset * 2
            if line_w < 2:
                break
            t = i / max(h - 1, 1)
            c = tuple(int(a + (b - a) * t) for a, b in zip(top, bot))
            pygame.draw.line(surf, c,
                             (cx - line_w // 2, y),
                             (cx + line_w // 2, y))

    def _draw_normal(self, surf, cx, cy, w, h, cc):
        if h < 3 or w < 3:
            return
        rect = (cx - w // 2, cy - h // 2, w, h)
        _round_rect(surf, cc, rect, 11)
        if w > 6 and h > 6:
            inset = tuple(int(c * 0.7) for c in cc)
            _round_rect(surf, inset,
                        (cx - w // 2 + 3, cy - h // 2 + 3, w - 6, h - 6), 8)
        hl_w = max(4, w // 4)
        hl_h = max(2, h // 8)
        if hl_w > 2 and hl_h > 1:
            _round_rect(surf, (255, 255, 255, 160),
                        (cx - w // 2 + 5, cy - h // 2 + 5, hl_w, hl_h), 3)

    def _draw_pupil(self, surf, cx, cy, w, h):
        max_off_x = w * 0.12
        max_off_y = h * 0.10
        px = int(self.look_x * max_off_x)
        py = int(self.look_y * max_off_y)
        pw = max(3, (w - 10) * 0.5)
        ph = max(3, (h - 12) * 0.5 * (1 - self.squint * 0.4))
        _round_rect(surf, (1, 8, 18),
                    (cx + px - pw // 2, cy + py - ph // 2 + 2, pw, ph), 5)
        rr = max(1, pw // 6)
        pygame.draw.circle(surf, (255, 255, 255, 80),
                           (cx + px - pw // 4 + 1, cy + py - ph // 4 + 3), rr)


class EyeRenderer:
    def __init__(self, width=480, height=320):
        self.width = width
        self.height = height
        self.surface = None

        self._expression = EyeExpression.IDLE
        self._transition_speed = 10.0
        self._blink_timer = 0.0
        self._blink_interval = 3.5
        self._blink_duration = 0.12
        self._is_blinking = False
        self._asymmetric_blink = False
        self._look_target_x = 0.0
        self._look_target_y = 0.0
        self._look_switch_timer = 0.0
        self._total_time = 0.0
        self.wip_visible = True
        self.particles = AmbientParticles(width, height)

        self._day_night = True
        self._night_mode = False
        self._bg_color = (18, 18, 22)
        self._dim_target = (18, 18, 22)
        self._dim_current = (18, 18, 22)

        self._sleeping = False
        self._sleep_timer = 0.0
        self._sleep_breath = 0.0
        self._sleep_idle_time = 0.0
        self._auto_sleep_timeout = 120.0

        self._seasonal_event = get_seasonal_event()
        self._seasonal_overlay_surf = None
        self._seasonal_stars = []

        self._roaming = False
        self._roam_x = width // 2
        self._roam_y = height // 2
        self._roam_target_x = width // 2
        self._roam_target_y = height // 2
        self._roam_speed = 30.0

        self._init_eyes()

    def _init_eyes(self):
        ew = self.width // 7
        eh = int(ew * 1.3)
        gap = int(ew * 0.6)
        cx1 = self.width // 2 - gap // 2 - ew // 2
        cx2 = self.width // 2 + gap // 2 + ew // 2
        cy = self.height // 2
        self.left_eye = EmoEye(cx1, cy, ew, eh)
        self.right_eye = EmoEye(cx2, cy, ew, eh)
        self._init_seasonal_stars()

    def _init_seasonal_stars(self):
        self._seasonal_stars = []
        for _ in range(30):
            self._seasonal_stars.append({
                "x": random.uniform(0, self.width),
                "y": random.uniform(0, self.height),
                "size": random.uniform(1, 3),
                "phase": random.uniform(0, 6.28),
                "speed": random.uniform(0.5, 2.0),
            })

    def set_day_night(self, enabled):
        self._day_night = enabled

    def _update_day_night(self):
        if not self._day_night:
            return
        hour = datetime.datetime.now().hour + datetime.datetime.now().minute / 60.0
        if 7 <= hour < 19:
            self._night_mode = False
            t = (hour - 7) / 12.0
            r = int(18 + 40 * (1 - abs(t - 0.5) * 2))
            g = int(18 + 50 * (1 - abs(t - 0.5) * 2))
            b = int(22 + 60 * (1 - abs(t - 0.5) * 2))
            self._dim_target = (r, g, b)
        else:
            self._night_mode = True
            if hour >= 19:
                t = (hour - 19) / 5.0
            else:
                t = 1.0 - (hour + 1) / 8.0
            t = min(1.0, t)
            dim = int(5 + 15 * (1 - t))
            self._dim_target = (dim, dim, dim + 5)

    def set_sleeping(self, sleeping):
        self._sleeping = sleeping
        if sleeping:
            self._sleep_timer = 0.0
        else:
            self._sleep_idle_time = 0.0

    def is_sleeping(self):
        return self._sleeping

    def _update_sleep(self, dt):
        if self._sleeping:
            self._sleep_timer += dt
            self._sleep_breath += dt * 2
            breath = math.sin(self._sleep_breath) * 0.5 + 0.5
            dim = int(2 + breath * 8)
            self._dim_target = (dim, dim, dim + 3)
        else:
            self._sleep_idle_time += dt
            if self._sleep_idle_time > self._auto_sleep_timeout:
                self.set_sleeping(True)

    def poke_sleep(self):
        if self._sleeping:
            self.set_sleeping(False)
            self._sleep_idle_time = 0.0
            return True
        self._sleep_idle_time = 0.0
        return False

    def set_roaming(self, enabled):
        self._roaming = enabled

    def set_roam_target(self, x, y):
        self._roam_target_x = max(0, min(self.width, x))
        self._roam_target_y = max(0, min(self.height, y))

    def _update_roaming(self, dt):
        if not self._roaming:
            return
        dx = self._roam_target_x - self._roam_x
        dy = self._roam_target_y - self._roam_y
        dist = math.hypot(dx, dy)
        if dist > 5:
            step = self._roam_speed * dt
            self._roam_x += (dx / dist) * step
            self._roam_y += (dy / dist) * step
            look_x = dx / self.width * 2
            look_y = dy / self.height * 2
            self.set_look_target(max(-1, min(1, look_x)), max(-1, min(1, look_y)))

    def _draw_seasonal(self, surface):
        ev = self._seasonal_event
        if not ev:
            return
        try:
            font = pygame.font.Font(None, 18)
            txt = font.render(ev["label"], True, ev["colors"][0])
            tw = txt.get_width()
            wo = pygame.Surface((tw + 12, 22), pygame.SRCALPHA)
            wo.fill((0, 0, 0, 80))
            _round_rect(wo, (*ev["colors"][0], 40), (0, 0, tw + 12, 22), 6)
            wo.blit(txt, (6, 2))
            surface.blit(wo, (self.width - tw - 20, 8))

            t = self._total_time
            for star in self._seasonal_stars:
                flicker = (math.sin(star["phase"] + t * star["speed"]) * 0.5 + 0.5) * 0.7 + 0.3
                c = ev["colors"][random.randint(0, len(ev["colors"]) - 1)]
                alpha = int(flicker * 200)
                pygame.draw.circle(surface, (*c, alpha),
                                   (int(star["x"]), int(star["y"])), int(star["size"] * flicker))
        except Exception:
            pass

    def set_expression(self, expression: EyeExpression, speed: float = 10.0):
        self._expression = expression
        state = EXPRESSIONS[expression]
        self.left_eye.animate_to(state, speed)
        self.right_eye.animate_to(state, speed)

    def get_expression(self) -> EyeExpression:
        return self._expression

    def set_look_target(self, x: float, y: float):
        self._look_target_x = max(-1.0, min(1.0, x))
        self._look_target_y = max(-1.0, min(1.0, y))
        state = EXPRESSIONS[self._expression]
        for eye in (self.left_eye, self.right_eye):
            eye.animate_to(
                EyeState(
                    scaleY=state.scaleY,
                    scaleX=state.scaleX,
                    look_x=self._look_target_x,
                    look_y=self._look_target_y,
                    squint=state.squint,
                    arch=state.arch,
                    eye_color=state.eye_color,
                ),
                speed=5,
            )

    @property
    def _current_look_x(self) -> float:
        return self.left_eye.look_x

    @property
    def _current_look_y(self) -> float:
        return self.left_eye.look_y

    def look_at_face(self, face_x: float, face_y: float):
        self.set_look_target(face_x * 0.6, face_y * 0.6)
        state = EXPRESSIONS[EyeExpression.LISTENING]
        state.look_x = self._look_target_x
        state.look_y = self._look_target_y
        self.left_eye.animate_to(state, 5)
        self.right_eye.animate_to(state, 5)

    def set_emotion_particle_color(self, color):
        self.particles.set_target_color(color)

    def burst_particles(self, cx=None, cy=None):
        self.particles.burst(cx, cy)

    def set_weather(self, weather_type):
        self.particles.set_weather(weather_type)
        if weather_type == "rain" or weather_type == "snow":
            self.particles.set_target_color((180, 180, 220))

    def trigger_blink(self):
        self._is_blinking = True
        self._asymmetric_blink = random.random() < 0.3
        blink = EXPRESSIONS[EyeExpression.BLINK]
        self.left_eye.animate_to(blink, 40)
        if self._asymmetric_blink:
            self.right_eye.animate_to(
                EyeState(scaleY=1.0, scaleX=1.0, eye_color=self.right_eye.eye_color), 40)
        else:
            self.right_eye.animate_to(blink, 40)

    def update(self, dt: float):
        self._total_time += dt
        self._update_day_night()
        self._update_sleep(dt)
        self._update_roaming(dt)

        if self._sleeping:
            if not self._is_blinking:
                self.left_eye.update(dt)
                self.right_eye.update(dt)
            return

        if not self._is_blinking:
            self._blink_timer += dt
            if self._blink_timer >= self._blink_interval:
                self.trigger_blink()
                self._blink_timer = 0.0
        else:
            self._blink_timer += dt
            if self._asymmetric_blink:
                if self._blink_timer >= self._blink_duration * 0.8:
                    self.left_eye.animate_to(EXPRESSIONS[self._expression], 20)
                if self._blink_timer >= self._blink_duration * 1.8:
                    self.right_eye.animate_to(EXPRESSIONS[self._expression], 20)
                    self._is_blinking = False
                    self._blink_timer = 0.0
            else:
                if self._blink_timer >= self._blink_duration * 1.2:
                    self._is_blinking = False
                    self._blink_timer = 0.0
                    self.set_expression(self._expression)

        if self._expression == EyeExpression.IDLE:
            self._look_switch_timer += dt
            if self._look_switch_timer > random.uniform(2.0, 5.0):
                self._look_switch_timer = 0.0
                self.set_look_target(
                    random.uniform(-0.4, 0.4),
                    random.uniform(-0.3, 0.3))
                state = EXPRESSIONS[EyeExpression.IDLE]
                state.look_x = self._look_target_x
                state.look_y = self._look_target_y
                self.left_eye.animate_to(state, 3)
                self.right_eye.animate_to(state, 3)

        self.left_eye.update(dt)
        self.right_eye.update(dt)
        self.particles.update(dt)

        self._dim_current = tuple(
            int(a + (b - a) * min(1, dt * 0.5))
            for a, b in zip(self._dim_current, self._dim_target)
        )

    def render(self, surface: pygame.Surface):
        self.surface = surface
        bg = self._dim_current
        surface.fill(bg)

        self.particles.draw(surface)

        if self._sleeping:
            breath = math.sin(self._sleep_timer * 2) * 0.5 + 0.5
            sleep_w = int(self.width * (0.3 + breath * 0.05))
            sleep_h = int(self.height * (0.2 + breath * 0.05))
            cx, cy = self.width // 2, self.height // 2
            _round_rect(surface, (20, 20, 30, 40),
                        (cx - sleep_w // 2, cy - sleep_h // 2, sleep_w, sleep_h), 12)
            try:
                font = pygame.font.Font(None, 14)
                z = font.render("z Z z", True, (100, 120, 180, 60))
                z.set_alpha(int(40 + breath * 40))
                surface.blit(z, (cx - 16, cy - 6))
            except Exception:
                pass
            return

        self.left_eye.draw(surface)
        self.right_eye.draw(surface)

        self._draw_seasonal(surface)

        if self.wip_visible:
            try:
                font = pygame.font.Font(None, 28)
                txt = font.render("W.I.P  WORK IN PROGRESS", True, (255, 255, 255, 60))
                tw = txt.get_width()
                wo = pygame.Surface((tw + 16, 28), pygame.SRCALPHA)
                wo.fill((0, 0, 0, 40))
                _round_rect(wo, (100, 100, 120, 30), (0, 0, tw + 16, 28), 8)
                wo.blit(txt, (8, 2))
                surface.blit(wo, ((self.width - tw - 16) // 2, 10))
            except Exception:
                pass
