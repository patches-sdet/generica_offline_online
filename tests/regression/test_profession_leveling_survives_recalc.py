from application.character_creation import create_character
from application.leveling import award_level_points, level_profession_job
from domain.calculations import recalculate


def test_profession_level_up_survives_recalculate(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Profession Recalc Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before_level = c.get_profession_level("Brewer")

    award_level_points(c, 1)
    level_profession_job(c, "Brewer")

    after_level = c.get_profession_level("Brewer")

    recalculate(c)

    assert c.get_profession_level("Brewer") == after_level
    assert c.get_profession_level("Brewer") == before_level + 1