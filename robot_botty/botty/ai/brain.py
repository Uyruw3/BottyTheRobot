"""
AI Brain module — integra OpenAI GPT y Ollama local con tool calling.
Puede buscar en internet, reproducir musica, recordar conversaciones y mas.
Version robot: incluye control de robot, limitador de tasa y resumen.
"""

import json
import urllib.request
import threading
import time
import hashlib
from datetime import datetime
from botty.config import Config


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_en_internet",
            "description": "Busca informacion actualizada en internet sobre cualquier tema",
            "parameters": {
                "type": "object",
                "properties": {
                    "consulta": {"type": "string", "description": "La consulta de busqueda"}
                },
                "required": ["consulta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reproducir_cancion",
            "description": "Busca y reproduce una cancion desde YouTube",
            "parameters": {
                "type": "object",
                "properties": {
                    "cancion": {"type": "string", "description": "Nombre de la cancion o artista"}
                },
                "required": ["cancion"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_clima",
            "description": "Obtiene el clima actual para una ciudad",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {"type": "string", "description": "Nombre de la ciudad"}
                },
                "required": ["ciudad"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "contar_chiste",
            "description": "Cuenta un chiste aleatorio de la base de datos local",
            "parameters": {
                "type": "object",
                "properties": {
                    "tema": {"type": "string", "description": "Tema del chiste (opcional)"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "poner_expresion",
            "description": "Cambia la expresion facial de Botty",
            "parameters": {
                "type": "object",
                "properties": {
                    "expresion": {
                        "type": "string",
                        "enum": ["happy", "sad", "angry", "surprised", "sleepy",
                                 "loving", "confused", "thinking", "searching", "idle"],
                        "description": "La expresion a mostrar",
                    }
                },
                "required": ["expresion"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cambiar_modo",
            "description": "Cambia el modo de operacion de Botty",
            "parameters": {
                "type": "object",
                "properties": {
                    "modo": {
                        "type": "string",
                        "enum": ["auto", "manual", "developer"],
                        "description": "Modo de operacion",
                    }
                },
                "required": ["modo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "enviar_comando_robot",
            "description": "Envia un comando directo al robot",
            "parameters": {
                "type": "object",
                "properties": {
                    "comando": {
                        "type": "string",
                        "enum": ["avanzar", "retroceder", "girar_izquierda",
                                 "girar_derecha", "detenerse"],
                        "description": "El comando a ejecutar",
                    }
                },
                "required": ["comando"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_estado_robot",
            "description": "Obtiene el estado actual del robot",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recordatorio",
            "description": "Establece un recordatorio para el futuro",
            "parameters": {
                "type": "object",
                "properties": {
                    "mensaje": {"type": "string", "description": "Mensaje del recordatorio"},
                    "segundos": {"type": "number", "description": "Segundos hasta el recordatorio"},
                },
                "required": ["mensaje", "segundos"],
            },
        },
    },
]


def _tool_defs_ollama():
    tools = []
    for td in TOOL_DEFINITIONS:
        fn = td["function"]
        tools.append({
            "type": "function",
            "function": {
                "name": fn["name"],
                "description": fn["description"],
                "parameters": fn["parameters"],
            },
        })
    return tools


class RateLimiter:
    def __init__(self, max_calls=15, window_seconds=60):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = []
        self._lock = threading.Lock()

    def allow(self):
        with self._lock:
            now = time.time()
            self.calls = [c for c in self.calls if now - c < self.window_seconds]
            if len(self.calls) >= self.max_calls:
                return False
            self.calls.append(now)
            return True

    def wait_time(self):
        with self._lock:
            if len(self.calls) < self.max_calls:
                return 0
            return max(0, self.window_seconds - (time.time() - min(self.calls)))


class RetryHandler:
    def __init__(self, max_retries=3, base_delay=1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    def execute(self, fn, *args, **kwargs):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return fn(*args, **kwargs)
            except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.base_delay * (2 ** attempt))
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.base_delay)
        raise last_error


class ReminderManager:
    def __init__(self):
        self._reminders = []
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def add_reminder(self, message, seconds, callback=None):
        fire_time = time.time() + seconds
        with self._lock:
            self._reminders.append({
                "message": message,
                "fire_time": fire_time,
                "callback": callback,
                "fired": False,
            })
            self._reminders.sort(key=lambda r: r["fire_time"])
        return f"Recordatorio establecido para dentro de {seconds} segundos: {message}"

    def _run(self):
        while self._running:
            now = time.time()
            to_fire = []
            with self._lock:
                remaining = []
                for r in self._reminders:
                    if not r["fired"] and r["fire_time"] <= now:
                        to_fire.append(r)
                    elif not r["fired"]:
                        remaining.append(r)
                self._reminders = remaining
            for r in to_fire:
                if r["callback"]:
                    try:
                        r["callback"](r["message"])
                    except Exception:
                        pass
            time.sleep(0.5)


class BrainCallError(Exception):
    pass


class Brain:
    def __init__(self, web_search=None, music_player=None, memory=None, emotion=None,
                 robot_controller=None):
        self.conversation_history = []
        self._system_prompt = Config.AI_SYSTEM_PROMPT
        self.web_search = web_search
        self.music_player = music_player
        self.memory = memory
        self.emotion = emotion
        self.robot_controller = robot_controller
        self._max_history = 20
        self._thinking = False
        self._lock = threading.Lock()
        self._tools_enabled = True
        self._response_callbacks = []
        self._rate_limiter = RateLimiter(max_calls=15, window_seconds=60)
        self._retry_handler = RetryHandler(max_retries=3, base_delay=1.0)
        self._reminder_manager = ReminderManager()
        self._total_queries = 0

        if self.web_search:
            self._system_prompt += (
                "\n\nTienes acceso a Internet. Cuando alguien te pregunte algo que no sabes "
                "o pida informacion actualizada, usa la herramienta 'buscar_en_internet'."
            )
        if self.music_player:
            self._system_prompt += (
                "\n\nPuedes reproducir musica. Si alguien te pide una cancion, "
                "usa la herramienta 'reproducir_cancion'."
            )
        if self.memory:
            self._system_prompt += (
                "\n\nTienes memoria a largo plazo. Recuerdas conversaciones anteriores "
                "y puedes usarlas para dar contexto."
            )
        if self.robot_controller:
            self._system_prompt += (
                "\n\nPuedes controlar el robot directamente. Usa 'enviar_comando_robot' "
                "para moverlo y 'obtener_estado_robot' para ver sus sensores."
            )
        self._system_prompt += (
            "\n\nModos de operacion:\n"
            "- Modo Auto: el robot se mueve autonomamente evitando obstaculos.\n"
            "- Modo Manual: el usuario controla el robot con un mando.\n"
            "- Developer Mode: solo el dueno activado."
        )

    def add_response_callback(self, callback):
        self._response_callbacks.append(callback)

    def reset_conversation(self):
        with self._lock:
            self.conversation_history = []

    def get_conversation_summary(self) -> str:
        with self._lock:
            if not self.conversation_history:
                return "No hay conversaciones previas."
            last = self.conversation_history[-6:]
            lines = []
            for msg in last:
                role = "Usuario" if msg["role"] == "user" else "Botty"
                content = msg["content"][:100]
                lines.append(f"{role}: {content}")
            return "\n".join(lines)

    def is_thinking(self) -> bool:
        return self._thinking

    def get_total_queries(self) -> int:
        return self._total_queries

    def think(self, user_input: str, context: dict | None = None) -> str:
        with self._lock:
            self._thinking = True
        self._total_queries += 1
        try:
            if not self._rate_limiter.allow():
                wait = self._rate_limiter.wait_time()
                return f"Muchas solicitudes. Espera {wait:.0f}s por favor."
            if Config.AI_PROVIDER == "ollama":
                reply = self._think_ollama(user_input, context)
            else:
                reply = self._think_openai(user_input, context)
            for cb in self._response_callbacks:
                try:
                    cb(reply)
                except Exception:
                    pass
            return reply
        finally:
            with self._lock:
                self._thinking = False

    def think_stream(self, user_input: str, context: dict | None = None):
        self._total_queries += 1
        if Config.AI_PROVIDER == "ollama":
            return self._think_ollama_stream(user_input, context)
        return self._think_openai(user_input, context)

    def _build_messages(self, user_input: str, context: dict | None = None,
                       memory_context: str = ""):
        messages = [{"role": "system", "content": self._system_prompt}]

        if context:
            ctx_str = "Contexto actual: "
            if "user_name" in context:
                ctx_str += f"Estas hablando con {context['user_name']}. "
            if "emotion" in context:
                ctx_str += f"Estado emocional: {context['emotion']}. "
            if "expression" in context:
                ctx_str += f"Expresion: {context['expression']}. "
            if "mode" in context:
                ctx_str += f"Modo: {context['mode']}. "
            if "battery" in context:
                ctx_str += f"Bateria: {context['battery']}%. "
            messages.append({"role": "system", "content": ctx_str})

        if memory_context:
            messages.append({"role": "system",
                           "content": f"Memoria de conversaciones previas:\n{memory_context}"})

        for msg in self.conversation_history[-self._max_history:]:
            messages.append(msg)

        messages.append({"role": "user", "content": user_input})
        return messages

    def _execute_tool(self, name: str, args: dict) -> str:
        if name == "buscar_en_internet":
            if not self.web_search:
                return "Error: busqueda web no disponible"
            query = args.get("consulta", args.get("query", ""))
            print(f"  [Brain] Buscando en internet: {query}")
            try:
                result = self.web_search.search_and_format(query)
                return result or "No se encontraron resultados."
            except Exception as e:
                return f"Error en busqueda: {e}"

        elif name == "reproducir_cancion":
            if not self.music_player:
                return "Error: reproductor no disponible"
            song = args.get("cancion", args.get("song", ""))
            print(f"  [Brain] Reproduciendo: {song}")
            try:
                ok = self.music_player.play(song)
                return f"Reproduciendo: {song}" if ok else f"No pude reproducir: {song}"
            except Exception as e:
                return f"Error al reproducir: {e}"

        elif name == "obtener_clima":
            ciudad = args.get("ciudad", "Madrid")
            print(f"  [Brain] Clima para: {ciudad}")
            if self.web_search:
                try:
                    return self.web_search.search_simple(f"clima {ciudad} 2026")
                except Exception as e:
                    return f"No pude obtener clima de {ciudad}: {e}"
            return f"No puedo consultar clima sin internet."

        elif name == "contar_chiste":
            tema = args.get("tema", "")
            try:
                from botty.knowledge.jokes import LARGE_JOKE_COLLECTION
                import random
                jokes = LARGE_JOKE_COLLECTION
                if tema:
                    temas = [j for j in jokes if tema.lower() in j.lower()]
                    if temas:
                        jokes = temas
                return random.choice(jokes) if jokes else "No tengo chistes de ese tema."
            except Exception:
                return "Por que los robots no juegan al escondite? Porque tienen miedo de quedarse sin bateria!"

        elif name == "poner_expresion":
            expr = args.get("expresion", "happy")
            print(f"  [Brain] Expresion: {expr}")
            if hasattr(self, '_expression_callback') and self._expression_callback:
                try:
                    self._expression_callback(expr)
                except Exception:
                    pass
            return f"Expresion cambiada a {expr}."

        elif name == "cambiar_modo":
            mode = args.get("modo", "auto")
            print(f"  [Brain] Modo: {mode}")
            if hasattr(self, '_mode_callback') and self._mode_callback:
                try:
                    self._mode_callback(mode)
                except Exception:
                    pass
            return f"Modo cambiado a {mode}."

        elif name == "enviar_comando_robot":
            if not self.robot_controller:
                return "Error: controlador no disponible"
            comando = args.get("comando", "")
            print(f"  [Brain] Comando robot: {comando}")
            try:
                resultado = self.robot_controller.execute(comando)
                return f"Comando '{comando}' ejecutado: {resultado}"
            except Exception as e:
                return f"Error al ejecutar '{comando}': {e}"

        elif name == "obtener_estado_robot":
            if not self.robot_controller:
                return "Error: controlador no disponible"
            try:
                estado = self.robot_controller.get_status()
                return json.dumps(estado, ensure_ascii=False)
            except Exception as e:
                return f"Error al obtener estado: {e}"

        elif name == "recordatorio":
            mensaje = args.get("mensaje", "")
            segundos = args.get("segundos", 60)
            self._reminder_manager.start()
            def callback(msg):
                print(f"  [Brain] Recordatorio: {msg}")
                if self.music_player:
                    self.music_player.play_sound("notification")
            return self._reminder_manager.add_reminder(mensaje, segundos, callback)

        return f"Error: herramienta desconocida '{name}'"

    def set_expression_callback(self, callback):
        self._expression_callback = callback

    def set_mode_callback(self, callback):
        self._mode_callback = callback

    def _call_openai_with_tools(self, messages: list) -> tuple[str, list]:
        from openai import OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        tools = TOOL_DEFINITIONS if self._tools_enabled else None
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=messages,
            max_tokens=Config.OPENAI_MAX_TOKENS,
            temperature=Config.OPENAI_TEMPERATURE,
            tools=tools,
        )
        msg = response.choices[0].message
        return msg.content or "", msg.tool_calls or []

    def _call_openai_stream(self, messages: list):
        from openai import OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        stream = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=messages,
            max_tokens=Config.OPENAI_MAX_TOKENS,
            temperature=Config.OPENAI_TEMPERATURE,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content

    def _think_with_api(self, user_input: str, context: dict | None,
                        call_api, api_name: str) -> str:
        memory_context = ""
        if self.memory:
            try:
                ctx = self.memory.get_context(user_input, top_k=3)
                memory_context = ctx if ctx else ""
            except Exception:
                pass

        messages = self._build_messages(user_input, context, memory_context)

        try:
            reply_text, tool_calls = call_api(messages)
            round_num = 0
            while tool_calls and round_num < 5:
                round_num += 1
                if api_name == "OpenAI":
                    tool_msg = {
                        "role": "assistant",
                        "content": reply_text,
                        "tool_calls": [
                            {"id": tc.id, "type": "function",
                             "function": {"name": tc.function.name,
                                         "arguments": tc.function.arguments}}
                            for tc in tool_calls
                        ],
                    }
                    messages.append(tool_msg)
                    for tc in tool_calls:
                        try:
                            args = json.loads(tc.function.arguments)
                        except json.JSONDecodeError:
                            args = {}
                        result = self._execute_tool(tc.function.name, args)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        })
                else:
                    ollama_tool_calls = []
                    for tc in tool_calls:
                        fn = tc.get("function", {})
                        ollama_tool_calls.append({
                            "name": fn.get("name", ""),
                            "arguments": fn.get("arguments", {}),
                        })
                    tool_msg = {
                        "role": "assistant",
                        "content": reply_text,
                        "tool_calls": [
                            {"type": "function",
                             "function": {"name": tc["name"],
                                         "arguments": json.dumps(tc["arguments"])}}
                            for tc in ollama_tool_calls
                        ],
                    }
                    messages.append(tool_msg)
                    for tc in ollama_tool_calls:
                        result = self._execute_tool(tc["name"], tc["arguments"])
                        messages.append({
                            "role": "tool",
                            "content": result,
                        })
                reply_text, tool_calls = call_api(messages)

            if not reply_text.strip():
                reply_text = "..."

            if self.emotion:
                try:
                    self.emotion.analyze_conversation(user_input)
                except Exception:
                    pass

        except Exception as e:
            reply_text = f"Error con {api_name}: {e}"

        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": reply_text})

        if len(self.conversation_history) > self._max_history * 2:
            self.conversation_history = self.conversation_history[-self._max_history:]

        if self.memory:
            try:
                self.memory.add_conversation(user_input, reply_text, tags=["chat"])
            except Exception:
                pass

        return reply_text

    def _think_openai(self, user_input: str, context: dict | None = None) -> str:
        def call_with_retry(messages):
            return self._retry_handler.execute(self._call_openai_with_tools, messages)
        return self._think_with_api(user_input, context, call_with_retry, "OpenAI")

    def _call_ollama_with_tools(self, messages: list) -> tuple[str, list]:
        tools = _tool_defs_ollama() if self._tools_enabled else None
        payload = {
            "model": Config.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": Config.OPENAI_MAX_TOKENS,
                "temperature": Config.OPENAI_TEMPERATURE,
            },
        }
        if tools:
            payload["tools"] = tools

        req = urllib.request.Request(
            f"{Config.OLLAMA_URL}/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())

        msg = data.get("message", {})
        reply_text = msg.get("content", "") or ""
        raw_tools = msg.get("tool_calls", [])
        return reply_text, raw_tools

    def _call_ollama_stream(self, messages: list):
        payload = {
            "model": Config.OLLAMA_MODEL,
            "messages": messages,
            "stream": True,
            "options": {
                "num_predict": Config.OPENAI_MAX_TOKENS,
                "temperature": Config.OPENAI_TEMPERATURE,
            },
        }
        req = urllib.request.Request(
            f"{Config.OLLAMA_URL}/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            for line in resp:
                if line:
                    try:
                        chunk = json.loads(line.decode().strip())
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

    def _think_ollama(self, user_input: str, context: dict | None = None) -> str:
        def call_with_retry(messages):
            return self._retry_handler.execute(self._call_ollama_with_tools, messages)
        return self._think_with_api(user_input, context, call_with_retry, "Ollama")

    def _think_ollama_stream(self, user_input: str, context: dict | None = None):
        messages = self._build_messages(user_input, context)
        full_response = ""
        for chunk in self._call_ollama_stream(messages):
            full_response += chunk
            yield chunk
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": full_response})

    def _think_openai_stream(self, user_input: str, context: dict | None = None):
        messages = self._build_messages(user_input, context)
        full_response = ""
        for chunk in self._call_openai_stream(messages):
            full_response += chunk
            yield chunk
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": full_response})

    def generate_system_prompt_with_context(self, additional_context: str = "") -> str:
        prompt = self._system_prompt
        if additional_context:
            prompt += f"\n\nContexto adicional: {additional_context}"
        return prompt

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def enable_tools(self, enabled: bool):
        self._tools_enabled = enabled

    def set_max_history(self, max_history: int):
        self._max_history = max(5, min(100, max_history))

    def get_max_history(self) -> int:
        return self._max_history

    def export_conversation_history(self, filepath: str) -> bool:
        try:
            with self._lock:
                data = {
                    "export_time": datetime.now().isoformat(),
                    "total_messages": len(self.conversation_history),
                    "conversation": self.conversation_history,
                }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"  [Brain] Error exporting: {e}")
            return False

    def set_robot_controller(self, controller):
        self.robot_controller = controller

    def get_robot_controller(self):
        return self.robot_controller
