from helpers.assertions import assert_ability_provenance
from helpers.builders import add_skill_source, make_character, make_recalculated_character
from domain.calculations import recalculate
from domain.progression import Progression


def test_duplicate_shared_ability_uses_plus_five_stack_rule(initialized_content):
    character = make_recalculated_character(
        name="Duplicate Stack Rule",
        progressions=[("race", "Bear", 1), ("adventure", "Berserker", 1)],
    )

    assert character.ability_levels["Growl"] == 6


def test_owned_skill_levels_add_to_progression_ability_total(initialized_content):
    character = make_character("Ability Provenance Test")
    character.progressions[("race", "Bear")] = Progression(
        type="race",
        name="Bear",
        level=1,
    )
    character.progressions[("adventure", "Berserker")] = Progression(
        type="adventure",
        name="Berserker",
        level=1,
    )
    add_skill_source(character, "Growl", "job_points:Berserker", 3)

    recalculate(character)

    assert character.ability_levels["Growl"] == 9
    assert_ability_provenance(
        character,
        "Growl",
        expected_final_level=9,
        expected_progression_level=6,
        expected_owned_level=3,
    )
    assert character.ability_provenance["Growl"]["progression"]["adventure:Berserker"]["effective_level"] == 1
    assert character.ability_provenance["Growl"]["progression"]["race:Bear"]["effective_level"] == 5
    assert character.ability_provenance["Growl"]["owned"]["job_points:Berserker"] == 3
