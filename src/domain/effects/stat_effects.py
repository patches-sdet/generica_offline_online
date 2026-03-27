from domain.effects.base import Effect, EffectContext
from domain.attributes import DEFENSE_KEYS

class StatIncrease(Effect):
    def __init__(self, stat: str, amount: int):
        self.stat = stat
        self.amount = amount

    def apply(self, context):
        for target in context.targets:
            target.add_stat(self.stat, self.amount)


class MultiStatIncrease(Effect):
    def __init__(self, stats: dict, scale: int = 1):
        self.stats = stats
        self.scale = scale

    def apply(self, context):
        for target in context.targets:
            for stat, value in self.stats.items():
                target.add_stat(stat, value * self.scale)

class DerivedStatBonus(Effect):
    stat = str
    amount = int
    priority = int = 0

    def apply(self, context: EffectContext):
        if self.stat not in DEFENSE_KEYS:
            raise ValueError(f"Invalid derived stat: {self.stat}")

        for target in context.targets:
            target._derived_bonuses[self.stat] += self.amount

    def to_dict(self):
        return {
            "type": "DerivedStatBonus",
            "stat": self.stat,
            "amount": self.amount,
        }

class DerivedStatOverride(Effect):
    stat = str
    value = int
    priority = int = 100  # overrides should apply AFTER bonuses

    def apply(self, context: EffectContext):
        if self.stat not in DEFENSE_KEYS:
            raise ValueError(f"Invalid derived stat: {self.stat}")

        for target in context.targets:
            target._derived_overrides[self.stat] = self.value

    def to_dict(self):
        return {
            "type": "DerivedStatOverride",
            "stat": self.stat,
            "value": self.value,
        }        
