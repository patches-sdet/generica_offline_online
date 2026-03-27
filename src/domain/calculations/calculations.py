import copy
from collections import defaultdict

from domain.effects.base import EffectContext
from domain.abilities.registry import get_all_abilities
from domain.attributes import Attributes


def recalculate(character):
    """
    Deterministically rebuilds full character state from:
    attributes, race, jobs, professions, abilities.
    """

    # =========================================================
    # RESET STATE
    # =========================================================

    # Fresh attributes (with defaults)
    character.attributes = Attributes()

    # Reset tracking
    character._attribute_sources = defaultdict(lambda: defaultdict(int))
    character._derived_bonuses = defaultdict(int)
    character._derived_overrides = {}

    character.skills = defaultdict(int)

    # Reset runtime systems (CRITICAL)
    character.states.clear()
    character.tags.clear()
    character.event_listeners.clear()

    character.next_attack_modifiers.clear()
    character.extra_attacks = 0
    character.bonus_damage = 0
    character.damage_conversion = None

    # =========================================================
    # ATTRIBUTE EFFECTS (ROLLS)
    # =========================================================

    context = EffectContext(source="attributes", targets=[character])

    for effect in character.attribute_effects:
        effect.apply(context)

    # Snapshot AFTER rolls
    character._base_attributes = copy.deepcopy(character.attributes.to_dict())

    # =========================================================
    # RACE EFFECTS
    # =========================================================

    race_level = character.get_race_level()

    context = EffectContext(source="race", targets=[character])

    # On acquire
    for effect in getattr(character.race, "effects_on_acquire", []):
        effect.apply(context)

    # Per level
    for _ in range(race_level):
        for effect in getattr(character.race, "effects_per_level", []):
            effect.apply(context)

    character.tags.update(character.race.tags)

    # =========================================================
    # ADVENTURE JOB EFFECTS
    # =========================================================

    for job in character.adventure_jobs:
        level = character.adventure_levels.get(job.name, 1)

        context = EffectContext(
            source=f"job:{job.name}",
            targets=[character]
        )

        for _ in range(level):
            for effect in getattr(job, "effects_per_level", []):
                effect.apply(context)

    character.tags.update(job.tags)

    # =========================================================
    # PROFESSION EFFECTS
    # =========================================================

    for job in character.profession_jobs:
        level = character.profession_levels.get(job.name, 1)

        context = EffectContext(
            source=f"profession:{job.name}",
            targets=[character]
        )

        for _ in range(level):
            for effect in getattr(job, "effects_per_level", []):
                effect.apply(context)
    
    if not hasattr(character, "crafting_tags"):
        character.crafting_tags = set()
        character.gathering_tags = set()
        character.economic_tags = set()

    character.crafting_tags.update(job.crafting_tags)
    character.gathering_tags.update(job.gathering_tags)
    character.economic_tags.update(job.economic_tags)


    # =========================================================
    # ABILITY UNLOCK
    # =========================================================

    all_abilities = get_all_abilities()

    character.abilities = [
        ability for ability in all_abilities
        if ability.unlock_condition(character)
    ]

    # Ensure levels exist
    for ability in character.abilities:
        character.ability_levels.setdefault(ability.name, 1)

    # =========================================================
    # SKILL DERIVATION
    # =========================================================

    for ability in character.abilities:
        if ability.is_skill:
            level = character.ability_levels.get(ability.name, 1)
            character.skills[ability.name] += level

    # =========================================================
    # PASSIVE ABILITY EFFECTS
    # =========================================================

    passive_effects = []

    for ability in character.abilities:
        if not ability.is_passive:
            continue

        if not ability.effect_generator:
            continue

        effects = ability.effect_generator(character) or []

        for effect in effects:
            passive_effects.append((effect, ability.name))

    # Optional: priority sorting
    passive_effects.sort(key=lambda pair: getattr(pair[0], "priority", 0))

    for effect, ability_name in passive_effects:
        context = EffectContext(
            source=f"ability:{ability_name}",
            targets=[character]
        )
        effect.apply(context)

    return character
