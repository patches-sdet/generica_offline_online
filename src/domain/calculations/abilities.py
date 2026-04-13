from domain.content_registry import get_ability, get_progression_ability_grants

def rebuild_abilities(character) -> None:
    character.abilities = []
    character.ability_levels = {}

    granted_counts: dict[str, int] = {}

    for (ptype, progression_name), progression in character.progressions.items():
        grants = get_progression_ability_grants(ptype, progression_name)

        for ability_name, required_level in grants:
            if progression.level >= required_level:
                granted_counts[ability_name] = granted_counts.get(ability_name, 0) + 1

    # Existing progression duplicate rule
    for ability_name, count in granted_counts.items():
        character.ability_levels[ability_name] = 1 + (count - 1) * 5

    # Merge rebuilt skill levels into executable lookup
    for skill_name, level in character.skill_levels.items():
        existing = character.ability_levels.get(skill_name, 0)
        character.ability_levels[skill_name] = max(existing, level)

    # Resolve canonical Ability objects
    resolved = []
    for ability_name in sorted(character.ability_levels):
        ability = get_ability(ability_name)
        if ability is not None:
            resolved.append(ability)

    character.abilities = resolved
    