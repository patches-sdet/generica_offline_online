from __future__ import annotations

def _ensure_skill_entry(character, skill_name: str) -> None:
    character.skill_sources.setdefault(skill_name, {})

def add_skill_levels(character, skill_name: str, source: str, levels: int = 1) -> None:
    if levels <= 0:
        raise ValueError(f"Levels must be positive for {skill_name!r}: {levels}")

    _ensure_skill_entry(character, skill_name)

    current = character.skill_sources[skill_name].get(source, 0)
    character.skill_sources[skill_name][source] = current + levels

def set_skill_levels(character, skill_name: str, source: str, levels: int) -> None:
    if levels < 0:
        raise ValueError(f"Levels cannot be negative for {skill_name!r}: {levels}")

    if levels == 0:
        remove_skill_source(character, skill_name, source)
        return

    character.skill_sources.setdefault(skill_name, {})
    character.skill_sources[skill_name][source] = levels

def remove_skill_source(character, skill_name: str, source: str) -> None:
    source_map = character.skill_sources.get(skill_name)
    if not source_map:
        return

    source_map.pop(source, None)

    if not source_map:
        character.skill_sources.pop(skill_name, None)

    _ensure_skill_entry(character, skill_name)
    character.skill_sources[skill_name][source] = levels

def get_total_skill_levels(character, skill_name: str) -> int:
    return sum(character.skill_sources.get(skill_name, {}).values())

def has_skill(character, skill_name: str) -> bool:
    return get_total_skill_levels(character, skill_name) > 0

def rebuild_skill_level_summary(character) -> dict[str, int]:
    summary = {}

    for skill_name, source_map in character.skill_sources.items():
        total = sum(source_map.values())
        if total > 0:
            summary[skill_name] = total

    return summary
