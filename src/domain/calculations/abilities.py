from domain.content_registry import get_ability
from domain.abilities.factory import Ability

def get_abilities_for_progression(progression) -> list[Ability]:
    """
    Return canonical Ability definitions granted by a single progression.

    Expects the progression object to have:
    - progression.type
    - progression.name
    - progression.level

    This function is intentionally read-only:
    it resolves grants, but does not mutate character state.
    """

    # Temporary hard-coded mapping layer.
    # Replace this later with data-driven definitions if you move grants
    # into job/race/template content.
    progression_ability_map: dict[tuple[str, str], tuple[str, ...]] = {
        ("adventure", "Cultist"): (
            "Faith",
            "Conceal Status",
            "Curses",
            "Enhance Pain",
            "Occult Eye",
            "Transfer Wounds",
        ),
        # ("adventure", "Conjuror"): (...),
        # ("race", "Human"): (...),
        # ("advanced", "Paladin"): (...),
    }

    ability_names = progression_ability_map.get(
        (progression.type, progression.name),
        (),
    )

    granted = []
    for name in ability_names:
        granted.append(get_ability(name))

    return granted

def rebuild_abilities(character) -> None:
    granted_counts: dict[str, int] = {}
    definitions: dict[str, object] = {}

    for progression in character.progressions.values():
        for ability in get_abilities_for_progression(progression):
            if not ability.is_unlocked(character):
                continue

            granted_counts[ability.name] = granted_counts.get(ability.name, 0) + 1
            definitions[ability.name] = ability

    character.abilities = list(definitions.values())
    character.ability_levels = {}
    for name, count in definitions.items():
        count = granted_counts[name]
    
        if ability.scales_with_level:
            character.ability_levels[name] = 1 + (count - 1) * 5
        else:
            character.ability_levels[name] = 1