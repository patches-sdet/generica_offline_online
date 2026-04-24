from application.character_creation import create_character
from application.leveling import (
    award_level_points,
    get_race_level_up_cost,
    can_level_race_progression,
    level_race_progression,
)


def test_get_race_level_up_cost_level_one_is_one(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Race Cost Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    assert c.get_race_level("Human") == 1
    assert get_race_level_up_cost(c, "Human") == 1


def test_get_race_level_up_cost_level_three_is_three(initialized_content, monkeypatch):
    from application import character_creation
    from application.leveling import level_up_progression

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Race Cost Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    level_up_progression(c, ptype="race", name="Human", refill_pools=False)
    level_up_progression(c, ptype="race", name="Human", refill_pools=False)

    assert c.get_race_level("Human") == 3
    assert get_race_level_up_cost(c, "Human") == 3


def test_can_level_race_progression_false_without_enough_points(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Race Can Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    assert can_level_race_progression(c, "Human") is False


def test_can_level_race_progression_true_with_enough_points(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Race Can Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_level_points(c, 1)

    assert can_level_race_progression(c, "Human") is True


def test_level_race_progression_spends_points_and_increments_progression(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Race Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before_level = c.get_race_level("Human")
    before_points = c.level_points

    award_level_points(c, 1)

    new_level = level_race_progression(c, "Human")

    assert new_level == before_level + 1
    assert c.get_race_level("Human") == before_level + 1
    assert c.level_points == before_points


def test_level_race_progression_refills_non_hp_pools(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Race Pool Refill Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.current_hp = max(0, c.max_hp - 5)
    c.current_sanity = max(0, c.max_sanity - 5)
    c.current_stamina = max(0, c.max_stamina - 5)
    c.current_moxie = max(0, c.max_moxie - 5)
    c.current_fortune = max(0, c.max_fortune - 5)

    award_level_points(c, 1)
    level_race_progression(c, "Human")

    assert c.current_hp == c.max_hp - 5
    assert c.current_sanity == c.max_sanity
    assert c.current_stamina == c.max_stamina
    assert c.current_moxie == c.max_moxie
    assert c.current_fortune == c.max_fortune


def test_level_race_progression_raises_for_missing_race(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Missing Race Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_level_points(c, 1)

    try:
        level_race_progression(c, "Elf")
        assert False, "Expected ValueError for missing race progression"
    except ValueError as e:
        assert "does not have race progression" in str(e)