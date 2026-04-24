from application.character_creation import create_character
from application.runtime import award_experience_die_result
from domain.calculations import recalculate
from domain.skill_ownership import add_skill_levels

def test_attribute_only_experience_die_award_survives_recalc(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Attr XP Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    before = c.get_stat("strength")

    result = award_experience_die_result(
        c,
        stat="strength",
        skill_name=None,
        experience_die=9,
    )

    assert result["attribute_increase"] == 1
    assert result["skill_increase"] == 0
    assert c.get_stat("strength") == before + 1

    recalculate(c)
    assert c.get_stat("strength") == before + 1

def test_skill_experience_die_threshold_awards_skill_only(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Skill XP Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    add_skill_levels(c, "Lockpicking", "generic_points", 23)
    recalculate(c)

    before_skill = c.get_skill_level("Lockpicking", 0)
    before_stat = c.get_stat("dexterity")

    result = award_experience_die_result(
        c,
        stat="dexterity",
        skill_name="Lockpicking",
        experience_die=3,  # 30 > 23
    )

    assert result["skill_increase"] == 1
    assert result["attribute_increase"] == 0
    assert c.get_skill_level("Lockpicking", 0) == before_skill + 1
    assert c.get_stat("dexterity") == before_stat

def test_skill_experience_die_nine_awards_skill_and_attribute(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Skill+Attr XP Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    add_skill_levels(c, "Lockpicking", "generic_points", 23)
    recalculate(c)

    before_skill = c.get_skill_level("Lockpicking", 0)
    before_stat = c.get_stat("dexterity")

    result = award_experience_die_result(
        c,
        stat="dexterity",
        skill_name="Lockpicking",
        experience_die=9,
    )

    assert result["skill_increase"] == 1
    assert result["attribute_increase"] == 1
    assert c.get_skill_level("Lockpicking", 0) == before_skill + 1
    assert c.get_stat("dexterity") == before_stat + 1

    recalculate(c)
    assert c.get_skill_level("Lockpicking", 0) == before_skill + 1
    assert c.get_stat("dexterity") == before_stat + 1