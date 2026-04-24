from application.character_creation import create_character
from application.leveling import (
    award_level_points,
    get_advanced_level_up_cost,
    can_level_advanced_job,
    level_advanced_job,
    can_learn_new_advanced_job,
    learn_new_advanced_job,
)


def test_get_advanced_level_up_cost_level_one_job_is_two(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Advanced Cost Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.add_progression("advanced", "Paladin", 1)

    assert c.get_advanced_level("Paladin") == 1
    assert get_advanced_level_up_cost(c, "Paladin") == 2


def test_get_advanced_level_up_cost_level_six_job_is_seven(initialized_content, monkeypatch):
    from application import character_creation
    from application.leveling import level_up_progression

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Advanced Cost Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.add_progression("advanced", "Paladin", 1)

    for _ in range(5):
        level_up_progression(c, ptype="advanced", name="Paladin", refill_pools=False)

    assert c.get_advanced_level("Paladin") == 6
    assert get_advanced_level_up_cost(c, "Paladin") == 7


def test_can_level_advanced_job_false_without_enough_points(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Advanced Can Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.add_progression("advanced", "Paladin", 1)

    assert can_level_advanced_job(c, "Paladin") is False


def test_can_level_advanced_job_true_with_enough_points(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Advanced Can Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.add_progression("advanced", "Paladin", 1)
    award_level_points(c, 2)

    assert can_level_advanced_job(c, "Paladin") is True


def test_level_advanced_job_spends_points_and_increments_progression(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Advanced Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.add_progression("advanced", "Paladin", 1)

    before_level = c.get_advanced_level("Paladin")
    before_points = c.level_points

    award_level_points(c, 2)

    new_level = level_advanced_job(c, "Paladin")

    assert new_level == before_level + 1
    assert c.get_advanced_level("Paladin") == before_level + 1
    assert c.level_points == before_points


def test_level_advanced_job_refills_non_hp_pools(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Advanced Pool Refill Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.add_progression("advanced", "Paladin", 1)

    c.current_hp = max(0, c.max_hp - 5)
    c.current_sanity = max(0, c.max_sanity - 5)
    c.current_stamina = max(0, c.max_stamina - 5)
    c.current_moxie = max(0, c.max_moxie - 5)
    c.current_fortune = max(0, c.max_fortune - 5)

    award_level_points(c, 2)
    level_advanced_job(c, "Paladin")

    assert c.current_hp == c.max_hp - 5
    assert c.current_sanity == c.max_sanity
    assert c.current_stamina == c.max_stamina
    assert c.current_moxie == c.max_moxie
    assert c.current_fortune == c.max_fortune


def test_level_advanced_job_raises_for_missing_job(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Missing Advanced Job Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_level_points(c, 2)

    try:
        level_advanced_job(c, "Paladin")
        assert False, "Expected ValueError for missing advanced job"
    except ValueError as e:
        assert "does not have advanced job" in str(e)


def test_can_learn_new_advanced_job_false_if_already_owned(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Learn Advanced Job Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.add_progression("advanced", "Paladin", 1)
    award_level_points(c, 1)

    assert can_learn_new_advanced_job(c, "Paladin") is False


def test_can_learn_new_advanced_job_true_with_one_point_and_missing_job(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Learn Advanced Job Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_level_points(c, 1)

    assert can_learn_new_advanced_job(c, "Paladin") is True


def test_learn_new_advanced_job_costs_one_level_point(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Learn Advanced Job Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before_points = c.level_points
    award_level_points(c, 1)

    new_level = learn_new_advanced_job(c, "Paladin")

    assert new_level == 1
    assert c.get_advanced_level("Paladin") == 1
    assert c.level_points == before_points


def test_learn_new_advanced_job_raises_if_duplicate(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Learn Advanced Job Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.add_progression("advanced", "Paladin", 1)
    award_level_points(c, 1)

    try:
        learn_new_advanced_job(c, "Paladin")
        assert False, "Expected ValueError for duplicate advanced job"
    except ValueError as e:
        assert "already has advanced job" in str(e)