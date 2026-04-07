from dataclasses import dataclass
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class StatIncrease(Effect):
    stat: str
    amount: int
    source: str = None

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            target.add_stat(self.stat, self.amount, source=self.source)

@dataclass(slots=True)
class MultiStatIncrease(Effect):
    stats: dict[str, int]
    scale: int = 1
    source: str = None

    def describe(self) -> list[str]:
        return [f"+{v} {k}" for k, v in self.stats.items()]

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            for stat, value in self.stats.items():
                target.add_stat(stat, value * self.scale, source=self.source)

@dataclass(slots=True)
class DerivedStatBonus(Effect):
    stat: str
    amount: int
    source: str = None
    priority: int = 0

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            target._derived_bonuses[self.stat] += self.amount

    def to_dict(self) -> dict:
        return {
            "type": "DerivedStatBonus",
            "stat": self.stat,
            "amount": self.amount,
        }

@dataclass(slots=True)
class DerivedStatOverride(Effect):
    stat: str
    value: int
    source: str = None
    priority: int = 100

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            target._derived_overrides[self.stat] = self.value

    def to_dict(self) -> dict:
        return {
            "type": "DerivedStatOverride",
            "stat": self.stat,
            "value": self.value,
        }