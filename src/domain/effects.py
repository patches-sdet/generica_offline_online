from typing import Dict

class Effect:
    """
    Base class for all effects.

    All effects MUST:
    - implement apply(character, source=None)
    - never mutate state outside Character APIs
    - conditionally apply to the correct objects
    """

    priority = 0  # future: ordering system

    def applies_to(self, character) -> bool:
        return True

    def apply(self, character, source: str | None = None):
        if not self.applies_to(character):
            return
        self._apply(character, source)

    def _apply(self, character, source:str | None = None):
        raise NotImplementedError()

    def to_dict(self):
        raise NotImplementedError()

# ATTRIBUTE EFFECTS

class StatIncrease(Effect):
    """
    Increase a single attribute.
    """

    def __init__(self, stat: str, amount: int):
        self.stat = stat
        self.amount = amount

    def _apply(self, character, source: str | None = None):
        if not self.applies_to(character):
            return
        if not hasattr(character.attributes, self.stat):
            raise ValueError(f"Invalid attribute: {self.stat}")

        character.add_attribute(self.stat, self.amount, source)

    def to_dict(self):
        return {
            "type": "stat_increase",
            "stat": self.stat,
            "amount": self.amount,
        }


class MultiStatIncrease(Effect):
    """
    Increase multiple attributes at once.
    Replaces repetitive StatIncrease calls.
    """

    def __init__(self, stats: Dict[str, int]):
        self.stats = stats

    def _apply(self, character, source: str | None = None):
        for stat, amount in self.stats.items():
            if not hasattr(character.attributes, stat):
                raise ValueError(f"Invalid attribute: {stat}")

            character.add_attribute(stat, amount, source)

    def to_dict(self):
        return {
            "type": "multi_stat_increase",
            "stats": self.stats,
        }

class ConditionalEffect(Effect):
    def __init__(self, effect: Effect, condition):
        self.effect = effect
        self.condition = condition


    def applies_to(self, character):
        return self.condition(character)

    def _apply(self, character, source=None):
        self.effect.apply(character, source)

# DERIVED STAT EFFECTS

class DerivedStatBonus(Effect):
    """
    Adds to derived stats (hp, armor, etc.)
    """

    VALID_STATS = {
        "hp", "sanity", "stamina", "moxie", "fortune",
        "armor", "mental_fortitude", "endurance", "cool", "fate"
    }

    def __init__(self, stat: str, amount: int):
        if stat not in self.VALID_STATS:
            raise ValueError(f"Invalid derived stat: {stat}")

        self.stat = stat
        self.amount = amount

    def _apply(self, character, source: str | None = None):
        character._derived_bonuses[self.stat] = (
            character._derived_bonuses.get(self.stat, 0) + self.amount
        )

        # Optional future tracking hook
        if hasattr(character, "_derived_sources"):
            character._derived_sources[self.stat][source] += self.amount

    def to_dict(self):
        return {
            "type": "derived_stat_bonus",
            "stat": self.stat,
            "amount": self.amount,
        }


class DerivedStatOverride(Effect):
    """
    Overrides a derived stat completely.
    """

    def __init__(self, stat: str, amount: int):
        self.stat = stat
        self.amount = amount
        self.priority = 100  # overrides should run last

    def _apply(self, character, source: str | None = None):
        if character._derived_overrides is None:
            character._derived_overrides = {}

        character._derived_overrides[self.stat] = self.amount

    def to_dict(self):
        return {
            "type": "derived_stat_override",
            "stat": self.stat,
            "amount": self.amount,
        }

# HELPERS

def make_effects(**mods):
    """
    Convenience helper for simple stat increases.
    Example:
        make_effects(strength=2, agility=1)
    """
    return [StatIncrease(stat, amount) for stat, amount in mods.items()]
