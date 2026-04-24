import random
from domain.attributes import ATTRIBUTE_NAMES
from domain.calculations.rolls import apply_roll_modifiers

def roll_2d10() -> int:
    """
    Standard 2d10 summed as ones dice.
    Zeroes count as tens in the tabletop rules, but this helper uses the
    engine's existing 1..10 range convention. Used almost exclusively for Character Creation
    """
    return random.randint(1, 10) + random.randint(1, 10)

def roll_1d100() -> int:
    """
    Core percentile roll.
    """
    return random.randint(1, 100)

def roll_experience_die() -> int:
    """
    Experience die is a single d10 interpreted as 0..9.
    """
    return random.randint(0, 9)

def main_roll(
    character,
    stat: str,
    skill: str | None = None,
    *,
    apply_modifiers: bool = True,
) -> dict[str, int | bool | str | None]:
    """
    Core resolved roll summary.

    Returns:
    {
        "roll": raw d100 result,
        "modified_roll": roll after roll modifiers,
        "attribute": current attribute value,
        "skill": current skill value,
        "total": modified_roll + attribute + skill,
        "stat": stat name,
        "skill_name": skill name or None,
        "critical_success": bool,
        "automatic_failure": bool,
    }

    Rules currently implemented:
    - raw roll >= 90 => automatic success / critical success
    - raw roll <= 10 => automatic failure
    - total is still returned for debugging / downstream logic
    """
    if stat not in ATTRIBUTE_NAMES:
        raise ValueError(f"Unknown attribute for roll: {stat!r}")

    attr_value = character.get_stat(stat)
    skill_value = character.get_skill_level(skill, 0) if skill else 0

    raw_roll = roll_1d100()
    modified_roll = apply_roll_modifiers(character, raw_roll) if apply_modifiers else raw_roll

    critical_success = raw_roll >= 90
    automatic_failure = raw_roll <= 10

    total = modified_roll + attr_value + skill_value

    return {
        "roll": raw_roll,
        "modified_roll": modified_roll,
        "attribute": attr_value,
        "skill": skill_value,
        "total": total,
        "stat": stat,
        "skill_name": skill,
        "critical_success": critical_success,
        "automatic_failure": automatic_failure,
    }