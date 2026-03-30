from typing import List, TYPE_CHECKING
from domain.effects.base import Effect, EffectContext

if TYPE_CHECKING:
    from domain.character import Character

def collect_effects(character: "Character") -> List[Effect]:
    """
    Centralized effect aggregation.

    This is the ONLY place that knows where effects come from.
    """
    effects: List[Effect] = []

    # --- Race Effects ---
    if character.race:
        race = character.race
        level = character.get_race_levels()

        effects.extend(race.effects_on_acquire)
        effects.extend(race.get_effects(level))

        # Handle base race inheritance if applicable
        if race.base_race:
            base = race.base_race
            base_level = character.base_race_levels.get(base.name, level)
            effects.extend(base.effects_on_acquire)
            effects.extend(base.get_effects(level))

    # --- Adventure Jobs ---
    for job in character.adventure_jobs:
        level = character.adventure_levels.get(job.name, 1)
        effects.extend(job.get_effects(level))

    # --- Professions ---
    for profession in character.profession_jobs:
        level = character.profession_levels.get(profession.name, 1)
        effects.extend(profession.get_effects(level))

    # --- Passive Effects ---
    for ability in getattr(character, "abilities", []):
            if ability.is_passive and ability.effect_generator:
                effects.extend(ability.effect_generator(character))

    # --- (Future) Equipment ---
    for item in getattr(character, "equipment", []):
        if hasattr(item, "get_effects"):
            effects.extend(item.get_effects())

    # --- Active Effects ---
    for effect in getattr(character, "active_effects", []):
        effects.append(effect)

    return effects