from __future__ import annotations


def assert_has_ability(character, ability_name: str, expected_level: int | None = None) -> None:
    assert ability_name in character.ability_levels, f"Expected ability '{ability_name}' to exist."
    if expected_level is not None:
        assert character.ability_levels[ability_name] == expected_level


def assert_ability_provenance(
    character,
    ability_name: str,
    *,
    expected_final_level: int,
    expected_progression_level: int | None = None,
    expected_owned_level: int | None = None,
) -> None:
    assert ability_name in character.ability_provenance, (
        f"Expected ability provenance for '{ability_name}' to exist."
    )

    provenance = character.ability_provenance[ability_name]
    final = provenance["final"]

    assert final["effective_level"] == expected_final_level

    if expected_progression_level is not None:
        assert final["progression_level"] == expected_progression_level

    if expected_owned_level is not None:
        assert final["owned_level"] == expected_owned_level


def assert_progression_grants(grants, ability_name: str, required_level: int = 1) -> None:
    assert (ability_name, required_level) in tuple(grants), (
        f"Expected grant ({ability_name!r}, {required_level}) in {grants!r}"
    )
