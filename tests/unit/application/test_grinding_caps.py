from application.character_creation import create_character
from application.leveling import (
    award_grind_points,
    get_related_skill_cap,
    can_grind_skill,
    grind_skill,
)
from domain.calculations import recalculate
from domain.skill_ownership import add_skill_levels


def test_generic_skill_cap_uses_highest_job_level_times_ten(initialized_content, monkeypatch):
    from application import character_creation
    from application.leveling import level_up_progression

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Generic Skill Cap Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    # Raise Berserker from 1 to 3 so highest job level becomes 3.
    level_up_progression(c, ptype="adventure", name="Berserker", refill_pools=False)
    level_up_progression(c, ptype="adventure", name="Berserker", refill_pools=False)

    add_skill_levels(c, "Lockpicking", "generic_points", 30)
    recalculate(c)

    assert get_related_skill_cap(c, "Lockpicking") == 30
    assert can_grind_skill(c, "Lockpicking") is False


def test_job_skill_cap_uses_related_job_level_times_five(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Job Skill Cap Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    # Growl should be related to Berserker and cap at 5 when Berserker is level 1.
    add_skill_levels(c, "Growl", "job_points:Berserker", 5)
    recalculate(c)

    assert get_related_skill_cap(c, "Growl") == 5
    assert can_grind_skill(c, "Growl") is False


def test_job_skill_below_cap_can_still_be_ground(initialized_content, monkeypatch):
    from application import character_creation

    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    c = create_character(
        name="Job Skill Grind Test",
        base_race_names=["Human"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    add_skill_levels(c, "Growl", "job_points:Berserker", 4)
    recalculate(c)

    assert get_related_skill_cap(c, "Growl") == 5

    award_grind_points(c, 1)
    new_level = grind_skill(c, "Growl")

    assert new_level == 5
    assert c.get_skill_level("Growl", 0) == 5