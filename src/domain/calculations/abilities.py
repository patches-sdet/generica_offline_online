from domain.content_registry import get_ability, get_progression_ability_names
from domain.abilities.factory import Ability

def get_abilities_for_progression(progression) -> list[Ability]:
    ability_names = get_progression_ability_names(
        progression.type,
        progression.name,
    )

    granted = []
    for name in ability_names:
        ability = get_ability(name)
        
        granted.append(ability)

    return granted

def rebuild_abilities(character) -> None:
    granted_counts: dict[str, int] = {}
    definitions_by_name: dict[str, object] = {}

    for progression in character.progressions.values():
        for ability in get_abilities_for_progression(progression):
            if not ability.is_unlocked(character):
                continue

            granted_counts[ability.name] = granted_counts.get(ability.name, 0) + 1
            definitions_by_name[ability.name] = ability

    character.abilities = list(definitions_by_name.values())
    character.ability_levels = {}

    for name, ability in definitions_by_name.items():
        count = granted_counts[name]

        if ability.is_leveled:
            character.ability_levels[name] = 1 + (count - 1) * 5
        else:
            character.ability_levels[name] = 1