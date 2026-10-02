"""
Plugin examples — documentation and example code for creating plugins.
Shows various plugin patterns and use cases.
"""

PLUGIN_TEMPLATE = '''
"""
{name} plugin — {description}.
"""

from botty.plugins import BasePlugin, PluginEvent


class {class_name}(BasePlugin):
    name = "{name}"
    version = "1.0.0"
    description = "{description}"
    author = "Botty"
    events = [{events}]
    priority = {priority}

    def __init__(self, robot=None):
        super().__init__(robot)
        self._state = {{}}

    def on_event(self, event: str, data: dict) -> dict | None:
        if event == PluginEvent.{event_example}:
            return self._handle_event(data)
        return None

    def _handle_event(self, data: dict) -> dict:
        if self.robot:
            self.robot.speaker.say("Plugin {name} activado!")
        return {{"action": "{name}_triggered", "data": data}}

    def on_unload(self):
        pass
'''

PLUGIN_PATTERNS = {
    "voice_command": {
        "pattern": "Escucha comandos de voz y responde",
        "events": ["PluginEvent.VOICE_COMMAND"],
        "priority": 50,
        "example_trigger": "botty <comando>",
    },
    "timer": {
        "pattern": "Ejecuta acciones en intervalos regulares",
        "events": ["PluginEvent.IDLE_TICK"],
        "priority": 30,
        "example_trigger": "Cada N segundos",
    },
    "face_detection": {
        "pattern": "Reacciona cuando se detectan caras",
        "events": ["PluginEvent.FACE_RECOGNIZED", "PluginEvent.FACE_LOST"],
        "priority": 10,
        "example_trigger": "Al detectar una cara",
    },
    "emotion_reactive": {
        "pattern": "Cambia comportamiento segun la emocion",
        "events": ["PluginEvent.EMOTION_CHANGED", "PluginEvent.EXPRESSION_CHANGED"],
        "priority": 20,
        "example_trigger": "Cuando la emocion cambia",
    },
    "sensor_monitor": {
        "pattern": "Monitorea sensores y alerta",
        "events": ["PluginEvent.IDLE_TICK"],
        "priority": 40,
        "example_trigger": "Cada tick de idle",
    },
    "web_api": {
        "pattern": "Expone una API web adicional",
        "events": [],
        "priority": 60,
        "example_trigger": "HTTP request",
    },
    "music_reactive": {
        "pattern": "Reacciona cuando la musica cambia",
        "events": ["PluginEvent.MUSIC_STARTED", "PluginEvent.MUSIC_STOPPED"],
        "priority": 30,
        "example_trigger": "Al cambiar cancion",
    },
    "desktop_integration": {
        "pattern": "Interactua con el escritorio",
        "events": ["PluginEvent.IDLE_TICK"],
        "priority": 25,
        "example_trigger": "Cuando esta inactivo",
    },
}

PLUGIN_BEST_PRACTICES = [
    "Siempre hereda de BasePlugin y define name, version, description, events y priority.",
    "Usa __init__ para inicializar estado, pero no hagas operaciones pesadas.",
    "Implementa on_event() que recibe el evento y datos, retorna un dict o None.",
    "Usa priority bajo (0-10) para plugins que deben ejecutarse primero.",
    "Usa priority alto (50+) para plugins que deben ejecutarse al final.",
    "Maneja todos los eventos posibles en on_event() con condicionales.",
    "Usa self.robot para acceder al robot (speaker, eyes, memory, etc).",
    "Implementa on_unload() para limpiar recursos (threads, archivos, etc).",
    "Coloca tu plugin en ~/.botty/plugins/ para que sea descubierto automaticamente.",
    "Usa nombres de archivo unicos para evitar conflictos.",
    "Documenta tu plugin con un docstring al inicio del archivo.",
    "Usa constantes de PluginEvent en lugar de strings literales.",
    "Los plugins no deben bloquear el hilo principal (usa threads para tareas largas).",
    "Retorna un dict con informacion util para depuracion.",
    "Maneja errores gracefulmente, no dejes que un plugin rompa el sistema.",
]

PLUGIN_EVENT_REFERENCE = {
    "STARTUP": "Se emite cuando el robot inicia",
    "SHUTDOWN": "Se emite cuando el robot se apaga",
    "IDLE_TICK": "Se emite periodicamente cuando el robot esta inactivo",
    "VOICE_COMMAND": "Se emite cuando se recibe un comando de voz",
    "TEXT_COMMAND": "Se emite cuando se recibe un comando de texto",
    "FACE_RECOGNIZED": "Se emite cuando se reconoce una cara",
    "FACE_LOST": "Se emite cuando se pierde una cara",
    "EXPRESSION_CHANGED": "Se emite cuando cambia la expresion de los ojos",
    "EMOTION_CHANGED": "Se emite cuando cambia la emocion",
    "MUSIC_STARTED": "Se emite cuando comienza la musica",
    "MUSIC_STOPPED": "Se emite cuando se detiene la musica",
    "OBSTACLE_DETECTED": "Se emite cuando se detecta un obstaculo",
    "MODE_CHANGED": "Se emite cuando cambia el modo de operacion",
    "USER_JOINED": "Se emite cuando un usuario se conecta",
    "USER_LEFT": "Se emite cuando un usuario se desconecta",
    "TIMER_TICK": "Se emite en intervalos regulares de tiempo",
    "SENSOR_UPDATE": "Se emite cuando los sensores se actualizan",
    "MEMORY_RECALL": "Se emite cuando se recupera un recuerdo",
    "CONTROLLER_INPUT": "Se emite cuando se recibe input del mando",
    "BATTERY_LOW": "Se emite cuando la bateria esta baja",
    "NETWORK_STATUS": "Se emite cuando cambia el estado de red",
    "DEVELOPER_COMMAND": "Se emite para comandos de desarrollador",
    "PLUGIN_LOADED": "Se emite cuando un plugin se carga",
    "PLUGIN_UNLOADED": "Se emite cuando un plugin se descarga",
    "ERROR_OCCURRED": "Se emite cuando ocurre un error",
}

if __name__ == "__main__":
    print("=== Plugin Examples ===")
    print(f"Templates: {len(PLUGIN_PATTERNS)} patterns")
    print(f"Best Practices: {len(PLUGIN_BEST_PRACTICES)} tips")
    print(f"Events: {len(PLUGIN_EVENT_REFERENCE)} events")
    print()
    print("Template example:")
    print(PLUGIN_TEMPLATE.format(
        name="hello_world",
        class_name="HelloWorldPlugin",
        description="Plugin de ejemplo que saluda",
        events="PluginEvent.VOICE_COMMAND",
        priority=50,
        event_example="VOICE_COMMAND",
    ))
