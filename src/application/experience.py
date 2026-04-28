from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from domain.calculations import recalculate

__all__ = [
    "award_attribute_experience",
    "award_skill_experience",
    "resolve_experience_die",
    "should_gain_attribute_from_experience_die",
    "should_gain_skill_from_experience_die",
]

EXPERIENCE_SOURCE = "experience"

@dataclass(frozen=True, slots=True)
class ExperienceGainResult:
    experience_die: int
    success: bool
    attribute_gained: bool = False
    skill_gained: bool = False
    attribute_name: Optional[str] = None
    skill_name: Optional[str] = None

    @property
    def gained_anything(self) -> bool:
        return self.attribute_gained or self.skill_gained

def _validate_experience_die(experience_die: int) -> None:
    if not 0 <= experience_die <= 9:
        raise ValueError(f"experience_die must be between 0 and 9: {experience_die!r}")

def _get_attribute_value(character, attribute_name: str) -> int:
    if hasattr(character.attributes, "get"):
        return character.attributes.get(attribute_name)

    if hasattr(character.attributes, "values"):
        return character.attributes.values[attribute_name]

    return getattr(character.attributes, attribute_name)

def _increase_manual_attribute(
    character,
    attribute_name: str,
    source: str = EXPERIENCE_SOURCE,
    amount: int = 1,
) -> None:
    if amount <= 0:
        raise ValueError(f"amount must be positive: {amount!r}")

    character.manual_attribute_increases.setdefault(attribute_name, {})
    character.manual_attribute_increases[attribute_name][source] = (
        character.manual_attribute_increases[attribute_name].get(source, 0) + amount
    )

def _increase_skill_source(
    character,
    skill_name: str,
    source: str = EXPERIENCE_SOURCE,
    amount: int = 1,
) -> None:
    if amount <= 0:
        raise ValueError(f"amount must be positive: {amount!r}")

    character.skill_sources.setdefault(skill_name, {})
    character.skill_sources[skill_name][source] = (
        character.skill_sources[skill_name].get(source, 0) + amount
    )

def should_gain_attribute_from_experience_die(
    character,
    attribute_name: str,
    experience_die: int,
) -> bool:
    """
    Rule:
        experience_die * 10 > attribute
        OR
        experience_die == 9
    """
    _validate_experience_die(experience_die)

    if experience_die == 9:
        return True

    return experience_die * 10 > _get_attribute_value(character, attribute_name)

def should_gain_skill_from_experience_die(
    character,
    skill_name: str,
    experience_die: int,
) -> bool:
    """
    Rule:
        experience_die * 10 > skill
        OR
        experience_die == 9
    """
    _validate_experience_die(experience_die)

    if experience_die == 9:
        return True

    current_skill = character.skill_levels.get(skill_name, 0)
    return experience_die * 10 > current_skill

def award_attribute_experience(
    character,
    attribute_name: str,
    experience_die: int,
    *,
    rebuild: bool = True,
) -> bool:
    """
    Applies a permanent attribute increase if the experience-die rule passes.

    Persistent storage only:
        character.manual_attribute_increases
    """
    if not should_gain_attribute_from_experience_die(
        character,
        attribute_name,
        experience_die,
    ):
        return False

    _increase_manual_attribute(character, attribute_name)

    if rebuild:
        recalculate(character)

    return True

def award_skill_experience(
    character,
    skill_name: str,
    experience_die: int,
    *,
    rebuild: bool = True,
) -> bool:
    """
    Applies a permanent skill increase if the experience-die rule passes.

    Persistent storage only:
        character.skill_sources
    """
    if not should_gain_skill_from_experience_die(character, skill_name, experience_die):
        return False

    _increase_skill_source(character, skill_name)

    if rebuild:
        recalculate(character)

    return True

def resolve_experience_die(
    character,
    *,
    success: bool,
    experience_die: int,
    attribute_name: str | None = None,
    skill_name: str | None = None,
    rebuild: bool = True,
) -> ExperienceGainResult:
    """
    Central experience-die advancement entry point.

    Intended roll flow:
        roll
        -> success/failure
        -> if success, resolve experience die
        -> mutate persistent growth
        -> recalculate

    Rules:
        Attribute check:
            experience_die * 10 > attribute -> +1 attribute
            experience_die == 9 -> +1 attribute

        Skill check:
            experience_die * 10 > skill -> +1 skill
            experience_die == 9 -> +1 skill AND +1 linked attribute
    """
    _validate_experience_die(experience_die)

    if not success:
        return ExperienceGainResult(
            experience_die=experience_die,
            success=False,
            attribute_name=attribute_name,
            skill_name=skill_name,
        )

    attribute_gained = False
    skill_gained = False

    if skill_name is not None:
        if should_gain_skill_from_experience_die(character, skill_name, experience_die):
            _increase_skill_source(character, skill_name)
            skill_gained = True

        if experience_die == 9 and attribute_name is not None:
            _increase_manual_attribute(character, attribute_name)
            attribute_gained = True

    elif attribute_name is not None:
        if should_gain_attribute_from_experience_die(
            character,
            attribute_name,
            experience_die,
        ):
            _increase_manual_attribute(character, attribute_name)
            attribute_gained = True

    if rebuild and (attribute_gained or skill_gained):
        recalculate(character)

    return ExperienceGainResult(
        experience_die=experience_die,
        success=True,
        attribute_gained=attribute_gained,
        skill_gained=skill_gained,
        attribute_name=attribute_name,
        skill_name=skill_name,
    )
