from collections import defaultdict


class Effect:
    def apply(self, character, source=None):
        raise NotImplementedError()

    def to_dict(self):
        raise NotImplementedError()


class StatIncrease(Effect):
    def __init__(self, stat: str, amount: int):
        self.stat = stat
        self.amount = amount

    def apply(self, character, source=None):
        # Safety check (optional but useful)
        if not hasattr(character.attributes, self.stat):
            raise ValueError(f"Invalid attribute: {self.stat}")

        # Single source of truth for mutation
        character.add_attribute(self.stat, self.amount, source)

    def to_dict(self):
        return {
            "type": "stat_increase",
            "stat": self.stat,
            "amount": self.amount,
        }


class DerivedStatBonus(Effect):
    """
    Applies bonuses to derived stats (armor, endurance, etc.)
    """

    VALID_DERIVED_STATS = {
        "hp", "sanity", "stamina", "moxie", "fortune",
        "armor", "mental_fortitude", "endurance", "cool", "fate"
    }

    def __init__(self, stat: str, amount: int):
        self.stat = stat
        self.amount = amount

    def apply(self, character, source=None):  # ✅ updated signature
        if self.stat not in self.VALID_DERIVED_STATS:
            raise ValueError(f"Invalid derived stat: {self.stat}")

        character._derived_bonuses[self.stat] = (
            character._derived_bonuses.get(self.stat, 0) + self.amount
        )

    def to_dict(self):
        return {
            "type": "derived_stat_bonus",
            "stat": self.stat,
            "amount": self.amount,
        }


class DerivedStatOverride(Effect):
    def __init__(self, stat: str, amount: int):
        self.stat = stat
        self.amount = amount

    def apply(self, character, source=None):  # ✅ updated signature
        if character._derived_overrides is None:
            character._derived_overrides = {}

        character._derived_overrides[self.stat] = self.amount

    def to_dict(self):
        return {
            "type": "derived_stat_override",
            "stat": self.stat,
            "amount": self.amount,
        }


def make_effects(**mods):
    return [StatIncrease(stat, amount) for stat, amount in mods.items()]
