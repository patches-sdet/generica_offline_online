from dataclasses import dataclass
from .base import Effect, EffectContext

@dataclass(slots=True)
class ResourceEffect(Effect):
    pool: str
    amount: int

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            target.modify_resource(self.pool, self.amount)

    def to_dict(self) -> dict:
        return {
            "type": "ResourceEffect",
            "pool": self.pool,
            "amount": self.amount,
        }

@dataclass(slots=True)
class Heal(ResourceEffect):
    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Heal amount must be positive")

    def to_dict(self) -> dict:
        return {
            "type": "Heal",
            "pool": self.pool,
            "amount": self.amount,
        }

@dataclass(slots=True)
class Damage(ResourceEffect):
    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Damage amount must be positive")

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            target.modify_resource(self.pool, -self.amount)

    def to_dict(self) -> dict:
        return {
            "type": "Damage",
            "pool": self.pool,
            "amount": self.amount,
        }

@dataclass(slots=True)
class SpendResource(ResourceEffect):
    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Spend amount must be positive")

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            success = target.modify_resource(self.pool, -self.amount)

            if success is False:
                raise ValueError(
                    f"Not enough {self.pool} to spend {self.amount}"
                )

    def to_dict(self) -> dict:
        return {
            "type": "SpendResource",
            "pool": self.pool,
            "amount": self.amount,
        }