from domain.effects.aggregation import collect_effects
from helpers.builders import make_recalculated_character


def test_collect_effects_returns_flat_list(initialized_content):
    character = make_recalculated_character(
        name="Effect Aggregation",
        progressions=[("adventure", "Cleric", 1)],
    )

    effects = collect_effects(character)

    assert isinstance(effects, list)
    assert not any(isinstance(item, list) for item in effects)
