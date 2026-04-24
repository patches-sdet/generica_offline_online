from application.character_creation import create_character
from application.leveling import level_up_progression


def test_level_up_progression_uses_progressions_model(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Level Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before = c.get_adventure_level("Berserker")
    new_level = level_up_progression(c, ptype="adventure", name="Berserker")

    assert new_level == before + 1
    assert c.get_adventure_level("Berserker") == before + 1


def test_level_up_progression_applies_berserker_strength_increase(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Level Stat Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before_level = c.get_adventure_level("Berserker")
    before_stat = c.get_stat("strength")

    new_level = level_up_progression(c, ptype="adventure", name="Berserker")

    assert new_level == before_level + 1
    assert c.get_adventure_level("Berserker") == before_level + 1
    assert c.get_stat("strength") == before_stat + 3