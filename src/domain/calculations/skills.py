# domain/calculations/skills.py

def rebuild_skills(character):
    skills = set()

    for ability in getattr(character, "abilities", []):
        if hasattr(ability, "is_skill") and ability.is_skill == True:
            skills.update(ability.skills)

    character.skills = skills
