from domain.effects.aggregation import collect_effects
from .attributes import rebuild_attributes
from .derived import apply_derived_effects, reset_derived
from .pools import calculate_pools
from .defenses import calculate_defenses
from .abilities import rebuild_abilities
from .skills import rebuild_skills
from .tags import rebuild_tags

def reset_runtime_state(character):
    character.event_listeners = []
    character.roll_modifiers = []
    character.next_attack_modifiers = []
    character.extra_attacks = 0
    character.bonus_damage = 0
    character.damage_conversion = None

def recalculate(character):
    """
    Full deterministic rebuild pipeline.
    """

    # RESET STATE
    reset_derived(character)
    reset_runtime_state(character)
    rebuild_abilities(character)
    rebuild_skills(character)
    effects = collect_effects(character)  
    rebuild_attributes(character, effects)
    apply_derived_effects(character, effects)
    calculate_pools(character)
    calculate_defenses(character)
    rebuild_tags(character, effects)

    return character
