from application.experience import (
    EXPERIENCE_SOURCE,
    award_skill_experience,
    resolve_experience_die,
)
from domain.character import Character
from domain.calculations import recalculate
from domain.skill_ownership import add_skill_levels
from domain.calculations.skills import rebuild_skills


def make_character():
    c = Character(name="Test")
    recalculate(c)
    return c

def test_skill_experience_gain_when_die_times_ten_exceeds_skill():
    c = make_character()

    gained = award_skill_experience(c, "Lockpicking", experience_die=8, rebuild=False)

    assert gained is True
    assert c.skill_sources["Lockpicking"][EXPERIENCE_SOURCE] == 1


def test_skill_experience_does_not_gain_when_threshold_fails():
    c = make_character()

    add_skill_levels(c, "Lockpicking", "test", 90)
    rebuild_skills(c)

    gained = award_skill_experience(c, "Lockpicking", experience_die=1, rebuild=False)

    assert gained is False
    assert c.skill_sources["Lockpicking"].get(EXPERIENCE_SOURCE, 0) == 0


def test_skill_experience_die_nine_always_gains_skill():
    c = make_character()

    gained = award_skill_experience(c, "Lockpicking", experience_die=9, rebuild=False)

    assert gained is True
    assert c.skill_sources["Lockpicking"][EXPERIENCE_SOURCE] == 1


def test_skill_experience_die_nine_also_gains_linked_attribute():
    c = make_character()
    before_dex = c.manual_attribute_increases.get("dexterity", 0)

    result = resolve_experience_die(
        c,
        success=True,
        experience_die=9,
        skill_name="Lockpicking",
        attribute_name="dexterity",
        rebuild=False
    )

    assert result.skill_gained is True
    assert result.attribute_gained is True
    assert c.skill_sources["Lockpicking"][EXPERIENCE_SOURCE] == 1
    assert c.manual_attribute_increases["dexterity"]["experience"] == before_dex + 1


def test_failed_roll_never_grants_skill_experience():
    c = make_character()

    result = resolve_experience_die(
        c,
        success=False,
        experience_die=9,
        skill_name="Lockpicking",
        attribute_name="dexterity",
    )

    assert result.skill_gained is False
    assert result.attribute_gained is False
    assert "Lockpicking" not in c.skill_sources