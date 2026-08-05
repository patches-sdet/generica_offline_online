from __future__ import annotations

from typing import Any

from domain.content_registry import get_ability, get_progression_ability_grants


def _build_progression_ability_contributions(character) -> dict[str, dict[str, dict[str, Any]]]:
    contributions: dict[str, dict[str, dict[str, Any]]] = {}
    granted_sources: dict[str, list[str]] = {}

    for (ptype, progression_name), progression in character.progressions.items():
        grants = get_progression_ability_grants(ptype, progression_name)
        source_key = f"{ptype}:{progression_name}"

        for ability_name, required_level in grants:
            if progression.level < required_level:
                continue

            granted_sources.setdefault(ability_name, []).append(source_key)

    for ability_name, source_occurrences in granted_sources.items():
        ability_sources = contributions.setdefault(ability_name, {})

        for grant_index, source_key in enumerate(sorted(source_occurrences)):
            effective_level = 1 if grant_index == 0 else 5
            ptype, progression_name = source_key.split(":", 1)
            source_entry = ability_sources.setdefault(
                source_key,
                {
                    "type": ptype,
                    "name": progression_name,
                    "grant_count": 0,
                    "effective_level": 0,
                },
            )
            source_entry["grant_count"] += 1
            source_entry["effective_level"] += effective_level

    return contributions


def _build_owned_ability_contributions(character) -> dict[str, dict[str, int]]:
    contributions: dict[str, dict[str, int]] = {}

    for ability_name, source_map in character.skill_sources.items():
        positive_sources = {
            source: levels
            for source, levels in source_map.items()
            if levels > 0
        }
        if positive_sources:
            contributions[ability_name] = positive_sources

    return contributions


def _finalize_ability_provenance(
    progression_contributions: dict[str, dict[str, dict[str, Any]]],
    owned_contributions: dict[str, dict[str, int]],
) -> dict[str, dict[str, Any]]:
    provenance: dict[str, dict[str, Any]] = {}
    ability_names = set(progression_contributions) | set(owned_contributions)

    for ability_name in sorted(ability_names):
        progression_sources = progression_contributions.get(ability_name, {})
        owned_sources = owned_contributions.get(ability_name, {})

        progression_total = sum(
            source_info["effective_level"] for source_info in progression_sources.values()
        )
        owned_total = sum(owned_sources.values())
        final_level = progression_total + owned_total

        provenance[ability_name] = {
            "progression": progression_sources,
            "owned": owned_sources,
            "final": {
                "progression_level": progression_total,
                "owned_level": owned_total,
                "effective_level": final_level,
                "rule": "sum(progression_duplicate_rule + owned_levels)",
            },
        }

    return provenance


def rebuild_abilities(character) -> None:
    character.abilities = []
    character.ability_levels = {}
    character.ability_provenance = {}

    progression_contributions = _build_progression_ability_contributions(character)
    owned_contributions = _build_owned_ability_contributions(character)

    character.ability_provenance = _finalize_ability_provenance(
        progression_contributions,
        owned_contributions,
    )

    for ability_name, provenance in character.ability_provenance.items():
        final_level = provenance["final"]["effective_level"]
        if final_level > 0:
            character.ability_levels[ability_name] = final_level

    resolved = []
    for ability_name in sorted(character.ability_levels):
        ability = get_ability(ability_name)
        if ability is not None:
            resolved.append(ability)

    character.abilities = resolved
    
