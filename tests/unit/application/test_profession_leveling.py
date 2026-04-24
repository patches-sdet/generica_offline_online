from application.character_creation import create_character
from application.leveling import (
    award_level_points,
    get_profession_level_up_cost,
    can_level_profession_job,
    level_profession_job,
)


def test_get_profession_level_up_cost_is_always_one(initialized_content, monkeypatch):
    from application import character_creation
    from application.leveling import level_up_progression

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Profession Cost Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    assert c.get_profession_level("Brewer") == 1
    assert get_profession_level_up_cost(c, "Brewer") == 1

    level_up_progression(c, ptype="profession", name="Brewer", refill_pools=False)

    assert c.get_profession_level("Brewer") == 2
    assert get_profession_level_up_cost(c, "Brewer") == 1


def test_can_level_profession_job_false_without_enough_points(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Profession Can Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    assert can_level_profession_job(c, "Brewer") is False


def test_can_level_profession_job_true_with_enough_points(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Profession Can Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_level_points(c, 1)

    assert can_level_profession_job(c, "Brewer") is True


def test_level_profession_job_spends_one_point_and_increments_progression(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Profession Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before_level = c.get_profession_level("Brewer")
    before_points = c.level_points

    award_level_points(c, 1)

    new_level = level_profession_job(c, "Brewer")

    assert new_level == before_level + 1
    assert c.get_profession_level("Brewer") == before_level + 1
    assert c.level_points == before_points


def test_level_profession_job_refills_non_hp_pools(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Profession Pool Refill Test",
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
    level_profession_job(c, "Brewer")

    assert c.current_hp == c.max_hp - 5
    assert c.current_sanity == c.max_sanity
    assert c.current_stamina == c.max_stamina
    assert c.current_moxie == c.max_moxie
    assert c.current_fortune == c.max_fortune


def test_level_profession_job_raises_for_missing_profession(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Missing Profession Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    award_level_points(c, 1)

    try:
        level_profession_job(c, "Cook")
        assert False, "Expected ValueError for missing profession job"
    except ValueError as e:
        assert "does not have profession job" in str(e)