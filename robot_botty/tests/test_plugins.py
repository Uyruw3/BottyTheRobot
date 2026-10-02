"""
Tests for plugin system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_VIDEODRIVER"] = "dummy"

from botty.plugins import PluginManager, BasePlugin, PluginEvent


class TestPlugin(BasePlugin):
    __test__ = False
    name = "test_plugin"
    version = "1.0.0"
    description = "Plugin de prueba"
    events = [PluginEvent.STARTUP, PluginEvent.TICK]
    priority = 5
    _event_log = []

    def on_load(self):
        self._event_log = []

    def on_event(self, event, data=None):
        self._event_log.append((event, data))
        return {"handled": True}


class TestPluginHighPrio(BasePlugin):
    __test__ = False
    name = "test_high"
    version = "1.0.0"
    events = [PluginEvent.TICK]
    priority = 100

    def on_event(self, event, data=None):
        return {"high_priority": True}


def test_plugin_manager_create():
    pm = PluginManager()
    assert pm is not None
    assert len(pm.plugins) == 0
    print("  OK test_plugin_manager_create")


def test_register_plugin():
    pm = PluginManager()
    plugin = TestPlugin()
    pm.plugins["test_plugin"] = plugin
    for evt in plugin.events:
        pm._event_handlers[evt].append(plugin)
    assert "test_plugin" in pm.plugins
    print("  OK test_register_plugin")


def test_emit_event():
    pm = PluginManager()
    plugin = TestPlugin()
    pm.plugins["test"] = plugin
    for evt in plugin.events:
        pm._event_handlers[evt].append(plugin)
    results = pm.emit(PluginEvent.STARTUP, {"msg": "hello"})
    assert len(results) > 0
    assert results[0]["handled"] is True
    print("  OK test_emit_event")


def test_priority_order():
    pm = PluginManager()
    low = TestPlugin()
    low.priority = 5
    low.name = "low"
    high = TestPluginHighPrio()
    pm.plugins["low"] = low
    pm.plugins["high"] = high
    pm._event_handlers[PluginEvent.TICK] = [low, high]
    results = pm.emit(PluginEvent.TICK)
    assert results[0].get("high_priority") is True
    print("  OK test_priority_order")


def test_disable_plugin():
    pm = PluginManager()
    plugin = TestPlugin()
    pm.plugins["test"] = plugin
    for evt in plugin.events:
        pm._event_handlers[evt].append(plugin)
    plugin.enabled = False
    results = pm.emit(PluginEvent.STARTUP)
    assert len(results) == 0
    print("  OK test_disable_plugin")


def test_unload_plugin():
    pm = PluginManager()
    plugin = TestPlugin()
    pm.plugins["test"] = plugin
    for evt in plugin.events:
        pm._event_handlers[evt].append(plugin)
    pm.unload("test")
    assert "test" not in pm.plugins
    print("  OK test_unload_plugin")


def test_list_plugins():
    pm = PluginManager()
    pm.plugins["a"] = TestPlugin()
    pm.plugins["b"] = TestPlugin()
    assert len(pm.list_plugins()) == 2
    print("  OK test_list_plugins")


def test_get_plugin():
    pm = PluginManager()
    p = TestPlugin()
    pm.plugins["test"] = p
    assert pm.get_plugin("test") is p
    assert pm.get_plugin("nonexistent") is None
    print("  OK test_get_plugin")


def test_cleanup():
    pm = PluginManager()
    p = TestPlugin()
    pm.plugins["test"] = p
    for evt in p.events:
        pm._event_handlers[evt].append(p)
    pm.cleanup()
    assert len(pm.plugins) == 0
    print("  OK test_cleanup")


if __name__ == "__main__":
    test_plugin_manager_create()
    test_register_plugin()
    test_emit_event()
    test_priority_order()
    test_disable_plugin()
    test_unload_plugin()
    test_list_plugins()
    test_get_plugin()
    test_cleanup()
    print("\nTodos los tests de plugins pasados!")
