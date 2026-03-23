from collections import defaultdict
from domain.character import Character
from domain.attributes import Pools, Defenses, Attributes


# Derived stat helpers

def get_derived_bonus(character: Character, stat: str) -> int:
    return character._derived_bonuses.get(stat, 0)


def get_derived_override(character: Character, stat: str):
    return character._derived_overrides.get(stat)

def _apply_derived(character: Character, stat: str, base_value: int) -> int:
    """
    Apply bonus + override (override takes precedence, even if 0).
    """
    value = base_value + get_derived_bonus(character, stat)
    override = get_derived_override(character, stat)

    return override if override is not None else value

# Buff source tracking

def add_derived_source(character: Character, stat: str, value: int, source: str | None):
    """
    Future-proof hook for tracking derived stat sources.
    Safe to leave unused until you wire full support.
    """
    if not source:
        return

    if not hasattr(character, "_derived_sources") or character._derived_sources is None:
        character._derived_sources = defaultdict(lambda: defaultdict(int))

    character._derived_sources[stat][source] += value

# POOLS

def calculate_pools(character: Character) -> Pools:
    """
    Calculate max resource pools from attributes + derived bonuses.
    Returns Pools with (current, max), clamped to valid ranges.
    """

    attrs = character.attributes

    # Baseline Pools

    base_values = {
            "hp": attrs.strength + attrs.constitution,
            "sanity": attrs.intelligence + attrs.wisdom,
            "stamina": attrs.dexterity + attrs.agility,
            "moxie": attrs.charisma + attrs.willpower,
            "fortune": attrs.perception + attrs.luck,
            }
    
    final_values = {
            stat: _apply_derived(character, stat, base)
            for stat, base in base_values.items()
            }

    """
    Stop values from going into the negatives (need to refactor
    so that going below 0 results in condtions.
    """
    clamped = {}
    for stat, max_val in final_values.items():
        current_attr = f"current_{stat}"
        current = getattr(character, current_attr)
        clamped[stat] = max(0, min(current, max_val))

    return Pools(
        hp=(clamped["hp"], final_values["hp"]),
        sanity=(clamped["sanity"], final_values["sanity"]),
        stamina=(clamped["stamina"], final_values["stamina"]),
        moxie=(clamped["moxie"], final_values["moxie"]),
        fortune=(clamped["fortune"],final_values["fortune"]),
    )

# DEFENSES

def calculate_defenses(character: Character) -> Defenses:
    """
    Calculate defensive stats from attributes + derived bonuses.
    """
    attrs = character.attributes

    base_values = {
        "armor": 0,
        "mental_fortitude": 0,
        "endurance": 0,
        "cool": 0,
        "fate": 0,
    }

    final_values = {
        stat: _apply_derived(character, stat, base)
        for stat, base in base_values.items()
}

    return Defenses(**final_values)

# Recalculation to keep state clean

def recalculate(character: Character):
    """
    Fully rebuilds character state deterministically from:
    race, jobs, profession, abilities.
    """

    # -------------------------
    # RESET STATE
    # -------------------------

    character.attributes = character.race.get_base_attributes(character.race_level)

    # Snapshot base attributes
    character._base_attributes = vars(character.attributes).copy()

    # Reset tracking
    character._attribute_sources.clear()
    character._derived_bonuses.clear()
    character._derived_overrides.clear()

    # -------------------------
    # APPLY RACE EFFECTS
    # -------------------------

    for effect in character.race.get_effects(character.race_level):
        effect.apply(character, source="race")

    # -------------------------
    # APPLY ADVENTURE JOB EFFECTS
    # -------------------------

    for effect in character.adventure_job.get_effects(character.adventure_level):
        effect.apply(character, source=f"job:{character.adventure_job.name}")

    # -------------------------
    # APPLY PROFESSION EFFECTS
    # -------------------------

    if character.profession_job:
        for effect in character.profession_job.get_effects(character.profession_level):
            effect.apply(character, source=f"profession:{character.profession_job.name}")

    # -------------------------
    # ABILITY UNLOCK
    # -------------------------

    from domain.abilities import ALL_ABILITIES

    character.abilities = [
        ability for ability in ALL_ABILITIES
        if ability.unlock_condition(character)
    ]

    for ability in character.abilities:
        character.ability_levels.setdefault(ability.name, 1)

    # -------------------------
    # APPLY ABILITY EFFECTS
    # -------------------------

    ability_effects = []

    for ability in character.abilities:
        for effect in ability.get_effects(character):
            ability_effects.append((effect, ability.name))

    # Optional priority system
    ability_effects.sort(key=lambda pair: getattr(pair[0], "priority", 0))

    for effect, ability_name in ability_effects:
        effect.apply(character, source=f"ability:{ability_name}")

    return character
