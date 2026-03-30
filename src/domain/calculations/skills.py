def rebuild_skills(character, effects=None):
    skills = {}

    for ability in getattr(character, "abilities", []):
        if ability.is_skill:
            base = skills.get(ability.name, 0)
            skills[ability.name] = max(base, 1)

    character.skills = skills