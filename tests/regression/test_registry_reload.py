from domain.content_registry import (
    clear_content_registries,
    get_progression_ability_grants,
    has_ability,
    initialize_content_registries,
)


def test_force_reinitialize_reloads_shared_abilities_and_grants():
    clear_content_registries()
    initialize_content_registries(force=True)

    assert has_ability("Growl") is True
    assert ("Growl", 1) in tuple(get_progression_ability_grants("race", "Bear"))
    assert ("Growl", 1) in tuple(get_progression_ability_grants("adventure", "Berserker"))

    clear_content_registries()
    initialize_content_registries(force=True)

    assert has_ability("Growl") is True
    assert ("Growl", 1) in tuple(get_progression_ability_grants("race", "Bear"))
    assert ("Growl", 1) in tuple(get_progression_ability_grants("adventure", "Berserker"))
