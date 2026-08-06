from pathlib import Path

from domain.content_registry import get_progression_ability_grants


def test_bear_growl_grant_registered(initialized_content):
    assert ("Growl", 1) in tuple(get_progression_ability_grants("race", "Bear"))


def test_berserker_growl_grant_registered(initialized_content):
    assert ("Growl", 1) in tuple(get_progression_ability_grants("adventure", "Berserker"))


def test_berserker_shared_grants_match_yaml_pilot_slice(initialized_content):
    yaml_path = Path("src/domain/abilities/adventure/berserker.yml")
    definition = yaml.safe_load(yaml_path.read_text())

    expected_grants = {
        (grant["name"], grant.get("required_level", 1))
        for grant in definition["grants"]
    }

    registered_grants = set(get_progression_ability_grants("adventure", "Berserker"))

    assert expected_grants <= registered_grants
