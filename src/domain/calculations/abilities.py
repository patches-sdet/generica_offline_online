from domain.content_registry import get_ability, get_progression_ability_grants
from domain.abilities.factory import Ability


def get_abilities_for_progression(progression, character) -> list[Ability]:
    granted: list[Ability] = []

    for ability_name, required_level in get_progression_ability_grants(
        progression.type,
        progression.name,
    ):
        if progression.level < required_level:
            continue

        ability = get_ability(ability_name)

        # Optional: keep this only if abilities still support
        # intrinsic non-progression unlock rules
        #if not ability.is_unlocked(character):
        #    continue

        granted.append(ability)

    return granted

def rebuild_abilities(character) -> None:
    granted_counts: dict[str, int] = {}
    definitions_by_name: dict[str, Ability] = {}

    for progression in character.progressions.values():
        for ability in get_abilities_for_progression(progression, character):
            granted_counts[ability.name] = granted_counts.get(ability.name, 0) + 1
            definitions_by_name[ability.name] = ability

    character.abilities = sorted(definitions_by_name.values(), key=lambda a: a.name)
    character.ability_levels = {}

    for name, ability in definitions_by_name.items():
        count = granted_counts[name]

        if ability.scales_with_level:
            character.ability_levels[name] = 1 + (count - 1) * 5
        else:
            character.ability_levels[name] = 1