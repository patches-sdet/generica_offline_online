from application.character_creation import create_character
from application.leveling import award_level_points, level_race_progression
from domain.calculations import recalculate


def test_race_level_up_survives_recalculate(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Race Recalc Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before_level = c.get_race_level("Human")

    award_level_points(c, 1)
    level_race_progression(c, "Human")

    after_level = c.get_race_level("Human")

    recalculate(c)

    assert c.get_race_level("Human") == after_level
    assert c.get_race_level("Human") == before_level + 1