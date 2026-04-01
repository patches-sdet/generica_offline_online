from typing import List, TYPE_CHECKING
from domain.effects.base import Effect

if TYPE_CHECKING:
    from domain.character import Character

def collect_effects(character: "Character") -> List[Effect]:
    """
    Centralized effect aggregation.

    This is updated to a progression-based system:
    - Removed legacy *level usages
    - Removed legacy paramters specific to jobs
    - Centralizing truth to Character.progressions
    """
    effects: List[Effect] = []

    for (ptype, name), progression in character.progressions.items():
        level = progression.level

        source = get_progression_source(ptype, name)
        if not source:
            continue

        if level >= 1 and hasattr(source, "effects_on_acquire"):
            effects.extend(source.effects_on_acquire)

        if hasattr(source, "get_effects"):
            effects.extend(source.get_effects(level))

    # --- Passive Abilities ---
    for ability in character.abilities:
            if ability.is_passive and ability.effect_generator:
                result = ability.effect_generator(character)
                
                if isinstance(result, list):
                    effects.extend(result)
                elif result:
                    raise TypeError(
                        f"{ability.name} returned non-list effect result: {type(result)}"
                    )

    # --- Future Equipment Implementation---
    for item in getattr(character, "equipment", []):
        if hasattr(item, "get_effects"):
            effects.extend(item.get_effects())

    # --- Active Effects ---
    for effect in getattr(character, "active_effects", []):
        effects.append(effect)

    return effects