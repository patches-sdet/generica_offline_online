from application.character_creation import create_character
from application.leveling import (
    award_level_points,
    get_adventure_level_up_cost,
    can_level_adventure_job,
    level_adventure_job,
    can_learn_new_adventure_job,
    learn_new_adventure_job,
)


def test_get_adventure_level_up_cost_level_one_job_is_two(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Cost Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    assert c.get_adventure_level("Berserker") == 1
    assert get_adventure_level_up_cost(c, "Berserker") == 2


def test_get_adventure_level_up_cost_level_six_job_is_seven(initialized_content, monkeypatch):
    from application import character_creation
    from application.leveling import level_up_progression

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Cost Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    for _ in range(5):
        level_up_progression(c, ptype="adventure", name="Berserker", refill_pools=False)

    assert c.get_adventure_level("Berserker") == 6
    assert get_adventure_level_up_cost(c, "Berserker") == 7


def test_can_level_adventure_job_false_without_enough_points(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Can Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    assert can_level_adventure_job(c, "Berserker") is False


def test_can_level_adventure_job_true_with_enough_points(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Can Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_level_points(c, 2)

    assert can_level_adventure_job(c, "Berserker") is True


def test_level_adventure_job_spends_points_and_increments_progression(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Adventure Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before_level = c.get_adventure_level("Berserker")
    before_points = c.level_points
    before_strength = c.get_stat("strength")

    award_level_points(c, 2)

    new_level = level_adventure_job(c, "Berserker")

    assert new_level == before_level + 1
    assert c.get_adventure_level("Berserker") == before_level + 1
    assert c.level_points == before_points
    assert c.get_stat("strength") == before_strength + 3


def test_level_adventure_job_refills_non_hp_pools(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Pool Refill Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.current_hp = max(0, c.max_hp - 5)
    c.current_sanity = max(0, c.max_sanity - 5)
    c.current_stamina = max(0, c.max_stamina - 5)
    c.current_moxie = max(0, c.max_moxie - 5)
    c.current_fortune = max(0, c.max_fortune - 5)

    award_level_points(c, 2)
    level_adventure_job(c, "Berserker")

    assert c.current_hp == c.max_hp - 5
    assert c.current_sanity == c.max_sanity
    assert c.current_stamina == c.max_stamina
    assert c.current_moxie == c.max_moxie
    assert c.current_fortune == c.max_fortune


def test_level_adventure_job_raises_for_missing_job(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Missing Job Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_level_points(c, 2)

    try:
        level_adventure_job(c, "Wizard")
        assert False, "Expected ValueError for missing adventure job"
    except ValueError as e:
        assert "does not have adventure job" in str(e)


def test_can_learn_new_adventure_job_false_if_already_owned(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Learn Job Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_level_points(c, 1)

    assert can_learn_new_adventure_job(c, "Berserker") is False


def test_can_learn_new_adventure_job_true_with_one_point_and_missing_job(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Learn Job Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_level_points(c, 1)

    assert can_learn_new_adventure_job(c, "Archer") is True


def test_learn_new_adventure_job_costs_one_level_point(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Learn Job Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before_points = c.level_points
    award_level_points(c, 1)

    new_level = learn_new_adventure_job(c, "Archer")

    assert new_level == 1
    assert c.get_adventure_level("Archer") == 1
    assert c.level_points == before_points


def test_learn_new_adventure_job_raises_if_duplicate(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Learn Job Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_level_points(c, 1)

    try:
        learn_new_adventure_job(c, "Berserker")
        assert False, "Expected ValueError for duplicate adventure job"
    except ValueError as e:
        assert "already has adventure job" in str(e)