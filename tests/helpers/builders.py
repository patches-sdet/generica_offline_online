from __future__ import annotations

from domain.character import Character
from domain.progression import Progression
from domain.calculations import recalculate


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
