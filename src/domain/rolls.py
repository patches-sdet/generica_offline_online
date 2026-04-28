from __future__ import annotations
import random
from application.experience import ExperienceGainResult, resolve_experience_die
from domain.attributes import ATTRIBUTE_NAMES
from domain.calculations.rolls import apply_roll_modifiers


def roll_2d10() -> int:
    return random.randint(1, 10) + random.randint(1, 10)


def roll_1d100() -> int:
    return random.randint(1, 100)


def roll_experience_die() -> int:
    """
    Experience die is a single d10 interpreted as 0..9.
    """
    return random.randint(0, 9)

def roll_experience_die() -> int:
    return randint(1, 9)

def apply_success_experience(
    character,
    *,
    success: bool,
    attribute_name: str | None = None,
    skill_name: str | None = None,
    experience_die: int | None = None,
    rebuild: bool = True,
) -> ExperienceGainResult:
    """
    Thin roll-layer adapter.

    Keeps the advancement rules in application.runtime.experience,
    while giving domain.rolls.main_roll(...) a small integration point.
    """
    die = experience_die if experience_die is not None else roll_experience_die()

    return resolve_experience_die(
        character,
        success=success,
        experience_die=die,
        attribute_name=attribute_name,
        skill_name=skill_name,
        rebuild=rebuild,
    )

def main_roll(
    character,
    stat: str,
    skill: str | None = None,
    *,
    difficulty: int | None = None,
    apply_modifiers: bool = True,
    apply_experience: bool = False,
) -> dict[str, int | bool | str | None | dict]:
    """
    Core resolved roll summary.

    If difficulty is provided:
        success = total >= difficulty

    Automatic rules:
        raw roll >= 90 => critical success / automatic success
        raw roll <= 10 => automatic failure

    Experience advancement only runs when:
        apply_experience=True
        AND success=True
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

    if automatic_failure:
        success = False
    elif critical_success:
        success = True
    elif difficulty is not None:
        success = total >= difficulty
    else:
        success = None

    experience_die = None
    experience_result = None

    if apply_experience:
        if success is None:
            raise ValueError(
                "Cannot apply experience without a resolved success value. "
                "Pass difficulty=... or resolve experience outside main_roll()."
            )

        experience_die = roll_experience_die()

        experience_result_obj = resolve_experience_die(
            character,
            success=success,
            experience_die=experience_die,
            attribute_name=stat,
            skill_name=skill,
            rebuild=True,
        )

        experience_result = {
            "experience_die": experience_result_obj.experience_die,
            "success": experience_result_obj.success,
            "attribute_gained": experience_result_obj.attribute_gained,
            "skill_gained": experience_result_obj.skill_gained,
            "attribute_name": experience_result_obj.attribute_name,
            "skill_name": experience_result_obj.skill_name,
            "gained_anything": experience_result_obj.gained_anything,
        }

    return {
        "roll": raw_roll,
        "modified_roll": modified_roll,
        "attribute": attr_value,
        "skill": skill_value,
        "total": total,
        "difficulty": difficulty,
        "success": success,
        "stat": stat,
        "skill_name": skill,
        "critical_success": critical_success,
        "automatic_failure": automatic_failure,
        "experience_die": experience_die,
        "experience_result": experience_result,
    }