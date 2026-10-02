"""
Tests for AI brain module.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_VIDEODRIVER"] = "dummy"

from botty.ai.brain import Brain, BrainCallError, TOOL_DEFINITIONS


class MockWebSearch:
    def search_and_format(self, query):
        return f"Resultados simulados para: {query}"


class MockMusicPlayer:
    def play(self, song):
        return True

    def is_playing(self):
        return False

    def current_song(self):
        return ""


def test_brain_create():
    b = Brain()
    assert b is not None
    assert b._system_prompt != ""
    print("  OK test_brain_create")


def test_brain_with_tools():
    b = Brain(web_search=MockWebSearch(), music_player=MockMusicPlayer())
    assert "buscar_en_internet" in b._system_prompt
    assert "reproducir_cancion" in b._system_prompt
    print("  OK test_brain_with_tools")


def test_brain_reset():
    b = Brain()
    b.conversation_history.append({"role": "user", "content": "test"})
    b.reset_conversation()
    assert len(b.conversation_history) == 0
    print("  OK test_brain_reset")


def test_build_messages():
    b = Brain()
    msgs = b._build_messages("Hola", {"user_name": "Juan", "emotion": "happy"})
    assert len(msgs) == 3
    assert msgs[0]["role"] == "system"
    assert msgs[-1]["role"] == "user"
    assert msgs[-1]["content"] == "Hola"
    print("  OK test_build_messages")


def test_build_messages_with_history():
    b = Brain()
    b.conversation_history.append({"role": "user", "content": "msg1"})
    b.conversation_history.append({"role": "assistant", "content": "resp1"})
    msgs = b._build_messages("msg2")
    assert len(msgs) >= 4
    print("  OK test_build_messages_with_history")


def test_tool_definitions_format():
    assert len(TOOL_DEFINITIONS) >= 2
    names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "buscar_en_internet" in names
    assert "reproducir_cancion" in names
    print("  OK test_tool_definitions_format")


def test_tool_defs_ollama():
    from botty.ai.brain import _tool_defs_ollama
    tools = _tool_defs_ollama()
    assert len(tools) >= 2
    for t in tools:
        assert "function" in t
        assert "name" in t["function"]
    print("  OK test_tool_defs_ollama")


def test_execute_tool_web_search():
    b = Brain(web_search=MockWebSearch())
    result = b._execute_tool("buscar_en_internet", {"consulta": "test"})
    assert "Resultados simulados" in result
    print("  OK test_execute_tool_web_search")


def test_execute_tool_music():
    b = Brain(music_player=MockMusicPlayer())
    result = b._execute_tool("reproducir_cancion", {"cancion": "test song"})
    assert "Reproduciendo" in result
    print("  OK test_execute_tool_music")


def test_execute_tool_unknown():
    b = Brain()
    result = b._execute_tool("unknown_tool", {})
    assert "Error" in result
    print("  OK test_execute_tool_unknown")


def test_execute_tool_no_web():
    b = Brain()
    result = b._execute_tool("buscar_en_internet", {"consulta": "test"})
    assert "Error" in result
    print("  OK test_execute_tool_no_web")


def test_system_prompt_contains_modes():
    b = Brain()
    assert "Modo Auto" in b._system_prompt
    assert "Modo Manual" in b._system_prompt
    assert "Developer Mode" in b._system_prompt
    print("  OK test_system_prompt_contains_modes")


if __name__ == "__main__":
    test_brain_create()
    test_brain_with_tools()
    test_brain_reset()
    test_build_messages()
    test_build_messages_with_history()
    test_tool_definitions_format()
    test_tool_defs_ollama()
    test_execute_tool_web_search()
    test_execute_tool_music()
    test_execute_tool_unknown()
    test_execute_tool_no_web()
    test_system_prompt_contains_modes()
    print("\nTodos los tests de brain pasados!")
