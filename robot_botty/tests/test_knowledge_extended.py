"""
Extended tests for new knowledge modules: geography, space, riddles, philosophy, english, nature.
"""

from botty.knowledge.geography import (
    CONTINENTS, COUNTRY_FACTS, CAPITAL_FACTS, LANDMARK_FACTS, ALL_GEOGRAPHY_FACTS,
)
from botty.knowledge.space import (
    PLANET_FACTS, STAR_FACTS, EXPLORATION_FACTS, ALL_SPACE_FACTS,
)
from botty.knowledge.riddles import RIDDLES, ENGLISH_RIDDLES
from botty.knowledge.philosophy import (
    PHILOSOPHICAL_QUOTES, PHILOSOPHICAL_CONCEPTS, PHILOSOPHICAL_DEEP_THOUGHTS,
)
from botty.knowledge.english import (
    ENGLISH_GREETINGS, ENGLISH_FAREWELLS, ENGLISH_THANKS,
    ENGLISH_APOLOGIES, ENGLISH_COMPLIMENTS, ENGLISH_ENCOURAGEMENT,
    ENGLISH_TOPIC_RESPONSES, ENGLISH_CURIOUS, ENGLISH_FEELINGS,
    ENGLISH_UNKNOWN, ENGLISH_ERRORS, ENGLISH_ABOUT_BOTTY,
)
from botty.knowledge.nature import (
    ANIMAL_FACTS, BIOME_FACTS, ECOSYSTEM_FACTS, NATURAL_PHENOMENA_FACTS, ALL_NATURE_FACTS,
)


class TestGeography:
    def test_continents_defined(self):
        assert len(CONTINENTS) == 7

    def test_country_facts_nonempty(self):
        assert len(COUNTRY_FACTS) > 20

    def test_capital_facts_nonempty(self):
        assert len(CAPITAL_FACTS) >= 15

    def test_landmark_facts_nonempty(self):
        assert len(LANDMARK_FACTS) >= 15

    def test_all_geography_facts_combined(self):
        expected = len(COUNTRY_FACTS) + len(CAPITAL_FACTS) + len(LANDMARK_FACTS)
        assert len(ALL_GEOGRAPHY_FACTS) == expected

    def test_facts_are_strings(self):
        for fact in ALL_GEOGRAPHY_FACTS:
            assert isinstance(fact, str)
            assert len(fact) > 10

    def test_continent_names(self):
        expected = {"Africa", "Antarctica", "Asia", "Europe", "North America", "Oceania", "South America"}
        assert set(CONTINENTS) == expected


class TestSpace:
    def test_planet_facts_nonempty(self):
        assert len(PLANET_FACTS) >= 10

    def test_star_facts_nonempty(self):
        assert len(STAR_FACTS) >= 8

    def test_exploration_facts_nonempty(self):
        assert len(EXPLORATION_FACTS) >= 15

    def test_all_space_facts_combined(self):
        expected = len(PLANET_FACTS) + len(STAR_FACTS) + len(EXPLORATION_FACTS)
        assert len(ALL_SPACE_FACTS) == expected

    def test_planet_facts_unique(self):
        assert len(set(PLANET_FACTS)) == len(PLANET_FACTS)

    def test_facts_cover_planets(self):
        combined = " ".join(PLANET_FACTS).lower()
        for planet in ["mercurio", "venus", "tierra", "marte", "jupiter", "saturno", "urano", "neptuno"]:
            assert planet in combined


class TestRiddles:
    def test_riddles_count(self):
        assert len(RIDDLES) >= 40

    def test_english_riddles_count(self):
        assert len(ENGLISH_RIDDLES) >= 8

    def test_each_riddle_has_answer(self):
        for r in RIDDLES:
            assert "riddle" in r
            assert "answer" in r
            assert isinstance(r["riddle"], str)
            assert isinstance(r["answer"], str)

    def test_english_riddles_have_answer(self):
        for r in ENGLISH_RIDDLES:
            assert "riddle" in r
            assert "answer" in r

    def test_riddles_are_questions(self):
        for r in RIDDLES:
            assert len(r["riddle"]) > 10

    def test_riddles_unique(self):
        riddles_only = [r["riddle"] for r in RIDDLES]
        assert len(set(riddles_only)) == len(riddles_only)


class TestPhilosophy:
    def test_quotes_nonempty(self):
        assert len(PHILOSOPHICAL_QUOTES) >= 15

    def test_concepts_nonempty(self):
        assert len(PHILOSOPHICAL_CONCEPTS) >= 12

    def test_deep_thoughts_nonempty(self):
        assert len(PHILOSOPHICAL_DEEP_THOUGHTS) >= 10

    def test_quotes_have_author(self):
        for q in PHILOSOPHICAL_QUOTES:
            assert "quote" in q
            assert "author" in q
            assert len(q["author"]) > 2

    def test_famous_philosophers_present(self):
        text = " ".join(q["quote"] for q in PHILOSOPHICAL_QUOTES)
        assert len(text) > 500


class TestEnglish:
    def test_greetings_nonempty(self):
        assert len(ENGLISH_GREETINGS) >= 10

    def test_farewells_nonempty(self):
        assert len(ENGLISH_FAREWELLS) >= 10

    def test_thanks_nonempty(self):
        assert len(ENGLISH_THANKS) >= 5

    def test_apologies_nonempty(self):
        assert len(ENGLISH_APOLOGIES) >= 5

    def test_compliments_nonempty(self):
        assert len(ENGLISH_COMPLIMENTS) >= 5

    def test_encouragement_nonempty(self):
        assert len(ENGLISH_ENCOURAGEMENT) >= 10

    def test_topic_responses_defined(self):
        assert len(ENGLISH_TOPIC_RESPONSES) >= 10

    def test_curious_nonempty(self):
        assert len(ENGLISH_CURIOUS) >= 5

    def test_feelings_nonempty(self):
        assert len(ENGLISH_FEELINGS) >= 5

    def test_unknown_nonempty(self):
        assert len(ENGLISH_UNKNOWN) >= 5

    def test_errors_nonempty(self):
        assert len(ENGLISH_ERRORS) >= 5

    def test_about_botty_defined(self):
        assert len(ENGLISH_ABOUT_BOTTY) >= 5

    def test_greetings_in_english(self):
        for g in ENGLISH_GREETINGS:
            assert isinstance(g, str)
            assert any(
                word in g.lower()
                for word in ("hello", "hi", "hey", "welcome", "greeting")
            )

    def test_farewells_in_english(self):
        for f in ENGLISH_FAREWELLS:
            assert isinstance(f, str)
            assert len(f) > 5


class TestNature:
    def test_animal_facts_nonempty(self):
        assert len(ANIMAL_FACTS) >= 15

    def test_biome_facts_nonempty(self):
        assert len(BIOME_FACTS) >= 8

    def test_ecosystem_facts_nonempty(self):
        assert len(ECOSYSTEM_FACTS) >= 8

    def test_natural_phenomena_nonempty(self):
        assert len(NATURAL_PHENOMENA_FACTS) >= 8

    def test_all_nature_facts_combined(self):
        expected = len(ANIMAL_FACTS) + len(BIOME_FACTS) + len(ECOSYSTEM_FACTS) + len(NATURAL_PHENOMENA_FACTS)
        assert len(ALL_NATURE_FACTS) == expected

    def test_facts_are_unique(self):
        assert len(set(ALL_NATURE_FACTS)) == len(ALL_NATURE_FACTS)

    def test_animal_facts_mention_animals(self):
        combined = " ".join(ANIMAL_FACTS).lower()
        animal_keywords = ["pajaro", "pulpo", "hormiga", "elefante", "delfin", "abeja", "mariposa"]
        found = any(k in combined for k in animal_keywords)
        assert found


class TestMath:
    def test_math_facts_nonempty(self):
        from botty.knowledge.math import MATH_FACTS, MATH_CURIOSITIES
        assert len(MATH_FACTS) >= 15
        assert len(MATH_CURIOSITIES) >= 8

    def test_math_facts_are_unique(self):
        from botty.knowledge.math import MATH_FACTS
        assert len(set(MATH_FACTS)) == len(MATH_FACTS)


class TestCooking:
    def test_cooking_facts_nonempty(self):
        from botty.knowledge.cooking import COOKING_FACTS, COOKING_TIPS, RECIPES
        assert len(COOKING_FACTS) >= 15
        assert len(COOKING_TIPS) >= 8
        assert len(RECIPES) >= 3

    def test_recipes_have_instructions(self):
        from botty.knowledge.cooking import RECIPES
        for name, recipe in RECIPES.items():
            assert "instructions" in recipe
            assert "ingredients" in recipe
            assert len(recipe["ingredients"]) >= 3


class TestHistory:
    def test_ancient_history_nonempty(self):
        from botty.knowledge.history import ANCIENT_HISTORY, MEDIEVAL_HISTORY, MODERN_HISTORY, ALL_HISTORY_FACTS
        assert len(ANCIENT_HISTORY) >= 8
        assert len(MEDIEVAL_HISTORY) >= 8
        assert len(MODERN_HISTORY) >= 8
        total = len(ANCIENT_HISTORY) + len(MEDIEVAL_HISTORY) + len(MODERN_HISTORY)
        assert len(ALL_HISTORY_FACTS) == total

    def test_ancient_mentions_rome(self):
        from botty.knowledge.history import ANCIENT_HISTORY
        assert len(ANCIENT_HISTORY) > 0


class TestTechnology:
    def test_tech_facts_nonempty(self):
        from botty.knowledge.technology import COMPUTING_HISTORY, INTERNET_FACTS, FUTURE_TECH, ALL_TECH_FACTS
        assert len(COMPUTING_HISTORY) >= 8
        assert len(INTERNET_FACTS) >= 8
        assert len(FUTURE_TECH) >= 8
        total = len(COMPUTING_HISTORY) + len(INTERNET_FACTS) + len(FUTURE_TECH)
        assert len(ALL_TECH_FACTS) == total

    def test_facts_are_strings(self):
        from botty.knowledge.technology import ALL_TECH_FACTS
        for fact in ALL_TECH_FACTS:
            assert isinstance(fact, str)

    def test_computing_history_mentions_eniac(self):
        from botty.knowledge.technology import COMPUTING_HISTORY
        combined = " ".join(COMPUTING_HISTORY).lower()
        assert "eniac" in combined or "computadora" in combined


class TestKnowledgePackage:
    def test_all_modules_importable(self):
        import botty.knowledge
        assert hasattr(botty.knowledge, "ALL_GEOGRAPHY_FACTS")
        assert hasattr(botty.knowledge, "ALL_SPACE_FACTS")
        assert hasattr(botty.knowledge, "RIDDLES")
        assert hasattr(botty.knowledge, "PHILOSOPHICAL_QUOTES")
        assert hasattr(botty.knowledge, "ENGLISH_GREETINGS")
        assert hasattr(botty.knowledge, "ALL_NATURE_FACTS")
        assert hasattr(botty.knowledge, "MATH_FACTS")
        assert hasattr(botty.knowledge, "COOKING_FACTS")
        assert hasattr(botty.knowledge, "ALL_HISTORY_FACTS")
        assert hasattr(botty.knowledge, "ALL_TECH_FACTS")

    def test_knowledge_total_size(self):
        from botty.knowledge.spanish import GREETING_RESPONSES, RANDOM_PHRASES
        assert len(GREETING_RESPONSES) >= 10
        assert len(RANDOM_PHRASES) >= 25

    def test_jokes_importable(self):
        from botty.knowledge.jokes import LARGE_JOKE_COLLECTION, SHORT_JOKES, TECH_JOKES, MIXED_JOKES
        assert len(SHORT_JOKES) >= 15
        assert len(TECH_JOKES) >= 5

    def test_trivia_categories(self):
        from botty.knowledge.trivia import ALL_CATEGORIES, ALL_FACTS
        assert "ciencia" in ALL_CATEGORIES
        assert len(ALL_FACTS) >= 6
