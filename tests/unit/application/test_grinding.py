from application.character_creation import create_character
from application.leveling import (
    award_grind_points,
    get_skill_grind_cost,
    can_grind_skill,
    grind_skill,
    get_attribute_grind_cost,
    can_grind_attribute,
    grind_attribute,
)
from domain.calculations import recalculate
from domain.skill_ownership import add_skill_levels


def test_get_skill_grind_cost_uses_ceil_division(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Skill Grind Cost Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    add_skill_levels(c, "Riding", "generic_points", 1)
    recalculate(c)
    assert get_skill_grind_cost(c, "Riding") == 1

    add_skill_levels(c, "Lockpicking", "generic_points", 23)
    recalculate(c)
    assert get_skill_grind_cost(c, "Lockpicking") == 3

    add_skill_levels(c, "Climb", "generic_points", 73)
    recalculate(c)
    assert get_skill_grind_cost(c, "Climb") == 8


def test_get_attribute_grind_cost_uses_ceil_division(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Attribute Grind Cost Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.add_manual_attribute_increase("strength", 5, "test")
    recalculate(c)

    assert get_attribute_grind_cost(c, "strength") == ((c.get_stat("strength") + 4) // 5)


def test_can_grind_skill_false_without_enough_points(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Can Grind Skill Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    add_skill_levels(c, "Lockpicking", "generic_points", 23)
    recalculate(c)

    assert can_grind_skill(c, "Lockpicking") is False


def test_can_grind_skill_true_with_enough_points(initialized_content, monkeypatch):
    from application import character_creation
    from application.leveling import level_up_progression

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Can Grind Skill Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    # Raise highest job level to 3 so generic skill cap becomes 30.
    level_up_progression(c, ptype="adventure", name="Berserker", refill_pools=False)
    level_up_progression(c, ptype="adventure", name="Berserker", refill_pools=False)

    add_skill_levels(c, "Lockpicking", "generic_points", 23)
    recalculate(c)

    award_grind_points(c, 3)

    assert can_grind_skill(c, "Lockpicking") is True


def test_grind_skill_spends_points_and_increases_skill(initialized_content, monkeypatch):
    from application import character_creation
    from application.leveling import level_up_progression

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Grind Skill Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    # Raise highest job level to 3 so generic skill cap becomes 30.
    level_up_progression(c, ptype="adventure", name="Berserker", refill_pools=False)
    level_up_progression(c, ptype="adventure", name="Berserker", refill_pools=False)

    add_skill_levels(c, "Lockpicking", "generic_points", 23)
    recalculate(c)

    before_skill = c.get_skill_level("Lockpicking", 0)
    before_points = c.grind_points

    award_grind_points(c, 3)

    new_level = grind_skill(c, "Lockpicking")

    assert new_level == before_skill + 1
    assert c.get_skill_level("Lockpicking", 0) == before_skill + 1
    assert c.grind_points == before_points
    assert c.skill_sources["Lockpicking"]["grind"] == 1


def test_grind_skill_survives_recalculate(initialized_content, monkeypatch):
    from application import character_creation
    from application.leveling import level_up_progression

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Grind Skill Recalc Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    # Raise highest job level to 3 so generic skill cap becomes 30.
    level_up_progression(c, ptype="adventure", name="Berserker", refill_pools=False)
    level_up_progression(c, ptype="adventure", name="Berserker", refill_pools=False)

    add_skill_levels(c, "Lockpicking", "generic_points", 23)
    recalculate(c)

    before_skill = c.get_skill_level("Lockpicking", 0)

    award_grind_points(c, 3)
    grind_skill(c, "Lockpicking")

    recalculate(c)

    assert c.get_skill_level("Lockpicking", 0) == before_skill + 1


def test_can_grind_attribute_false_without_enough_points(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Can Grind Attribute Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    assert can_grind_attribute(c, "strength") is False


def test_can_grind_attribute_true_with_enough_points(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Can Grind Attribute Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    cost = get_attribute_grind_cost(c, "strength")
    award_grind_points(c, cost)

    assert can_grind_attribute(c, "strength") is True


def test_grind_attribute_spends_points_and_increases_attribute(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Grind Attribute Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before_stat = c.get_stat("strength")
    before_points = c.grind_points
    cost = get_attribute_grind_cost(c, "strength")

    award_grind_points(c, cost)

    new_value = grind_attribute(c, "strength")

    assert new_value == before_stat + 1
    assert c.get_stat("strength") == before_stat + 1
    assert c.grind_points == before_points
    assert c.manual_attribute_increases["strength"]["grind"] == 1


def test_grind_attribute_survives_recalculate(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Grind Attribute Recalc Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before_stat = c.get_stat("strength")
    cost = get_attribute_grind_cost(c, "strength")

    award_grind_points(c, cost)
    grind_attribute(c, "strength")

    recalculate(c)

    assert c.get_stat("strength") == before_stat + 1


def test_grind_skill_rejects_missing_skill(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Missing Skill Grind Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_grind_points(c, 1)

    try:
        grind_skill(c, "Definitely Missing")
        assert False, "Expected ValueError for missing skill"
    except ValueError as e:
        assert "does not have skill" in str(e)


def test_grind_attribute_rejects_unknown_attribute(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Missing Attribute Grind Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_grind_points(c, 1)

    try:
        grind_attribute(c, "laser_vision")
        assert False, "Expected ValueError for unknown attribute"
    except ValueError as e:
        assert "Unknown attribute" in str(e)

def test_cannot_grind_generic_skill_when_already_at_or_above_cap(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Generic Cap Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    # Highest job level is 1, so generic cap is 10.
    add_skill_levels(c, "Lockpicking", "generic_points", 23)
    recalculate(c)

    award_grind_points(c, 3)

    assert can_grind_skill(c, "Lockpicking") is False

    try:
        grind_skill(c, "Lockpicking")
        assert False, "Expected ValueError for capped generic skill"
    except ValueError as e:
        assert "already at or above its current cap" in str(e)