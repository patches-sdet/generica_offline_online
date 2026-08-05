from __future__ import annotations

from application.character_creation import create_character
from domain.calculations import recalculate
from domain.character import Character
from domain.progression import Progression
from domain.skill_ownership import set_skill_levels


def make_character(name: str = "Test Character") -> Character:
    return Character(name=name)


def add_progression(character: Character, ptype: str, name: str, level: int = 1) -> Character:
    character.progressions[(ptype, name)] = Progression(type=ptype, name=name, level=level)
    return character


def make_recalculated_character(
    *,
    name: str = "Test Character",
    progressions: list[tuple[str, str, int]] | None = None,
) -> Character:
    character = make_character(name=name)
    for ptype, progression_name, level in progressions or []:
        add_progression(character, ptype, progression_name, level)
    recalculate(character)
    return character


def add_skill_source(
    character: Character,
    skill_name: str,
    source: str,
    levels: int,
) -> Character:
    set_skill_levels(character, skill_name, source=source, levels=levels)
    return character


def make_created_character(
    *,
    name: str = "Workflow Character",
    base_race_names: list[str] | None = None,
    adventure_job_names: list[str] | None = None,
    profession_job_names: list[str] | None = None,
) -> Character:
    return create_character(
        name=name,
        base_race_names=base_race_names or ["Human"],
        adventure_job_names=adventure_job_names or [],
        profession_job_names=profession_job_names or [],
    )
