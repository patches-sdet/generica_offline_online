from .attributes import rebuild_attributes
from .derived import reset_derived
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

    # -------------------------
    # RESET STATE
    # -------------------------

    reset_derived(character)
    character.skills.clear()

    # Rebuild Character
    rebuild_attributes(character)
    calculate_pools(character)
    calculate_defenses(character)
    rebuild_tags(character)
    rebuild_abilities(character)
    rebuild_skills(character)
    reset_derived(character)

    # -------------------------
    # PASSIVES
    # -------------------------

    from domain.effects import EffectContext

    ability_effects = []

    for ability in character.abilities:
        if not getattr(ability, "is_passive", True):
            continue

        for effect in ability.get_effects(character):
            ability_effects.append((effect, ability.name))

    ability_effects.sort(key=lambda pair: getattr(pair[0], "priority", 0))

    for effect, name in ability_effects:
        context = EffectContext(
            source=f"ability:{name}",
            targets=[character],
        )
        effect.apply(context)

    return character
