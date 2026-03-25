import random

def roll_2d10():
    return random.radint(1, 10) + random.radint(1, 10)

def skill_check(character, stat: str, skill: str):
    attr_value = getattr(character.attributes, stat)
    skill_value = character.skills.get(skill, 0)

    roll = roll_2d10()

    total = roll + attr_value + skill_value

    return {
            "roll": roll,
            "attribute": attr_value,
            "skill": skill_value,
            "total": total
            }
