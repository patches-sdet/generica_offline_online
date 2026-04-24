from application.character_creation import create_character
from application.leveling import award_level_points, level_adventure_job
from domain.calculations import recalculate


def test_adventure_level_up_survives_recalculate(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Adventure Recalc Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before_strength = c.get_stat("strength")

    award_level_points(c, 2)
    level_adventure_job(c, "Berserker")

    after_level = c.get_adventure_level("Berserker")
    after_strength = c.get_stat("strength")

    recalculate(c)

    assert c.get_adventure_level("Berserker") == after_level
    assert c.get_stat("strength") == after_strength
    assert c.get_stat("strength") == before_strength + 3