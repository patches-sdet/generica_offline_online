from domain.character import Character
from domain.skill_ownership import (
    add_skill_levels,
    get_total_skill_levels,
    has_skill,
    set_skill_levels,
)


def test_add_skill_levels_creates_entry():
    c = Character(name="Test")
    add_skill_levels(c, "Riding", source="runtime:first_use", levels=1)

    assert has_skill(c, "Riding")
    assert get_total_skill_levels(c, "Riding") == 1


def test_add_skill_levels_accumulates_by_source():
    c = Character(name="Test")
    add_skill_levels(c, "Riding", source="generic_points", levels=5)
    add_skill_levels(c, "Riding", source="runtime:first_use", levels=1)

    assert get_total_skill_levels(c, "Riding") == 6

def test_set_skill_levels_overwrites_source_value():
    c = Character(name="Test")
    set_skill_levels(c, "Sword", source="generic_points", levels=10)
    set_skill_levels(c, "Sword", source="generic_points", levels=7)

    assert get_total_skill_levels(c, "Sword") == 7