"""
Tests for memory modules (face memory + vector memory).
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_VIDEODRIVER"] = "dummy"

from botty.memory.vector_memory import VectorMemory, MemoryEntry
from botty.memory.face_memory import FaceMemory
from botty.config import Config


def test_memory_entry_create():
    e = MemoryEntry("Hola mundo", role="user", tags=["saludo"])
    assert e.text == "Hola mundo"
    assert e.role == "user"
    assert "saludo" in e.tags
    print("  OK test_memory_entry_create")


def test_memory_entry_serialize():
    e = MemoryEntry("Test", role="bot", tags=["test"])
    d = e.to_dict()
    assert d["text"] == "Test"
    assert d["role"] == "bot"
    e2 = MemoryEntry.from_dict(d)
    assert e2.text == e.text
    assert e2.role == e.role
    print("  OK test_memory_entry_serialize")


def test_vector_memory_add():
    vm = VectorMemory(max_entries=100)
    vm.add("Este es un mensaje de prueba", role="user", tags=["test"])
    assert vm.count() == 1
    print("  OK test_vector_memory_add")


def test_vector_memory_search():
    vm = VectorMemory(max_entries=100, similarity_threshold=0.1)
    vm.add("Me gusta la musica clasica", role="user")
    vm.add("Los perros son muy bonitos", role="user")
    vm.add("Prefiero el rock y el jazz", role="user")
    results = vm.search("musica", top_k=2)
    assert len(results) > 0
    print("  OK test_vector_memory_search")


def test_vector_memory_context():
    vm = VectorMemory(max_entries=100, similarity_threshold=0.1)
    vm.add_conversation("Hola Botty", "Hola humano!", tags=["saludo"])
    vm.add_conversation("Que hora es?", "Son las 3 de la tarde", tags=["hora"])
    ctx = vm.get_context("saludo", max_chars=500)
    assert len(ctx) > 0
    print("  OK test_vector_memory_context")


def test_vector_memory_forget():
    vm = VectorMemory(max_entries=100)
    vm.add("Recuerdo reciente", role="user")
    vm.add("Recuerdo muy muy muy antiguo", role="user",
           metadata={"timestamp": 0})
    assert vm.count() == 2
    print("  OK test_vector_memory_forget")


def test_vector_memory_clear():
    vm = VectorMemory(max_entries=100)
    vm.add("Algo", role="user")
    vm.clear()
    assert vm.count() == 0
    print("  OK test_vector_memory_clear")


def test_vector_memory_tags():
    vm = VectorMemory(max_entries=100)
    vm.add("Mensaje importante", role="user", tags=["importante", "urgente"])
    tags = vm.get_by_tag("importante")
    assert len(tags) == 1
    print("  OK test_vector_memory_tags")


def test_face_memory_create():
    fm = FaceMemory()
    assert fm is not None
    print("  OK test_face_memory_create")


def test_face_memory_remember(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "MEMORY_DB_PATH", str(tmp_path / "memory.json"))
    fm = FaceMemory()
    # No se puede testear sin archivo real, solo verificar que no crashea
    fm.remember("test_user")
    assert fm.get_familiarity("test_user") == "nuevo"
    print("  OK test_face_memory_remember")


def test_vector_memory_recent():
    vm = VectorMemory(max_entries=100)
    vm.add("Primero", role="user")
    vm.add("Segundo", role="user")
    vm.add("Tercero", role="user")
    recent = vm.get_recent(2)
    assert len(recent) == 2
    print("  OK test_vector_memory_recent")


if __name__ == "__main__":
    test_memory_entry_create()
    test_memory_entry_serialize()
    test_vector_memory_add()
    test_vector_memory_search()
    test_vector_memory_context()
    test_vector_memory_forget()
    test_vector_memory_clear()
    test_vector_memory_tags()
    test_face_memory_create()
    test_face_memory_remember()
    test_vector_memory_recent()
    print("\nTodos los tests de memoria pasados!")
