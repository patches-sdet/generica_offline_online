from domain.character import Character
from domain.attributes import Pools, Defenses


# ----------------------
# Internal Helpers
# ----------------------

def get_derived_bonus(character: Character, stat: str) -> int:
    """
    Safely retrieve accumulated derived stat bonuses.
    """
    return getattr(character, "_derived_bonuses", {}).get(stat, 0)


# ----------------------
# Pool Calculations
# ----------------------

def calculate_pools(character: Character) -> Pools:
    """
    Calculate max resource pools from attributes + derived bonuses.
    Returns Pools with (current, max), clamped to valid ranges.
    """

    attrs = character.attributes

    # --- Base formulas ---
    hp = attrs.constitution * 2 + attrs.strength
    sanity = attrs.wisdom * 2 + attrs.intelligence
    stamina = attrs.constitution + attrs.agility
    moxie = attrs.charisma * 2 + attrs.willpower
    fortune = attrs.luck * 2

    # --- Apply derived bonuses ---
    hp += get_derived_bonus(character, "hp")
    sanity += get_derived_bonus(character, "sanity")
    stamina += get_derived_bonus(character, "stamina")
    moxie += get_derived_bonus(character, "moxie")
    fortune += get_derived_bonus(character, "fortune")

    # --- Clamp current values ---
    current_hp = max(0, min(character.current_hp, hp))
    current_sanity = max(0, min(character.current_sanity, sanity))
    current_stamina = max(0, min(character.current_stamina, stamina))
    current_moxie = max(0, min(character.current_moxie, moxie))
    current_fortune = max(0, min(character.current_fortune, fortune))

    return Pools(
        hp=(current_hp, hp),
        sanity=(current_sanity, sanity),
        stamina=(current_stamina, stamina),
        moxie=(current_moxie, moxie),
        fortune=(current_fortune, fortune),
    )


# ----------------------
# Defense Calculations
# ----------------------

def calculate_defenses(character) -> Defenses:
    def resolve(stat: str):
        override = character._derived_overrides.get(stat)
        bonus = character._derived_bonuses.get(stat, 0)

        base = override if override is not None else 0
        return base + bonus

    return Defenses(
        armor=resolve("armor"),
        mental_fortitude=resolve("mental_fortitude"),
        endurance=resolve("endurance"),
        cool=resolve("cool"),
        fate=resolve("fate"),
    )

# ----------------------
# Full Recalculation Hook
# ----------------------

def recalculate(character: Character):
    """
    Reapply all effects and recompute derived values.

    Call this after:
    - character creation
    - leveling
    - equipment changes (future)
    """

    # Reset derived bonuses
    character._derived_bonuses = {}
    character._derived_overrides = {}

    # Apply race effects
    for effect in character.race.effects_on_acquire:
        effect.apply(character)

    for _ in range(character.race_level):
        for effect in character.race.effects_per_level:
            effect.apply(character)

    # Apply job effects
    for effect in character.adventure_job.effects_on_acquire:
        effect.apply(character)

    for _ in range(character.adventure_level):
        for effect in character.adventure_job.effects_per_level:
            effect.apply(character)

    # Profession job (if present)
    if character.profession_job:
        for effect in character.profession_job.effects_on_acquire:
            effect.apply(character)

        for _ in range(character.profession_level):
            for effect in character.profession_job.effects_per_level:
                effect.apply(character)
