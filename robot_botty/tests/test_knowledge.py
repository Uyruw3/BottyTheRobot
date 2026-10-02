"""
Tests for knowledge base modules — Spanish, jokes, trivia, personality, responses.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from botty.knowledge.spanish import (
    GREETING_RESPONSES, FAREWELL_RESPONSES, THANKS_RESPONSES,
    APOLOGY_RESPONSES, COMPLIMENT_RESPONSES, CURIOUS_RESPONSES,
    ENCOURAGEMENT_RESPONSES, WEATHER_RESPONSES, TIME_RESPONSES,
    NAME_RESPONSES, FEELING_RESPONSES, UNKNOWN_RESPONSES,
    ERROR_RESPONSES, TOPIC_RESPONSES, QUESTIONS_ABOUT_BOTTY,
    RANDOM_PHRASES,
)
from botty.knowledge.jokes import LARGE_JOKE_COLLECTION, TECH_JOKES, MIXED_JOKES
from botty.knowledge.trivia import (
    ALL_FACTS, ALL_CATEGORIES, ALL_FACTS_FLAT,
    SCIENCE_FACTS, TECHNOLOGY_FACTS, ROBOTICS_FACTS,
    HISTORY_FACTS, NATURE_FACTS, BRAIN_FACTS,
)
from botty.knowledge.personality import PERSONALITY, FACTS, HUMOR
from botty.knowledge.responses import RESPONSES, GREETINGS, FAREWELLS


class TestSpanishModule:
    def test_greeting_responses(self):
        assert len(GREETING_RESPONSES) >= 15
        for response in GREETING_RESPONSES:
            assert isinstance(response, str)
            assert len(response) > 10

    def test_farewell_responses(self):
        assert len(FAREWELL_RESPONSES) >= 15
        for response in FAREWELL_RESPONSES:
            assert isinstance(response, str)

    def test_thanks_responses(self):
        assert len(THANKS_RESPONSES) >= 10
        for r in THANKS_RESPONSES:
            assert "gracias" in r.lower() or "nada" in r.lower() or "gusto" in r.lower()

    def test_apology_responses(self):
        assert len(APOLOGY_RESPONSES) >= 10
        for r in APOLOGY_RESPONSES:
            assert len(r) > 5

    def test_compliment_responses(self):
        assert len(COMPLIMENT_RESPONSES) >= 10
        for r in COMPLIMENT_RESPONSES:
            assert "gracias" in r.lower() or "eres" in r.lower()

    def test_curious_responses(self):
        assert len(CURIOUS_RESPONSES) >= 10
        for r in CURIOUS_RESPONSES:
            assert "?" in r or "!" in r

    def test_encouragement_responses(self):
        assert len(ENCOURAGEMENT_RESPONSES) >= 10
        for r in ENCOURAGEMENT_RESPONSES:
            assert len(r) > 10

    def test_weather_responses(self):
        assert len(WEATHER_RESPONSES) >= 8

    def test_time_responses(self):
        assert len(TIME_RESPONSES) >= 5

    def test_name_responses(self):
        assert len(NAME_RESPONSES) >= 5
        for r in NAME_RESPONSES:
            assert "Botty" in r

    def test_feeling_responses(self):
        assert len(FEELING_RESPONSES) >= 8
        for r in FEELING_RESPONSES:
            assert "estoy" in r.lower() or "bien" in r.lower()

    def test_unknown_responses(self):
        assert len(UNKNOWN_RESPONSES) >= 10

    def test_error_responses(self):
        assert len(ERROR_RESPONSES) >= 5

    def test_topic_responses(self):
        assert len(TOPIC_RESPONSES) >= 15
        for topic, response in TOPIC_RESPONSES.items():
            assert isinstance(topic, str)
            assert isinstance(response, str)

    def test_questions_about_botty(self):
        assert len(QUESTIONS_ABOUT_BOTTY) >= 8
        for q, a in QUESTIONS_ABOUT_BOTTY.items():
            assert isinstance(q, str)
            assert isinstance(a, str)
            assert len(a) > 10

    def test_random_phrases(self):
        assert len(RANDOM_PHRASES) >= 20
        for p in RANDOM_PHRASES:
            assert isinstance(p, str)
            assert len(p) > 10

    def test_all_responses_have_content(self):
        all_responses = (
            GREETING_RESPONSES + FAREWELL_RESPONSES + THANKS_RESPONSES +
            APOLOGY_RESPONSES + COMPLIMENT_RESPONSES + CURIOUS_RESPONSES +
            ENCOURAGEMENT_RESPONSES + WEATHER_RESPONSES + TIME_RESPONSES +
            NAME_RESPONSES + FEELING_RESPONSES + UNKNOWN_RESPONSES +
            ERROR_RESPONSES + RANDOM_PHRASES
        )
        assert len(all_responses) > 100

    def test_no_empty_responses(self):
        all_responses = (
            GREETING_RESPONSES + FAREWELL_RESPONSES + THANKS_RESPONSES +
            APOLOGY_RESPONSES + COMPLIMENT_RESPONSES + CURIOUS_RESPONSES +
            ENCOURAGEMENT_RESPONSES + WEATHER_RESPONSES + TIME_RESPONSES +
            NAME_RESPONSES + FEELING_RESPONSES + UNKNOWN_RESPONSES +
            ERROR_RESPONSES + RANDOM_PHRASES
        )
        for r in all_responses:
            assert r.strip(), f"Empty response found"


class TestJokesModule:
    def test_large_joke_collection(self):
        assert len(LARGE_JOKE_COLLECTION) >= 50
        for joke in LARGE_JOKE_COLLECTION:
            assert isinstance(joke, str)
            assert len(joke) > 5

    def test_tech_jokes(self):
        assert len(TECH_JOKES) >= 10

    def test_mixed_jokes(self):
        assert len(MIXED_JOKES) >= 25

    def test_all_jokes_unique(self):
        all_jokes = LARGE_JOKE_COLLECTION + TECH_JOKES + MIXED_JOKES
        assert len(all_jokes) == len(set(all_jokes))

    def test_jokes_have_punctuation(self):
        for joke in LARGE_JOKE_COLLECTION:
            assert joke.endswith("!") or joke.endswith(".") or joke.endswith("?")

    def test_spanish_jokes_content(self):
        spanish_markers = ["por que", "como se llama", "que le dijo", "cual es"]
        found = any(any(m in joke.lower() for m in spanish_markers) for joke in LARGE_JOKE_COLLECTION)
        assert found


class TestTriviaModule:
    def test_all_categories(self):
        assert len(ALL_CATEGORIES) >= 6
        assert "ciencia" in ALL_CATEGORIES
        assert "tecnologia" in ALL_CATEGORIES

    def test_science_facts(self):
        assert len(SCIENCE_FACTS) >= 10
        for fact in SCIENCE_FACTS:
            assert isinstance(fact, str)
            assert len(fact) > 10

    def test_technology_facts(self):
        assert len(TECHNOLOGY_FACTS) >= 10

    def test_robotics_facts(self):
        assert len(ROBOTICS_FACTS) >= 10

    def test_history_facts(self):
        assert len(HISTORY_FACTS) >= 10

    def test_nature_facts(self):
        assert len(NATURE_FACTS) >= 10

    def test_brain_facts(self):
        assert len(BRAIN_FACTS) >= 10

    def test_all_facts_flat(self):
        assert len(ALL_FACTS_FLAT) >= 60
        assert len(ALL_FACTS_FLAT) == (
            len(SCIENCE_FACTS) + len(TECHNOLOGY_FACTS) + len(ROBOTICS_FACTS) +
            len(HISTORY_FACTS) + len(NATURE_FACTS) + len(BRAIN_FACTS)
        )

    def test_all_facts_unique(self):
        assert len(ALL_FACTS_FLAT) == len(set(ALL_FACTS_FLAT))

    def test_category_facts_all_strings(self):
        for category, facts in ALL_FACTS.items():
            for fact in facts:
                assert isinstance(fact, str), f"{category} has non-string fact"

    def test_category_mapping(self):
        for cat in ALL_CATEGORIES:
            assert cat in ALL_FACTS


class TestPersonalityModule:
    def test_personality_has_keys(self):
        required = ["name", "greeting", "emotions", "likes", "dislikes", "goals"]
        for key in required:
            assert key in PERSONALITY, f"Missing key: {key}"

    def test_facts_list(self):
        assert len(FACTS) >= 10
        for fact in FACTS:
            assert isinstance(fact, str)
            assert len(fact) > 5

    def test_humor_list(self):
        assert len(HUMOR) >= 5
        for humor_item in HUMOR:
            assert isinstance(humor_item, str)

    def test_personality_emotions(self):
        emotions = PERSONALITY.get("emotions", [])
        assert len(emotions) >= 5

    def test_personality_likes(self):
        likes = PERSONALITY.get("likes", [])
        assert len(likes) >= 3

    def test_personality_dislikes(self):
        dislikes = PERSONALITY.get("dislikes", [])
        assert len(dislikes) >= 3

    def test_personality_goals(self):
        goals = PERSONALITY.get("goals", [])
        assert len(goals) >= 3


class TestResponsesModule:
    def test_responses_categories(self):
        required = ["saludos", "despedidas", "estado", "ayuda", "errores"]
        for cat in required:
            assert cat in RESPONSES, f"Missing category: {cat}"

    def test_responses_not_empty(self):
        for category, responses in RESPONSES.items():
            assert len(responses) > 0, f"Empty category: {category}"

    def test_greetings(self):
        assert len(GREETINGS) >= 5
        for g in GREETINGS:
            assert isinstance(g, str)

    def test_farewells(self):
        assert len(FAREWELLS) >= 5
        for f in FAREWELLS:
            assert isinstance(f, str)

    def test_all_responses_strings(self):
        for cat, responses in RESPONSES.items():
            for r in responses:
                assert isinstance(r, str), f"{cat} has non-string response"


class TestKnowledgeBaseSize:
    def test_total_responses_count(self):
        total = (
            len(GREETING_RESPONSES) + len(FAREWELL_RESPONSES) +
            len(THANKS_RESPONSES) + len(APOLOGY_RESPONSES) +
            len(COMPLIMENT_RESPONSES) + len(CURIOUS_RESPONSES) +
            len(ENCOURAGEMENT_RESPONSES) + len(WEATHER_RESPONSES) +
            len(TIME_RESPONSES) + len(NAME_RESPONSES) +
            len(FEELING_RESPONSES) + len(UNKNOWN_RESPONSES) +
            len(ERROR_RESPONSES) + len(RANDOM_PHRASES)
        )
        assert total > 150

    def test_total_jokes_count(self):
        total = len(LARGE_JOKE_COLLECTION) + len(TECH_JOKES) + len(MIXED_JOKES)
        assert total > 100

    def test_total_facts_count(self):
        assert len(ALL_FACTS_FLAT) > 60

    def test_spanish_knowledge_size(self):
        total = len(TOPIC_RESPONSES) + len(QUESTIONS_ABOUT_BOTTY)
        assert total > 20
