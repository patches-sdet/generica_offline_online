from .attributes import rebuild_attributes
from .derived import reset_derived
from .pools import calculate_pools
from .defenses import calculate_defenses


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

    # -------------------------
    # ATTRIBUTES
    # -------------------------

    rebuild_attributes(character)

    # -------------------------
    # ABILITIES
    # -------------------------

    from domain.abilities import ALL_ABILITIES

    character.abilities = [
        ability for ability in ALL_ABILITIES
        if ability.unlock_condition(character)
    ]

    for ability in character.abilities:
        character.ability_levels.setdefault(ability.name, 1)

    # -------------------------
    # SKILLS
    # -------------------------

    for ability in character.abilities:
        if getattr(ability, "is_skill", False):
            character.skills[ability.name] += character.ability_levels.get(ability.name, 1)

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
