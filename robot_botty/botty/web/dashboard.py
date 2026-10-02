"""
Web dashboard — interfaz Flask para monitorear y controlar Botty.
Incluye camara, chat, control de modos y estadisticas en tiempo real.
"""

import os
import json
import threading
import time
import base64
import io
import queue

try:
    from flask import Flask, render_template, request, jsonify, Response, stream_with_context
    HAVE_FLASK = True
except ImportError:
    HAVE_FLASK = False

try:
    import cv2
except ImportError:
    cv2 = None

from botty.config import Config
from botty.eyes.animations import EyeExpression


class WebDashboard:
    def __init__(self, robot=None, host="0.0.0.0", port=5000):
        self.robot = robot
        self.host = host
        self.port = port
        self.app = (
            Flask(__name__, template_folder="templates", static_folder="static")
            if HAVE_FLASK else None
        )
        self._server_thread = None
        self._running = False
        self._command_queue = queue.Queue()
        self._frame_queue = queue.Queue(maxsize=10)
        self._log_queue = queue.Queue(maxsize=100)
        if self.app:
            self._setup_routes()

    def _setup_routes(self):
        app = self.app

        @app.route("/")
        def index():
            return render_template("dashboard.html")

        @app.route("/api/status")
        def api_status():
            if not self.robot:
                return jsonify({"error": "robot not connected"})
            r = self.robot
            mode = "auto"
            if r._developer_mode:
                mode = "developer"
            elif r.controller_drive:
                mode = "manual"
            return jsonify({
                "mode": mode,
                "auto_mode": r._auto_mode,
                "developer_mode": r._developer_mode,
                "controller_drive": r.controller_drive,
                "current_user": r.current_user,
                "last_interaction": time.time() - r.last_interaction if r.last_interaction else 0,
                "fleeing": r._fleeing,
                "pushing": r._pushing,
                "expression": r.eye_renderer.get_expression().value if r.eye_renderer else "none",
                "motor_enabled": Config.MOTOR_ENABLED,
                "sonar_enabled": Config.SONAR_ENABLED,
                "camera_ok": r.camera is not None,
                "controller_ok": r.controller and r.controller.connected,
                "listener_active": r._listener_running,
                "music_playing": r.music_player and r.music_player.is_playing(),
                "lockout": r._lockout_timer,
            })

        @app.route("/api/mode", methods=["POST"])
        def api_set_mode():
            data = request.get_json()
            mode = data.get("mode", "auto")
            if not self.robot:
                return jsonify({"error": "no robot"})
            if mode == "auto":
                self.robot._auto_mode = True
                self.robot._developer_mode = False
                self.robot.controller_drive = False
                self.robot.motors.stop()
                self.robot.eye_renderer.set_expression(EyeExpression.HAPPY)
                self._log("Modo automatico")
            elif mode == "manual":
                self.robot.controller_drive = True
                self.robot._auto_mode = False
                self.robot._developer_mode = False
                self.robot.motors.stop()
                self.robot.eye_renderer.set_expression(EyeExpression.DRIVE)
                self._log("Modo manual")
            elif mode == "developer":
                self.robot._developer_mode = True
                self.robot._auto_mode = False
                self.robot.controller_drive = False
                self.robot.eye_renderer.set_expression(EyeExpression.DEVELOPER)
                self._log("Developer mode")
            return jsonify({"status": "ok", "mode": mode})

        @app.route("/api/expression", methods=["POST"])
        def api_set_expression():
            data = request.get_json()
            expr_name = data.get("expression", "idle")
            if self.robot and self.robot.eye_renderer:
                for e in EyeExpression:
                    if e.value == expr_name:
                        self.robot.eye_renderer.set_expression(e, speed=8)
                        self._log(f"Expresion: {expr_name}")
                        return jsonify({"status": "ok"})
            return jsonify({"error": "invalid expression"}), 400

        @app.route("/api/speak", methods=["POST"])
        def api_speak():
            data = request.get_json()
            text = data.get("text", "")
            if self.robot and self.robot.speaker and text:
                self.robot.speaker.say(text)
                self._log(f"Hablando: {text}")
                return jsonify({"status": "ok"})
            return jsonify({"error": "no text"}), 400

        @app.route("/api/chat", methods=["POST"])
        def api_chat():
            data = request.get_json()
            message = data.get("message", "")
            if self.robot and self.robot.brain and message:
                self._log(f"Chat: {message}")
                context = {}
                if self.robot.current_user:
                    context["user_name"] = self.robot.current_user
                reply = self.robot.brain.think(message, context)
                self._log(f"IA: {reply}")
                if self.robot.speaker:
                    self.robot.speaker.say(reply)
                return jsonify({"reply": reply})
            return jsonify({"error": "no message"}), 400

        @app.route("/api/motor", methods=["POST"])
        def api_motor():
            data = request.get_json()
            cmd = data.get("command", "stop")
            speed = int(data.get("speed", Config.MOTOR_MAX_SPEED))
            if not self.robot or not self.robot.motors:
                return jsonify({"error": "motors not available"})
            if cmd == "forward":
                self.robot.motors.forward(speed)
            elif cmd == "backward":
                self.robot.motors.backward(speed)
            elif cmd == "left":
                self.robot.motors.turn_left(speed)
            elif cmd == "right":
                self.robot.motors.turn_right(speed)
            elif cmd == "stop":
                self.robot.motors.stop()
            return jsonify({"status": "ok", "cmd": cmd})

        @app.route("/api/sensors")
        def api_sensors():
            data = {}
            if self.robot and self.robot.sonar and self.robot.sonar.ready:
                data["sonar"] = self.robot.sonar.read()
            else:
                data["sonar"] = {}
            if self.robot and self.robot.motors and Config.MOTOR_ENABLED:
                data["motors"] = {"enabled": True}
            else:
                data["motors"] = {"enabled": False}
            return jsonify(data)

        @app.route("/api/emotion")
        def api_emotion():
            if hasattr(self.robot, "emotion") and self.robot.emotion:
                e = self.robot.emotion
                return jsonify({
                    "valence": round(e.mood.valence, 2),
                    "arousal": round(e.mood.arousal, 2),
                    "emotion": e.current_emotion.value,
                    "personality": e.personality,
                    "report": e.get_mood_report(),
                })
            return jsonify({"emotion": "unknown"})

        @app.route("/api/memory")
        def api_memory():
            if self.robot and self.robot.memory:
                names = list(self.robot.memory.faces.keys()) if hasattr(self.robot.memory, "faces") else []
                return jsonify({"faces": names})
            return jsonify({"faces": []})

        @app.route("/api/command", methods=["POST"])
        def api_command():
            data = request.get_json()
            cmd = data.get("command", "")
            if self.robot:
                self.robot._process_voice(cmd)
                return jsonify({"status": "ok"})
            return jsonify({"error": "no robot"}), 400

        @app.route("/api/logs")
        def api_logs():
            logs = []
            while not self._log_queue.empty():
                logs.append(self._log_queue.get_nowait())
            return jsonify({"logs": logs[-50:]})

        @app.route("/api/explore")
        def api_explore():
            if self.robot:
                return jsonify({
                    "fleeing": self.robot._fleeing,
                    "avoid_timer": self.robot._avoid_timer,
                    "explore_timer": self.robot._explore_timer,
                    "explore_dir": self.robot._explore_dir,
                })
            return jsonify({})

        @app.route("/video_feed")
        def video_feed():
            return Response(
                self._generate_frames(),
                mimetype="multipart/x-mixed-replace; boundary=frame"
            )

    def _generate_frames(self):
        while self._running:
            try:
                frame_data = self._frame_queue.get(timeout=1)
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_data + b"\r\n"
                )
            except queue.Empty:
                continue

    def _log(self, message: str):
        try:
            self._log_queue.put_nowait({"time": time.time(), "msg": message})
        except queue.Full:
            pass

    def push_frame(self, frame):
        if self._running:
            try:
                _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                self._frame_queue.put_nowait(buffer.tobytes())
            except Exception:
                pass

    def start(self):
        if not self.app:
            print("  [Web] Flask no instalado. Usa: pip install botty-prototype[web]")
            return False
        self._running = True
        self._server_thread = threading.Thread(
            target=self._run_server, daemon=True
        )
        self._server_thread.start()
        print(f"  [Web] Dashboard en http://{self.host}:{self.port}")
        return True

    def _run_server(self):
        try:
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        except Exception as e:
            print(f"  [Web] Error del servidor: {e}")
        self._running = False

    def stop(self):
        self._running = False
        print("  [Web] Dashboard detenido")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Botty Web Dashboard")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    dashboard = WebDashboard(host=args.host, port=args.port)
    if not dashboard.start():
        return
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        dashboard.stop()


if __name__ == "__main__":
    main()
