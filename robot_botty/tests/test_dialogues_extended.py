"""
Tests for extended dialogue data — contextual responses, personality traits, extended topics.
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from botty.data.dialogues_extended import (
    DIALOGUES_EXTENDED, DIALOGUES_EXTENDED_TOPICS,
    DIALOGUES_EXTENDED_KEYWORDS, CONTEXTUAL_RESPONSES,
)


class TestExtendedDialogues:
    def test_extended_dialogues_exist(self):
        assert len(DIALOGUES_EXTENDED) >= 10
        assert "salud" in DIALOGUES_EXTENDED
        assert "educacion" in DIALOGUES_EXTENDED
        assert "naturaleza" in DIALOGUES_EXTENDED
        assert "programacion" in DIALOGUES_EXTENDED
        assert "musica" in DIALOGUES_EXTENDED
        assert "viajes" in DIALOGUES_EXTENDED
        assert "arte" in DIALOGUES_EXTENDED
        assert "ciencia" in DIALOGUES_EXTENDED
        assert "tecnologia" in DIALOGUES_EXTENDED
        assert "deportes" in DIALOGUES_EXTENDED
        assert "alimentacion" in DIALOGUES_EXTENDED
        assert "lectura" in DIALOGUES_EXTENDED

    def test_all_topics_have_responses(self):
        for topic in DIALOGUES_EXTENDED:
            assert len(DIALOGUES_EXTENDED[topic]) >= 5, f"{topic} has too few responses"
            for response in DIALOGUES_EXTENDED[topic]:
                assert isinstance(response, str)
                assert len(response) > 10

    def test_all_topics_in_topic_list(self):
        for topic in DIALOGUES_EXTENDED:
            assert topic in DIALOGUES_EXTENDED_TOPICS

    def test_all_topics_in_keywords(self):
        for topic in DIALOGUES_EXTENDED:
            assert topic in DIALOGUES_EXTENDED_KEYWORDS

    def test_keywords_have_entries(self):
        for topic, keywords in DIALOGUES_EXTENDED_KEYWORDS.items():
            assert len(keywords) >= 5, f"{topic} has too few keywords"
            for kw in keywords:
                assert isinstance(kw, str)
                assert len(kw) > 0

    def test_no_empty_responses(self):
        for topic, responses in DIALOGUES_EXTENDED.items():
            for r in responses:
                assert r.strip(), f"Empty response in {topic}"

    def test_response_length_distribution(self):
        lengths = []
        for topic, responses in DIALOGUES_EXTENDED.items():
            for r in responses:
                lengths.append(len(r))
        avg = sum(lengths) / len(lengths)
        assert 20 < avg < 200


class TestContextualResponses:
    def test_contextual_responses_exist(self):
        assert len(CONTEXTUAL_RESPONSES) >= 8
        required = ["morning", "afternoon", "evening", "happy_user", "sad_user", "goodbye"]
        for ctx in required:
            assert ctx in CONTEXTUAL_RESPONSES

    def test_all_contexts_have_responses(self):
        for ctx, responses in CONTEXTUAL_RESPONSES.items():
            assert len(responses) >= 3
            for r in responses:
                assert isinstance(r, str)
                assert len(r) > 5

    def test_morning_responses(self):
        for r in CONTEXTUAL_RESPONSES["morning"]:
            assert "buenos" in r.lower() or "buen" in r.lower()

    def test_goodbye_responses(self):
        for r in CONTEXTUAL_RESPONSES["goodbye"]:
            assert "hasta" in r.lower() or "nos" in r.lower() or "cuídate" in r.lower()

    def test_no_empty_contextual(self):
        for ctx, responses in CONTEXTUAL_RESPONSES.items():
            for r in responses:
                assert r.strip()

    def test_contextual_response_uniqueness(self):
        for ctx, responses in CONTEXTUAL_RESPONSES.items():
            assert len(responses) == len(set(responses))


class TestPersonalityTraitsData:
    def test_traits_json_loads(self):
        path = os.path.join(os.path.dirname(__file__), "..", "botty", "data", "personality_traits.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "traits" in data
        assert len(data["traits"]) >= 8

    def test_trait_structure(self):
        path = os.path.join(os.path.dirname(__file__), "..", "botty", "data", "personality_traits.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for trait in data["traits"]:
            assert "id" in trait
            assert "name" in trait
            assert "description" in trait
            assert "questions" in trait
            assert "reaction_probability" in trait
            assert len(trait["questions"]) >= 5

    def test_trait_probabilities(self):
        path = os.path.join(os.path.dirname(__file__), "..", "botty", "data", "personality_traits.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for trait in data["traits"]:
            assert 0 <= trait["reaction_probability"] <= 1

    def test_reaction_triggers(self):
        path = os.path.join(os.path.dirname(__file__), "..", "botty", "data", "personality_traits.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        triggers = data.get("reaction_triggers", {})
        assert "positive_keywords" in triggers
        assert "negative_keywords" in triggers
        assert "question_keywords" in triggers
        assert len(triggers["positive_keywords"]) >= 5
        assert len(triggers["negative_keywords"]) >= 3

    def test_trait_switching(self):
        path = os.path.join(os.path.dirname(__file__), "..", "botty", "data", "personality_traits.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        switching = data.get("trait_switching", {})
        assert "enabled" in switching
        assert "interval_min" in switching
        assert "interval_max" in switching
        assert switching["interval_min"] > 0
        assert switching["interval_max"] > switching["interval_min"]

    def test_default_trait(self):
        path = os.path.join(os.path.dirname(__file__), "..", "botty", "data", "personality_traits.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        default = data.get("default_trait", "")
        trait_ids = [t["id"] for t in data["traits"]]
        assert default in trait_ids, f"default_trait '{default}' not found in traits"


class TestDataFiles:
    def test_faq_json(self):
        path = os.path.join(os.path.dirname(__file__), "..", "botty", "data", "faq_data.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "faq" in data
        assert len(data["faq"]) >= 20
        for entry in data["faq"]:
            assert "q" in entry
            assert "a" in entry
            assert len(entry["q"]) > 5
            assert len(entry["a"]) > 10

    def test_voice_commands_json(self):
        path = os.path.join(os.path.dirname(__file__), "..", "botty", "data", "voice_commands.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "voice_commands" in data
        cmds = data["voice_commands"]
        assert len(cmds) >= 25
        for cmd_name, cmd in cmds.items():
            assert "patterns" in cmd
            assert "action" in cmd
            assert "response" in cmd
            assert "category" in cmd
            assert len(cmd["patterns"]) >= 1

    def test_example_conversations_json(self):
        path = os.path.join(os.path.dirname(__file__), "..", "botty", "data", "example_conversations.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) >= 15
        for entry in data:
            assert "id" in entry
            assert "user" in entry
            assert "bot" in entry
            assert "emotion" in entry
            assert "tags" in entry

    def test_config_yaml_example(self):
        path = os.path.join(os.path.dirname(__file__), "..", "botty", "config.yaml.example")
        assert os.path.exists(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "botty:" in content or "general:" in content
        assert "display:" in content
        assert "ai:" in content
        assert "audio:" in content

    def test_sound_generator_imports(self):
        try:
            from botty.audio.sound import SoundGenerator
            sg = SoundGenerator()
            assert sg is not None
        except Exception as e:
            pytest.skip(f"Sound generator import: {e}")

    def test_importer_imports(self):
        from botty.sensors.imu import MPU6050, SimulatedIMU
        imu = SimulatedIMU()
        assert imu is not None
        imu.init()
        data = imu.get_all()
        assert "ax" in data
        assert "gy" in data
        assert "roll" in data
        assert "temperature" in data
        imu.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
