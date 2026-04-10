from __future__ import annotations


def assert_has_ability(character, ability_name: str, expected_level: int | None = None) -> None:
    assert ability_name in character.ability_levels, f"Expected ability '{ability_name}' to exist."
    if expected_level is not None:
        assert character.ability_levels[ability_name] == expected_level


def assert_progression_grants(grants, ability_name: str, required_level: int = 1) -> None:
    assert (ability_name, required_level) in tuple(grants), (
        f"Expected grant ({ability_name!r}, {required_level}) in {grants!r}"
    )
