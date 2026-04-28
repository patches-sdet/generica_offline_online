from application.experience import (
    award_attribute_experience,
    resolve_experience_die,
)
from domain.character import Character
from domain.calculations import recalculate


def make_character():
    c = Character(name="Test")
    recalculate(c)
    return c

def test_attribute_experience_gain_when_die_times_ten_exceeds_attribute():
    c = make_character()
    before = c.manual_attribute_increases.get("strength", {}).get("experience", 0)

    gained = award_attribute_experience(c, "strength", experience_die=8)

    assert gained is True
    assert c.manual_attribute_increases["strength"]["experience"] == before + 1


def test_attribute_experience_does_not_gain_when_threshold_fails():
    c = make_character()
    before = c.manual_attribute_increases.get("strength", {}).get("experience", 0)

    gained = award_attribute_experience(c, "strength", experience_die=1)

    assert gained is False
    assert c.manual_attribute_increases.get("strength", {}).get("experience", 0) == before


def test_attribute_experience_die_nine_always_gains():
    c = make_character()
    before = c.manual_attribute_increases.get("strength", {}).get("experience", 0)

    gained = award_attribute_experience(c, "strength", experience_die=9)

    assert gained is True
    assert c.manual_attribute_increases["strength"]["experience"] == before + 1


def test_failed_roll_never_grants_attribute_experience():
    c = make_character()
    before = c.manual_attribute_increases.get("strength", {}).get("experience", 0)

    result = resolve_experience_die(
        c,
        success=False,
        experience_die=9,
        attribute_name="strength",
    )

    assert result.attribute_gained is False
    assert result.gained_anything is False
    assert c.manual_attribute_increases.get("strength", {}).get("experience", 0) == before