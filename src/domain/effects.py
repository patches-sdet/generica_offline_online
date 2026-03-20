class Effect:
    def apply(self, character):
        raise NotImplementedError()

    def to_dict(self):
        raise NotImplementedError()

class StatIncrease(Effect):
    def __init__(self, stat: str, amount: int):
        self.stat = stat
        self.amount = amount

    def apply(self, character):
        if not hasattr(character.attributes, self.stat):
            raise ValueError(f"Invalid attribute: {self.stat}")

        current = getattr(character.attributes, self.stat)
        setattr(character.attributes, self.stat, current + self.amount)

    def to_dict(self):
        return {
                "type": "stat_increase",
                "stat": self.stat,
                "amount": self.amount,
                }

class DerivedStatBonus(Effect):
    """
    Applies bonuses to derived stats (armor, endurance, etc.)
    These are collected during effect application and used in calculations.
    """

    VALID_DERIVED_STATS = {
    "hp", "sanity", "stamina", "moxie", "fortune",
    "armor", "mental_fortitude", "endurance", "cool", "fate"
}

    def __init__(self, stat: str, amount: int):
        self.stat = stat
        self.amount = amount

    def apply(self, character):
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

    def apply(self, character):
        if not hasattr(character, "_derived_overrides") or character._derived_overrides is None:
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
