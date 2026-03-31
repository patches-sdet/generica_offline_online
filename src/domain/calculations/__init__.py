from domain.effects.aggregation import collect_effects
from .attributes import rebuild_attributes
from .derived import apply_derived_effects, reset_derived
from .pools import calculate_pools
from .defenses import calculate_defenses
from .abilities import rebuild_abilities
from .skills import rebuild_skills
from .tags import rebuild_tags

def recalculate(character):
    """
    Full deterministic rebuild pipeline.
    """

    if character._base_attributes is None:
        raise ValueError(f"{character.name} has no base attributes initialized")

    # RESET STATE

    reset_derived(character)
    character.roll_modifiers.clear()
    character.next_attack_modifiers.clear()
    character.extra_attacks = 0
    character.bonus_damage = 0
    character.damage_conversion = None
    character.skills.clear()
    rebuild_abilities(character)
    rebuild_skills(character)

    # Rebuild Character
    effects = collect_effects(character)  
    rebuild_attributes(character, effects)
    calculate_pools(character)
    calculate_defenses(character)
    apply_derived_effects(character, effects)
    rebuild_tags(character, effects)

    return character
