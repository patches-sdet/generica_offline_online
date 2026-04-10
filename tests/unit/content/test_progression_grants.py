from domain.content_registry import get_progression_ability_grants


def test_bear_growl_grant_registered(initialized_content):
    assert ("Growl", 1) in tuple(get_progression_ability_grants("race", "Bear"))


def test_berserker_growl_grant_registered(initialized_content):
    assert ("Growl", 1) in tuple(get_progression_ability_grants("adventure", "Berserker"))
