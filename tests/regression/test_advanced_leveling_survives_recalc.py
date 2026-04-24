from application.character_creation import create_character
from application.leveling import award_level_points, level_advanced_job
from domain.calculations import recalculate


def test_advanced_level_up_survives_recalculate(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Advanced Recalc Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    c.add_progression("advanced", "Paladin", 1)

    before_level = c.get_advanced_level("Paladin")

    award_level_points(c, 2)
    level_advanced_job(c, "Paladin")

    after_level = c.get_advanced_level("Paladin")

    recalculate(c)

    assert c.get_advanced_level("Paladin") == after_level
    assert c.get_advanced_level("Paladin") == before_level + 1