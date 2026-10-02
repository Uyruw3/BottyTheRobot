"""
Plugin manager — descubre, carga y ejecuta plugins.
Soporta hooks de eventos y ciclo de vida.
"""

import os
import sys
import importlib
import inspect
import time
import traceback
from pathlib import Path

from .event_types import PluginEvent


class BasePlugin:
    name = "base"
    version = "0.1.0"
    description = ""
    author = ""
    events = []
    priority = 0

    def __init__(self, robot=None):
        self.robot = robot
        self.enabled = True

    def on_load(self):
        pass

    def on_unload(self):
        pass

    def on_event(self, event: str, data: dict = None) -> dict | None:
        return None

    def __str__(self):
        return f"{self.name} v{self.version}"


class PluginManager:
    def __init__(self, robot=None):
        self.robot = robot
        self.plugins: dict[str, BasePlugin] = {}
        self._event_handlers: dict[str, list[BasePlugin]] = {e: [] for e in PluginEvent.ALL}
        self._plugin_dirs = []
        self._discover_plugin_dirs()

    def _discover_plugin_dirs(self):
        self._plugin_dirs = []
        pkg_dir = Path(__file__).parent
        examples_dir = pkg_dir / "examples"
        if examples_dir.exists():
            self._plugin_dirs.append(str(examples_dir))
        home_plugins = Path.home() / ".botty" / "plugins"
        if home_plugins.exists():
            self._plugin_dirs.append(str(home_plugins))
        if "BOTTY_PLUGINS" in os.environ:
            for p in os.environ["BOTTY_PLUGINS"].split(os.pathsep):
                if Path(p).exists():
                    self._plugin_dirs.append(p)

    def discover(self) -> list[str]:
        found = []
        for d in self._plugin_dirs:
            p = Path(d)
            if not p.exists():
                continue
            for f in p.glob("*.py"):
                if f.name.startswith("_"):
                    continue
                name = f.stem
                if name not in self.plugins:
                    found.append(str(f))
        return found

    def load_plugin(self, filepath: str) -> BasePlugin | None:
        path = Path(filepath)
        name = path.stem
        if name in self.plugins:
            return self.plugins[name]

        try:
            spec = importlib.util.spec_from_file_location(name, filepath)
            if spec is None or spec.loader is None:
                print(f"  [Plugins] No se pudo cargar {name}")
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and issubclass(obj, BasePlugin)
                        and obj is not BasePlugin):
                    instance = obj(robot=self.robot)
                    instance.on_load()
                    self.plugins[name] = instance
                    if instance.events:
                        for evt in instance.events:
                            if evt in self._event_handlers:
                                self._event_handlers[evt].append(instance)
                    print(f"  [Plugins] Cargado: {instance}")
                    return instance
            print(f"  [Plugins] {name}: no se encontro clase Plugin")
            return None
        except Exception as e:
            print(f"  [Plugins] Error cargando {name}: {e}")
            traceback.print_exc()
            return None

    def load_all(self):
        for fp in self.discover():
            self.load_plugin(fp)

    def unload(self, name: str):
        if name in self.plugins:
            plugin = self.plugins[name]
            plugin.on_unload()
            for evt in plugin.events:
                if evt in self._event_handlers:
                    self._event_handlers[evt] = [
                        p for p in self._event_handlers[evt] if p is not plugin
                    ]
            del self.plugins[name]
            print(f"  [Plugins] Descargado: {name}")

    def enable_plugin(self, name: str):
        plugin = self.plugins.get(name)
        if plugin is not None:
            plugin.enabled = True

    def disable_plugin(self, name: str):
        plugin = self.plugins.get(name)
        if plugin is not None:
            plugin.enabled = False

    def emit(self, event: str, data: dict = None) -> list[dict]:
        results = []
        for plugin in sorted(self._event_handlers.get(event, []),
                             key=lambda p: p.priority, reverse=True):
            if not plugin.enabled:
                continue
            try:
                result = plugin.on_event(event, data or {})
                if result is not None:
                    results.append(result)
            except Exception as e:
                print(f"  [Plugins] Error en {plugin.name}.{event}: {e}")
        return results

    def dispatch_event(self, event: str, data: dict = None) -> list[dict]:
        return self.emit(event, data)

    def get_plugin(self, name: str) -> BasePlugin | None:
        return self.plugins.get(name)

    def list_plugins(self) -> list[BasePlugin]:
        return sorted(self.plugins.values(), key=lambda plugin: plugin.priority)

    def reload_all(self):
        names = list(self.plugins.keys())
        for name in names:
            self.unload(name)
        self.load_all()

    def cleanup(self):
        for plugin in list(self.plugins.values()):
            try:
                plugin.on_unload()
            except Exception:
                pass
        self.plugins.clear()
        self._event_handlers = {e: [] for e in PluginEvent.ALL}
