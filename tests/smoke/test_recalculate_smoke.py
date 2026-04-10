from helpers.builders import make_recalculated_character


def test_recalculate_smoke_bear_berserker(initialized_content):
    character = make_recalculated_character(
        name="Smoke Bear Berserker",
        progressions=[("race", "Bear", 1), ("adventure", "Berserker", 1)],
    )

    assert character is not None
    assert isinstance(character.ability_levels, dict)
    assert character.max_hp >= 0
