from collections import defaultdict
from typing import Optional

from domain.effects.stat_effects import DerivedStatBonus, DerivedStatOverride


def reset_derived(character) -> None:
    character._derived_bonuses = defaultdict(int)
    character._derived_overrides = {}


def get_derived_bonus(character, stat: str) -> int:
    return character._derived_bonuses.get(stat, 0)


def get_derived_override(character, stat: str) -> Optional[int]:
    return character._derived_overrides.get(stat)


def apply_derived_effects(character, effects: list) -> None:
    for effect in effects:
        if isinstance(effect, DerivedStatBonus):
            character._derived_bonuses[effect.stat] += effect.amount

        elif isinstance(effect, DerivedStatOverride):
            character._derived_overrides[effect.stat] = effect.value