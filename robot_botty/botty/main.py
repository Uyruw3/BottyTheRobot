"""
Botty Robot — Main entry point.
Robot autonomo con ruedas, IA, sensores ultrasonicos, OLED,
reconocimiento facial, voz, memoria y aprendizaje por refuerzo.
"""

import sys
import time
import signal
import random
import threading
import queue

import pygame

from botty.config import Config
from botty.eyes.renderer import EyeRenderer
from botty.eyes.animations import EyeExpression
from botty.display.oled import OLEDDisplay
from botty.display.eye_renderer_oled import OLEDEyes
from botty.vision.camera import Camera
from botty.vision.face_recognition import FaceRecognizer
from botty.vision.object_detection import ObjectDetector
from botty.audio.stt import SpeechRecognizer
from botty.audio.tts import Speaker
from botty.ai.brain import Brain
from botty.tools.web_search import WebSearch
from botty.tools.music import MusicPlayer
from botty.tools.controller import Controller, ControllerAction
from botty.tools.desktop_hands import DesktopHands
from botty.sensors.ultrasonic import SonarArray
from botty.rl.obstacle_avoidance import ObstacleAvoidanceRL
from botty.memory.face_memory import FaceMemory
from botty.movement.motors import Motors


class BottyRobot:
    def __init__(self):
        self.running = False
        self.clock = pygame.time.Clock()

        self.eye_renderer = None
        self.oled = None
        self.oled_eyes = None
        self.camera = None
        self.face_recognizer = None
        self.object_detector = None
        self.stt = None
        self.speaker = None
        self.brain = None
        self.motors = None
        self.web_search = None
        self.music_player = None
        self.controller = None
        self.sonar = None
        self.rl = None
        self.memory = None
        self.desktop_hands = None

        self.screen = None
        self.display_surface = None

        # State
        self.current_user = None
        self.last_face_seen = 0
        self.last_interaction = 0
        self._voice_queue = queue.Queue()
        self._listener_thread = None
        self._listener_running = False
        self._typing_mode = False
        self._input_text = ""
        self._mouse_x = 0
        self._mouse_y = 0
        self._mouse_reaction_timer = 0.0
        self._prev_expression = EyeExpression.IDLE
        self._idle_behavior_timer = 0.0
        self._idle_complaints = [
            "Uf... que aburrido.",
            "Bostezando aqui solo...",
            "Cuando volveras?",
            "Hmm... sin nadie.",
            "Me gustaria explorar.",
            "Que silencio hay...",
            "Tic tac, tic tac...",
            "Alguien me habla?",
            "Mis ruedas necesitan accion.",
            "La vida de robot es dura.",
        ]
        self._touch_reactions = [
            "Hey! Que fue eso?",
            "Ay, me tocaste!",
            "Oye!",
            "Eh!",
            "Que haces?",
            "Jeje, cosquillas!",
            "Ups!",
            "Otra vez?",
        ]
        self.face_lost_timeout = 5.0
        self.controller_drive = False
        self._auto_mode = True
        self._developer_mode = False
        self._lockout_timer = 0.0
        self._owner_name = Config.DEVELOPER_OWNER_NAME
        self._last_voice_text = ""
        self._fleeing = False
        self._pushing = False
        self._avoid_timer = 0.0
        self._explore_timer = 0.0
        self._explore_dir = 1

    # ── Init ──

    def init(self):
        print("=" * 50)
        print("  Botty Prototype — Iniciando...")
        print("=" * 50)

        self._init_display()
        self._init_eyes()
        self._init_oled()
        self._init_audio()
        self._init_vision()
        self._init_ai()
        self._init_motors()
        self._init_sensors()
        self._init_rl()
        self._init_memory()
        self._init_controller()
        self._start_listener()

        print("  Sistema listo!")

    def _init_display(self):
        pygame.init()
        flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE if Config.DISPLAY_FULLSCREEN else 0
        self.screen = pygame.display.set_mode(
            (Config.DISPLAY_WIDTH, Config.DISPLAY_HEIGHT), flags
        )
        pygame.display.set_caption("Botty Robot")
        pygame.key.start_text_input()
        self.display_surface = self.screen

    def _init_eyes(self):
        self.eye_renderer = EyeRenderer(Config.DISPLAY_WIDTH, Config.DISPLAY_HEIGHT)

    def _init_oled(self):
        if Config.OLED_ENABLED:
            self.oled = OLEDDisplay()
            if self.oled.init():
                self.oled_eyes = OLEDEyes(self.oled)

    def _init_audio(self):
        self.speaker = Speaker()
        try:
            self.speaker.init()
        except Exception as e:
            print(f"  ! Error TTS: {e}")
        self.stt = SpeechRecognizer()
        try:
            self.stt.init()
        except Exception as e:
            print(f"  ! Error STT: {e}")

    def _init_vision(self):
        self.camera = Camera()
        if not self.camera.start():
            print("  ! No se pudo iniciar la camara")
            self.camera = None
        self.face_recognizer = FaceRecognizer()
        self.face_recognizer.load_known_faces()

        self.object_detector = ObjectDetector()
        if Config.OBJECT_DETECTION_ENABLED:
            self.object_detector.init()

    def _init_ai(self):
        self.web_search = WebSearch()
        self.music_player = MusicPlayer()
        self.brain = Brain(
            web_search=self.web_search,
            music_player=self.music_player,
        )

    def _init_motors(self):
        self.motors = Motors()
        self.motors.init()

    def _init_sensors(self):
        self.sonar = SonarArray()
        if Config.SONAR_ENABLED:
            self.sonar.init()

    def _init_rl(self):
        self.rl = ObstacleAvoidanceRL()
        if Config.RL_ENABLED:
            self.rl.load()

    def _init_memory(self):
        self.memory = FaceMemory()
        if Config.MEMORY_ENABLED:
            self.memory.load()

    def _init_controller(self):
        if not Config.CONTROLLER_ENABLED:
            return
        self.controller = Controller()
        self.controller.init()
        self.desktop_hands = DesktopHands()
        if self.desktop_hands.is_available():
            print("  [Manos] Botty tiene manos digitales!")

    # ── Listener thread ──

    def _start_listener(self):
        self._listener_running = True
        self._listener_thread = threading.Thread(target=self._listener_loop, daemon=True)
        self._listener_thread.start()

    def _listener_loop(self):
        while self._listener_running:
            try:
                text = self.stt.listen(timeout=1.0)
                if text:
                    self._voice_queue.put(text)
            except Exception as e:
                print(f"  [Listener] Error: {e}")
                time.sleep(1.0)

    # ── Boot animation ──

    def _boot_animation(self):
        print("  Animacion de inicio...")
        self.eye_renderer.set_expression(EyeExpression.SHUT_DOWN)
        for i in range(30):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            dt = self.clock.tick(Config.EYE_FPS) / 1000.0
            self.eye_renderer.update(dt)
            if i == 15:
                self.eye_renderer.set_expression(EyeExpression.WAKING_UP, speed=4)
            self.eye_renderer.render(self.display_surface)
            pygame.display.flip()
            self._update_oled()

        self.eye_renderer.set_expression(EyeExpression.IDLE)
        for _ in range(10):
            dt = self.clock.tick(Config.EYE_FPS) / 1000.0
            self.eye_renderer.update(dt)
            self.eye_renderer.render(self.display_surface)
            pygame.display.flip()
            self._update_oled()

    def _on_mouse_touch(self, pos):
        mx, my = pos
        cw, ch = self.eye_renderer.width, self.eye_renderer.height
        face_cx, face_cy = cw // 2, ch // 2
        rel_x = (mx - face_cx) / (cw // 2)
        rel_y = (my - face_cy) / (ch // 2)
        rel_x = max(-1.0, min(1.0, rel_x))
        rel_y = max(-1.0, min(1.0, rel_y))
        self.eye_renderer.set_look_target(rel_x, rel_y)
        self._prev_expression = self.eye_renderer.get_expression()
        expr = random.choice([EyeExpression.SURPRISED, EyeExpression.CONFUSED,
                              EyeExpression.HAPPY, EyeExpression.ANGRY])
        self.eye_renderer.set_expression(expr, speed=8)
        self._mouse_reaction_timer = 0.8
        if self.speaker and hasattr(self.speaker, 'engine') and self.speaker.engine:
            msg = random.choice(self._touch_reactions)
            self.speaker.say(msg, block=False)

    def _shutdown_animation(self):
        self.eye_renderer.set_expression(EyeExpression.SAD)
        for _ in range(15):
            self.eye_renderer.update(1 / 30)
            self.eye_renderer.render(self.display_surface)
            pygame.display.flip()
            self._update_oled()
        self.eye_renderer.set_expression(EyeExpression.SHUT_DOWN, speed=3)
        for _ in range(20):
            self.eye_renderer.update(1 / 30)
            self.eye_renderer.render(self.display_surface)
            pygame.display.flip()
            self._update_oled()

    def _update_oled(self):
        if self.oled_eyes:
            self.oled_eyes.update(1 / 30)
            self.oled_eyes.render()

    # ── Vision ──

    def _process_vision(self) -> tuple[list[dict], list[dict]]:
        faces, objects = [], []
        if self.camera is None:
            return faces, objects

        frame = self.camera.read()
        if frame is None:
            return faces, objects

        if self.face_recognizer.ready:
            faces = self.face_recognizer.detect_faces(frame)
            if faces and Config.FACE_RECOGNITION_ENABLED:
                faces = self.face_recognizer.recognize(frame, faces)

        if self.object_detector and self.object_detector.ready:
            objects = self.object_detector.detect_legs_and_feet(frame)
            if not objects:
                objects = self.object_detector.detect_motion(frame)

        return faces, objects

    # ── Behaviors ──

    def _autonomous_behavior(self, dt: float):
        """Bucle autonomo: evitar obstaculos, explorar, huir."""
        if not self._auto_mode or self.controller_drive:
            return

        sonar = self.sonar.read() if self.sonar and self.sonar.ready else {}
        front = sonar.get("front", 999.0)
        left = sonar.get("left", 999.0)
        right = sonar.get("right", 999.0)

        # ── RL predict ──
        if self.rl and self.rl.ready:
            speed, turn = self.rl.predict(front, left, right)
            spd = int(speed * Config.MOTOR_MAX_SPEED)
            if abs(speed) > 0.1:
                l = int(clamp(spd + turn * Config.MOTOR_MAX_SPEED, -100, 100))
                r = int(clamp(spd - turn * Config.MOTOR_MAX_SPEED, -100, 100))
                self.motors.drive(l, r)
                return

        # ── Flee from close objects ──
        if front < Config.SONAR_FLEE_THRESHOLD:
            self._fleeing = True
            self.eye_renderer.set_expression(EyeExpression.SURPRISED)
            self.motors.backward(Config.MOTOR_MAX_SPEED)
            time.sleep(0.4)
            self.motors.turn_right(Config.MOTOR_MAX_SPEED)
            time.sleep(0.3)
            self.motors.stop()
            self._fleeing = False
            return

        # ── Avoid obstacles ──
        if front < Config.SONAR_OBSTACLE_THRESHOLD:
            self._avoid_timer = 0.5
            if left > right:
                self.motors.turn_left(Config.MOTOR_MAX_SPEED)
            else:
                self.motors.turn_right(Config.MOTOR_MAX_SPEED)
            return

        if self._avoid_timer > 0:
            self._avoid_timer -= dt
            self.motors.forward(Config.MOTOR_MAX_SPEED // 2)
            return

        # ── Explore ──
        self._explore_timer += dt
        if self._explore_timer > random.uniform(2.0, 5.0):
            self._explore_timer = 0
            self._explore_dir = random.choice([-1, 0, 1])

        if self._explore_dir != 0:
            if self._explore_dir > 0:
                self.motors.turn_right(Config.MOTOR_MAX_SPEED // 2)
            else:
                self.motors.turn_left(Config.MOTOR_MAX_SPEED // 2)
        else:
            self.motors.forward(Config.MOTOR_MAX_SPEED // 3)

    def _handle_faces_and_objects(self, faces: list[dict], objects: list[dict]):
        now = time.time()

        # ── Flee from legs/feet ──
        legs = [o for o in objects if o.get("type") == "legs_feet"]
        if legs:
            closest = min(legs, key=lambda x: x.get("distance_estimate", 999))
            dist = closest.get("distance_estimate", 999)
            if dist < Config.OBJECT_FLEE_DISTANCE:
                self._run_away()
                return

        # ── Face handling ──
        if not faces:
            self._handle_no_face()
            return

        closest = max(faces, key=lambda f: f["bbox"][2] * f["bbox"][3])
        name = closest.get("name", "Desconocido")

        cx, cy = closest["center"]
        rel_x = (cx / Config.CAMERA_WIDTH) * 2 - 1
        rel_y = (cy / Config.CAMERA_HEIGHT) * 2 - 1
        self.eye_renderer.look_at_face(rel_x, rel_y)

        if self.current_user is None:
            self._greet_person(name)
        elif name != self.current_user and name != "Desconocido":
            self.current_user = name
            self.last_interaction = now
            self.speaker.say(f"Ahora veo a {name}. Hola!")
            self.eye_renderer.set_expression(EyeExpression.HAPPY)
        else:
            self.last_interaction = now
            if self.eye_renderer.get_expression() not in (
                EyeExpression.TALKING, EyeExpression.THINKING
            ):
                self.eye_renderer.set_expression(EyeExpression.LISTENING)

        self.last_face_seen = now

    def _greet_person(self, name: str):
        self.current_user = name
        self.last_interaction = time.time()
        self.eye_renderer.set_expression(EyeExpression.SURPRISED, speed=6)

        familiarity = "desconocido"
        if self.memory:
            familiarity = self.memory.get_familiarity(name)

        if name != "Desconocido":
            if familiarity == "amigo":
                greeting = f"Hola {name}! Que alegria verte de nuevo."
                self.eye_renderer.set_expression(EyeExpression.LOVING)
                self.motors.forward(30)
                time.sleep(0.2)
                self.motors.stop()
            elif familiarity == "conocido":
                greeting = f"Hey {name}, ya regresaste!"
                self.eye_renderer.set_expression(EyeExpression.HAPPY)
            else:
                greeting = f"Hola {name}! Buen conocerte."
                self.eye_renderer.set_expression(EyeExpression.HAPPY)
            if self.memory:
                self.memory.remember(name)
        else:
            greeting = "Hola! Quien eres? No te tengo en mis recuerdos."
            self.eye_renderer.set_expression(EyeExpression.CONFUSED)
            self.motors.forward(20)
            time.sleep(0.2)
            self.motors.stop()

        self.speaker.say(greeting)

    def _run_away(self):
        self._fleeing = True
        self.eye_renderer.set_expression(EyeExpression.SURPRISED)
        if self.speaker:
            self.speaker.say("Ay, piernas!", block=False)
        self.motors.backward(Config.MOTOR_MAX_SPEED)
        time.sleep(0.6)
        self.motors.turn_right(Config.MOTOR_MAX_SPEED)
        time.sleep(0.4)
        self.motors.forward(Config.MOTOR_MAX_SPEED)
        time.sleep(0.3)
        self.motors.stop()
        self._fleeing = False

    def _handle_no_face(self):
        if time.time() - self.last_face_seen > self.face_lost_timeout:
            self.current_user = None
            if self.eye_renderer.get_expression() not in (
                EyeExpression.IDLE, EyeExpression.SEARCHING
            ):
                self.eye_renderer.set_expression(EyeExpression.SEARCHING, speed=4)
                time.sleep(0.3)
                self.eye_renderer.set_expression(EyeExpression.IDLE)

    def _push_object(self):
        """Empuja un objeto con la pala delantera."""
        if not Config.SHOVEL_ENABLED:
            return
        self._pushing = True
        self.eye_renderer.set_expression(EyeExpression.HAPPY)
        try:
            import RPi.GPIO as GPIO
            GPIO.setup(Config.SHOVEL_PIN, GPIO.OUT)
            GPIO.output(Config.SHOVEL_PIN, GPIO.HIGH)
            self.motors.forward(Config.MOTOR_MAX_SPEED)
            time.sleep(Config.SHOVEL_PUSH_DURATION)
            self.motors.stop()
            GPIO.output(Config.SHOVEL_PIN, GPIO.LOW)
        except Exception as e:
            print(f"  [Shovel] Error: {e}")
        self._pushing = False

    # ── Conversation ──

    def _is_dangerous(self, text: str) -> bool:
        """Filtro de seguridad — rechaza comandos peligrosos."""
        lower = text.lower()
        for kw in Config.DEVELOPER_DANGEROUS_KEYWORDS:
            if kw in lower:
                return True
        return False

    def _handle_voice_command(self, text: str):
        """Procesa comandos de voz especiales."""
        lower = text.lower().strip()

        # ── Developer Mode ──
        if Config.DEVELOPER_PHRASE in lower:
            if self.current_user and self.current_user == self._owner_name:
                self._developer_mode = True
                self._auto_mode = False
                self.controller_drive = False
                self.eye_renderer.set_expression(EyeExpression.DEVELOPER, speed=4)
                self.speaker.say("Developer Mode activado. A sus ordenes, dueno.")
                print("  [MODO] DEVELOPER MODE ACTIVADO")
                return True
            else:
                self.speaker.say("Solo el dueno puede activar Developer Mode.")
                self.eye_renderer.set_expression(EyeExpression.CONFUSED)
                return True

        # ── Modo Auto ──
        if "modo auto" in lower or "modo automatico" in lower:
            self._auto_mode = True
            self._developer_mode = False
            self.controller_drive = False
            self.motors.stop()
            self.eye_renderer.set_expression(EyeExpression.HAPPY)
            self.speaker.say("Modo automatico activado.")
            print("  [MODO] AUTO")
            return True

        # ── Modo Manual ──
        if "modo manual" in lower or "modo mando" in lower:
            self.controller_drive = True
            self._auto_mode = False
            self._developer_mode = False
            self.motors.stop()
            self.eye_renderer.set_expression(EyeExpression.DRIVE)
            self.speaker.say("Modo manual. Usa el mando para conducirme.")
            print("  [MODO] MANUAL")
            return True

        # ── Developer Mode commands (obediencia total + seguridad) ──
        if self._developer_mode:
            if self.current_user != self._owner_name:
                self._developer_mode = False
                self.speaker.say("Dueno no detectado. Developer Mode desactivado.")
                return True

            if self._is_dangerous(text):
                self._lockout_timer = Config.DEVELOPER_LOCK_OUT
                self.eye_renderer.set_expression(EyeExpression.ANGRY)
                self.speaker.say(
                    "No puedo hacer eso. Es peligroso para mi o para otros."
                )
                print(f"  [SEGURIDAD] Comando rechazado: {text}")
                return True

            print(f"  [DEVELOPER] Ejecutando: {text}")
            # Process direct commands
            if "adelante" in lower or "avanza" in lower:
                self.motors.forward(Config.MOTOR_MAX_SPEED)
                time.sleep(1.0)
                self.motors.stop()
            elif "atras" in lower or "retrocede" in lower:
                self.motors.backward(Config.MOTOR_MAX_SPEED)
                time.sleep(1.0)
                self.motors.stop()
            elif "gira izquierda" in lower or "a la izquierda" in lower:
                self.motors.turn_left(Config.MOTOR_MAX_SPEED)
                time.sleep(0.5)
                self.motors.stop()
            elif "gira derecha" in lower or "a la derecha" in lower:
                self.motors.turn_right(Config.MOTOR_MAX_SPEED)
                time.sleep(0.5)
                self.motors.stop()
            elif "empuja" in lower or "pala" in lower:
                self._push_object()
            elif "detente" in lower or "para" in lower or "stop" in lower:
                self.motors.stop()
            elif "musica" in lower and ("pon" in lower or "reproduce" in lower):
                cancion = lower.replace("pon", "").replace("reproduce", "").replace("musica", "").strip()
                if cancion and self.music_player:
                    self.music_player.play(cancion)
            elif "busca" in lower:
                query = lower.replace("busca", "").strip()
                if query and self.web_search:
                    self.eye_renderer.set_expression(EyeExpression.THINKING)
                    result = self.web_search.search_and_format(query)
                    self.speaker.say(result[:200])
            elif "saluda" in lower:
                self.speaker.say(f"Hola {self.current_user}! Como estas?")
            elif "que ves" in lower:
                self.eye_renderer.set_expression(EyeExpression.SEARCHING, speed=4)
                self.speaker.say("Estoy mirando a mi alrededor.")
            else:
                return False  # Dejar que la IA maneje
            return True

        return False  # No es comando especial

    def _process_voice(self, text: str):
        self._last_voice_text = text

        if self._handle_voice_command(text):
            return

        self.eye_renderer.set_expression(EyeExpression.THINKING)
        pygame.display.flip()

        context = {}
        if self.current_user:
            context["user_name"] = self.current_user
        if self.music_player and self.music_player.is_playing():
            context["current_song"] = self.music_player.current_song()
        sonar = self.sonar.read() if self.sonar and self.sonar.ready else {}
        context["sensors"] = sonar
        context["emotion"] = "curious"
        context["mode"] = "developer" if self._developer_mode else "auto"

        reply = self.brain.think(text, context)
        print(f"  [IA] {reply}")

        if "empuja" in text.lower() or "pala" in text.lower():
            self._push_object()

        self.eye_renderer.set_expression(EyeExpression.TALKING)
        self.speaker.say(reply)
        pygame.display.flip()
        time.sleep(0.3)

    def _listen_and_respond(self):
        self.eye_renderer.set_expression(EyeExpression.LISTENING)
        pygame.display.flip()

        text = self.stt.listen(timeout=4.0)
        if text is None:
            return

        print(f"  [Voz] {text}")
        self._process_voice(text)

    # ── Controller ──

    def _process_controller(self, dt: float):
        if not self.controller or not self.controller.connected:
            return
        self.controller.update(dt)

        look_x, look_y = self.controller.get_look()
        if abs(look_x) > 0.05 or abs(look_y) > 0.05:
            self.eye_renderer.set_look_target(look_x, look_y)

        for action in self.controller.actions:
            self._handle_controller_action(action)

    def _handle_controller_action(self, action: str):
        if action == ControllerAction.TALK:
            if self.current_user:
                self._listen_and_respond()
            else:
                self.speaker.say("No veo a nadie.")
        elif action == ControllerAction.STOP_MUSIC:
            if self.music_player:
                self.music_player.stop()
                self.speaker.say("Musica parada.")
        elif action == ControllerAction.DRIVE_MODE:
            self._developer_mode = False
            self.controller_drive = not self.controller_drive
            self._auto_mode = not self.controller_drive
            if self.controller_drive:
                self.speaker.say("Modo conduccion.")
                self.eye_renderer.set_expression(EyeExpression.DRIVE)
            else:
                self.speaker.say("Modo automatico.")
                self.motors.stop()
                self.eye_renderer.set_expression(EyeExpression.HAPPY)
        elif action == ControllerAction.LISTEN:
            self._listen_and_respond()
        elif action == ControllerAction.EXPR_HAPPY:
            self.eye_renderer.set_expression(EyeExpression.HAPPY, speed=6)
        elif action == ControllerAction.EXPR_SAD:
            self.eye_renderer.set_expression(EyeExpression.SAD, speed=6)
        elif action == ControllerAction.EXPR_ANGRY:
            self.eye_renderer.set_expression(EyeExpression.ANGRY, speed=6)
        elif action == ControllerAction.EXPR_SURPRISED:
            self.eye_renderer.set_expression(EyeExpression.SURPRISED, speed=6)
        elif action == ControllerAction.WAKE:
            self.eye_renderer.set_expression(EyeExpression.WAKING_UP, speed=4)
        elif action == ControllerAction.SLEEP:
            self.motors.stop()
            self.eye_renderer.set_expression(EyeExpression.SHUT_DOWN, speed=3)
            self.speaker.say("Buenas noches...")
        elif action == ControllerAction.SPEED_UP:
            self.controller.speed_mult = min(2.0, self.controller.speed_mult + 0.25)
        elif action == ControllerAction.SPEED_DOWN:
            self.controller.speed_mult = max(0.25, self.controller.speed_mult - 0.25)

    def _apply_controller_movement(self, speed: float, turn: float):
        if not self.motors:
            return
        dead = Config.CONTROLLER_DEADZONE
        max_spd = Config.CONTROLLER_DRIVE_SPEED
        if abs(speed) < dead and abs(turn) < dead:
            self.motors.stop()
            return
        left = int(clamp((speed + turn) * max_spd, -max_spd, max_spd))
        right = int(clamp((speed - turn) * max_spd, -max_spd, max_spd))
        self.motors.drive(left, right)

    # ── Main loop ──

    def run(self):
        self.running = True
        self._boot_animation()
        if self.speaker.engine:
            self.speaker.say(
                "Hola! Soy Botty. "
                "Estas usando una version de prueba de Botty Desktop. "
                "La version optimizada de Botty para escritorios. "
                "Esta en Alpha, nada de lo que ves es final."
            )

        print("  Bucle principal iniciado.")
        print("  ENTER: escribir mensaje | ESPACIO: voz | ESC: salir")

        while self.running:
            dt = self.clock.tick(Config.EYE_FPS) / 1000.0

            # ── Lockout timer decay ──
            if self._lockout_timer > 0:
                self._lockout_timer -= dt
                if self._lockout_timer <= 0:
                    self._lockout_timer = 0
                    if self._developer_mode:
                        self.eye_renderer.set_expression(EyeExpression.DEVELOPER)

            # ── Developer mode: verify owner still present ──
            if self._developer_mode and self.current_user:
                if self.current_user != self._owner_name:
                    self._developer_mode = False
                    self._auto_mode = True
                    self.speaker.say("Dueno no detectado. Modo normal.")
                    print("  [MODO] DEVELOPER MODE DESACTIVADO — dueno perdido")

            # ── Developer mode expression ──
            if self._developer_mode and self._lockout_timer <= 0:
                current = self.eye_renderer.get_expression()
                if current not in (EyeExpression.TALKING, EyeExpression.THINKING,
                                   EyeExpression.LISTENING, EyeExpression.ANGRY):
                    self.eye_renderer.set_expression(EyeExpression.DEVELOPER)

            # ── Music expression ──
            if self.music_player and self.music_player.is_playing():
                if self.eye_renderer.get_expression() not in (
                    EyeExpression.TALKING, EyeExpression.THINKING, EyeExpression.LISTENING,
                ):
                    self.eye_renderer.set_expression(EyeExpression.HAPPY)

            # ── Controller ──
            if self.controller and self.controller.connected:
                self._process_controller(dt)

            # ── Events ──
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self._typing_mode:
                            self._typing_mode = False
                            self._input_text = ""
                        else:
                            self.running = False
                    elif event.key == pygame.K_SPACE:
                        self._listen_and_respond()
                    elif event.key == pygame.K_RETURN:
                        if self._typing_mode:
                            if self._input_text.strip():
                                self._process_voice(self._input_text.strip())
                            self._typing_mode = False
                            self._input_text = ""
                        else:
                            self._typing_mode = True
                            self._input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        if self._typing_mode:
                            self._input_text = self._input_text[:-1]
                elif event.type == pygame.TEXTINPUT:
                    if self._typing_mode:
                        self._input_text += event.text
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._mouse_x, self._mouse_y = event.pos
                    self._on_mouse_touch(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self._mouse_x, self._mouse_y = event.pos
                elif event.type == pygame.FINGERDOWN:
                    w, h = self.eye_renderer.width, self.eye_renderer.height
                    fx, fy = event.x * w, event.y * h
                    self._mouse_x, self._mouse_y = int(fx), int(fy)
                    self._on_mouse_touch((int(fx), int(fy)))
                elif event.type == pygame.FINGERMOTION:
                    w, h = self.eye_renderer.width, self.eye_renderer.height
                    self._mouse_x = int(event.x * w)
                    self._mouse_y = int(event.y * h)

            # ── Voice queue (always listening) ──
            while not self._voice_queue.empty():
                text = self._voice_queue.get_nowait()
                print(f"  [Voz] {text}")
                self._process_voice(text)

            # ── Vision + behaviors (not in developer mode) ──
            if not self._developer_mode and not self._fleeing and not self._pushing:
                faces, objects = self._process_vision()
                if faces or objects:
                    self._handle_faces_and_objects(faces, objects)
                    if (time.time() - self.last_interaction > 3.0
                            and not self.speaker.is_speaking()
                            and self.current_user):
                        self._listen_and_respond()
                else:
                    self._handle_no_face()
                    self._autonomous_behavior(dt)

            # ── In developer mode: listen continuously if owner present ──
            if self._developer_mode and self.current_user == self._owner_name:
                if (time.time() - self.last_interaction > 2.0
                        and not self.speaker.is_speaking()):
                    self._listen_and_respond()

            # ── Motor override from controller ──
            if self.controller and self.controller.is_driving():
                speed, turn = self.controller.get_movement()
                self._apply_controller_movement(speed, turn)
            elif self.controller_drive and not self.controller.is_driving():
                self.motors.stop()

            # ── Mouse / touch tracking ──
            if self._mouse_reaction_timer > 0:
                self._mouse_reaction_timer -= dt
                if self._mouse_reaction_timer <= 0:
                    self.eye_renderer.set_expression(self._prev_expression, speed=6)
            else:
                mx, my = self._mouse_x, self._mouse_y
                cw, ch = self.eye_renderer.width, self.eye_renderer.height
                face_cx, face_cy = cw // 2, ch // 2
                rel_x = (mx - face_cx) / (cw // 2)
                rel_y = (my - face_cy) / (ch // 2)
                rel_x = max(-1.0, min(1.0, rel_x))
                rel_y = max(-1.0, min(1.0, rel_y))
                if abs(rel_x) > 0.05 or abs(rel_y) > 0.05:
                    self.eye_renderer.set_look_target(rel_x, rel_y)

            # ── Idle behavior (complaints, desktop hands, blinks) ──
            if (not self.current_user and not self._typing_mode
                    and self._mouse_reaction_timer <= 0
                    and not self.speaker.is_speaking()
                    and not self._developer_mode):
                self._idle_behavior_timer += dt
                if self._idle_behavior_timer > random.uniform(6.0, 15.0):
                    self._idle_behavior_timer = 0
                    # Desktop hands action
                    if self.desktop_hands and self.desktop_hands.is_available():
                        result = self.desktop_hands.do_playful_action()
                        if result:
                            pos = self.desktop_hands.get_target_position()
                            if pos:
                                screen_cx = self.eye_renderer.width // 2
                                screen_cy = self.eye_renderer.height // 2
                                rel_x = (pos[0] - screen_cx) / screen_cx
                                rel_y = (pos[1] - screen_cy) / screen_cy
                                rel_x = max(-1.0, min(1.0, rel_x))
                                rel_y = max(-1.0, min(1.0, rel_y))
                                self.eye_renderer.set_look_target(rel_x * 0.6, rel_y * 0.6)
                            self.eye_renderer.set_expression(
                                random.choice([EyeExpression.HAPPY, EyeExpression.SURPRISED,
                                               EyeExpression.LOVING]),
                                speed=5
                            )
                            if random.random() < 0.3 and self.speaker and self.speaker.engine:
                                self.speaker.say(
                                    random.choice([
                                        "A jugar!", "Mira esto!", "Ups!",
                                        "Jeje!", "A moverse!", "Tremendo!",
                                    ]),
                                    block=False
                                )
                        elif random.random() < 0.4 and self.speaker and self.speaker.engine:
                            msg = random.choice(self._idle_complaints)
                            self.speaker.say(msg, block=False)
                            self.eye_renderer.set_expression(
                                random.choice([EyeExpression.SAD, EyeExpression.SLEEPY,
                                               EyeExpression.CONFUSED]),
                                speed=5
                            )
                        else:
                            self.eye_renderer.trigger_blink()
                    else:
                        action = random.random()
                        if action < 0.4 and self.speaker and self.speaker.engine:
                            msg = random.choice(self._idle_complaints)
                            self.speaker.say(msg, block=False)
                            self.eye_renderer.set_expression(
                                random.choice([EyeExpression.SAD, EyeExpression.SLEEPY,
                                               EyeExpression.CONFUSED, EyeExpression.THINKING]),
                                speed=5
                            )
                        elif action < 0.7:
                            self.eye_renderer.trigger_blink()
                        else:
                            self.eye_renderer.set_expression(
                                random.choice([EyeExpression.SEARCHING, EyeExpression.SURPRISED,
                                               EyeExpression.HAPPY]),
                                speed=4
                            )

            # ── Eyes (pygame + OLED) ──
            self.eye_renderer.update(dt)
            self.eye_renderer.render(self.display_surface)

            # Text input overlay
            if self._typing_mode:
                try:
                    font = pygame.font.Font(None, 22)
                    hint = font.render("Escribe y presiona ENTER:", True, (180, 180, 190))
                    tx = (self.eye_renderer.width - hint.get_width()) // 2
                    self.display_surface.blit(hint, (tx, self.eye_renderer.height - 70))

                    bg = pygame.Rect(30, self.eye_renderer.height - 55,
                                     self.eye_renderer.width - 60, 30)
                    pygame.draw.rect(self.display_surface, (30, 30, 35), bg)
                    pygame.draw.rect(self.display_surface, (80, 80, 100), bg, 1)

                    txt = font.render(self._input_text + "|", True, (220, 220, 230))
                    self.display_surface.blit(txt, (38, self.eye_renderer.height - 52))
                except Exception:
                    pass

            pygame.display.flip()
            if self.oled_eyes:
                self.oled_eyes.set_expression(self.eye_renderer.get_expression())
                self.oled_eyes.update(dt)
                self.oled_eyes.render()

        self.shutdown()

    def shutdown(self):
        print("  Cerrando sistemas...")
        self._listener_running = False
        self._shutdown_animation()
        if self.speaker:
            self.speaker.stop()
        if self.music_player:
            self.music_player.stop()
        if self.camera:
            self.camera.release()
        if self.sonar:
            self.sonar.cleanup()
        if self.controller:
            self.controller.cleanup()
        if self.motors:
            self.motors.cleanup()
        if self.memory:
            self.memory.save()
        pygame.quit()
        print("  Botty se ha dormido. Hasta luego!")
        sys.exit(0)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def signal_handler(sig, frame):
    print("\n  Interrupcion recibida.")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    robot = BottyRobot()
    try:
        robot.init()
        robot.run()
    except KeyboardInterrupt:
        robot.shutdown()
    except Exception as e:
        print(f"\n  Error fatal: {e}")
        import traceback
        traceback.print_exc()
        try:
            robot.shutdown()
        except Exception:
            pygame.quit()
            sys.exit(1)


if __name__ == "__main__":
    main()
