from collections import defaultdict


def reset_derived(character):
    character._derived_bonuses = defaultdict(int)
    character._derived_overrides = {}


def get_derived_bonus(character, stat: str) -> int:
    return character._derived_bonuses.get(stat, 0)


def get_derived_override(character, stat: str):
    return character._derived_overrides.get(stat)
