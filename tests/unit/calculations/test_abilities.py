from helpers.builders import make_recalculated_character


def test_duplicate_shared_ability_uses_plus_five_stack_rule(initialized_content):
    character = make_recalculated_character(
        name="Duplicate Stack Rule",
        progressions=[("race", "Bear", 1), ("adventure", "Berserker", 1)],
    )

    assert character.ability_levels["Growl"] == 6
