from domain.character import Character
from domain.skill_ownership import (
    add_skill_levels,
    set_skill_levels,
    remove_skill_source,
    get_total_skill_levels,
    has_skill,
    rebuild_skill_level_summary,
)


def test_add_skill_levels_accumulates_by_source():
    c = Character(name="Test")

    add_skill_levels(c, "Riding", "runtime:first_use", 1)
    add_skill_levels(c, "Riding", "runtime:first_use", 2)

    assert c.skill_sources["Riding"]["runtime:first_use"] == 3
    assert get_total_skill_levels(c, "Riding") == 3

def test_set_skill_levels_zero_removes_source():
    c = Character(name="Test")

    set_skill_levels(c, "Riding", "generic_points", 5)
    assert has_skill(c, "Riding") is True

    set_skill_levels(c, "Riding", "generic_points", 0)

    assert get_total_skill_levels(c, "Riding") == 0
    assert has_skill(c, "Riding") is False
    assert "Riding" not in c.skill_sources

def test_remove_skill_source_only_removes_targeted_source():
    c = Character(name="Test")

    add_skill_levels(c, "Riding", "generic_points", 5)
    add_skill_levels(c, "Riding", "runtime:experience_die", 2)

    remove_skill_source(c, "Riding", "generic_points")

    assert c.skill_sources["Riding"]["runtime:experience_die"] == 2
    assert get_total_skill_levels(c, "Riding") == 2

def test_rebuild_skill_level_summary_sums_sources():
    c = Character(name="Test")

    add_skill_levels(c, "Riding", "generic_points", 5)
    add_skill_levels(c, "Riding", "runtime:experience_die", 2)
    add_skill_levels(c, "Climb", "generic_points", 3)

    summary = rebuild_skill_level_summary(c)

    assert summary == {
        "Riding": 7,
        "Climb": 3,
    }