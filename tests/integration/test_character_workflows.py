from application import character_creation
from application.character_creation import create_character
from application.leveling import award_level_points, level_adventure_job
from application.runtime import execute_ability
from domain.abilities.factory import make_ability
from domain.calculations import recalculate
from domain.content_registry import register_ability
from helpers.assertions import assert_ability_provenance, assert_has_ability
from helpers.builders import add_skill_source


def test_creation_progression_and_recalculation_workflow(initialized_content, monkeypatch):
    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    character = create_character(
        name="Workflow Test",
        base_race_names=["Bear"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )

    assert_has_ability(character, "Growl", expected_level=6)
    assert_ability_provenance(
        character,
        "Growl",
        expected_final_level=6,
        expected_progression_level=6,
        expected_owned_level=0,
    )

    before_strength = character.get_stat("strength")

    award_level_points(character, 2)
    level_adventure_job(character, "Berserker")
    recalculate(character)

    assert character.get_adventure_level("Berserker") == 2
    assert character.get_stat("strength") == before_strength + 3
    assert_has_ability(character, "Growl", expected_level=6)
    assert_ability_provenance(
        character,
        "Growl",
        expected_final_level=6,
        expected_progression_level=6,
        expected_owned_level=0,
    )


def test_execute_ability_spends_resources_and_rebuilds_after_resolution(
    initialized_content,
    monkeypatch,
):
    monkeypatch.setattr(character_creation, "roll_attributes", lambda: [])

    character = create_character(
        name="Runtime Workflow Test",
        base_race_names=["Bear"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
    )
    runtime_ability = make_ability(
        name="Workflow Runtime Spend",
        unlock_condition=lambda _: True,
        execute=lambda caster, targets: [],
        cost=5,
        cost_pool="sanity",
        is_skill=True,
        auto_register=False,
    )
    register_ability(runtime_ability)
    add_skill_source(character, "Workflow Runtime Spend", "generic_points", 2)
    recalculate(character)

    character.current_sanity = character.max_sanity

    before_sanity = character.current_sanity
    before_levels = dict(character.ability_levels)

    result = execute_ability(
        character,
        "Workflow Runtime Spend",
        explicit_targets=[character],
        rebuild_after=True,
    )

    assert result["ability"].name == "Workflow Runtime Spend"
    assert character.current_sanity == before_sanity - 5
    assert dict(character.ability_levels) == before_levels
    assert_ability_provenance(
        character,
        "Workflow Runtime Spend",
        expected_final_level=2,
        expected_progression_level=0,
        expected_owned_level=2,
    )
