from helpers.builders import make_recalculated_character
from helpers.assertions import assert_has_ability


def test_lesser_healing_stacks_for_cleric_oracle(initialized_content):
    character = make_recalculated_character(
        name="Cleric Oracle",
        progressions=[("adventure", "Cleric", 1), ("adventure", "Oracle", 1)],
    )

    assert_has_ability(character, "Lesser Healing", expected_level=6)
