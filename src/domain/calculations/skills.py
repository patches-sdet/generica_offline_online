def rebuild_skills(character, effects=None) -> None:
    skills: dict[str, int] = {}

    for ability in getattr(character, "abilities", []):
        if not ability.is_skill:
            continue

        skills[ability.name] = character.ability_levels.get(ability.name, 1)

    character.skills = skills