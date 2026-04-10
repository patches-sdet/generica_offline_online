from domain.content_registry import get_progression_ability_grants
from helpers.builders import make_recalculated_character
from helpers.assertions import assert_has_ability, assert_progression_grants


def test_bear_and_berserker_both_grant_growl(initialized_content):
    bear_grants = get_progression_ability_grants("race", "Bear")
    berserker_grants = get_progression_ability_grants("adventure", "Berserker")

    assert_progression_grants(bear_grants, "Growl", 1)
    assert_progression_grants(berserker_grants, "Growl", 1)


def test_growl_stacks_to_six_for_bear_berserker(initialized_content):
    character = make_recalculated_character(
        name="Growl Stack",
        progressions=[("race", "Bear", 1), ("adventure", "Berserker", 1)],
    )

    assert_has_ability(character, "Growl", expected_level=6)
