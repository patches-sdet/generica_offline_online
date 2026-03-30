from dataclasses import dataclass
from .base import Effect, EffectContext

# BASE RESOURCE EFFECT

@dataclass
class ResourceEffect(Effect):
    pool: str
    amount: int

    def apply(self, context: EffectContext):
        for target in context.targets:
            target.modify_resource(self.pool, self.amount)

    def to_dict(self):
        return {
            "type": "ResourceEffect",
            "pool": self.pool,
            "amount": self.amount,
        }

# HEAL (POSITIVE GAIN)

@dataclass
class Heal(ResourceEffect):
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Heal amount must be positive")

    def apply(self, context: EffectContext):
        for target in context.targets:
            target.modify_resource(self.pool, self.amount)

    def to_dict(self):
        return {
            "type": "Heal",
            "pool": self.pool,
            "amount": self.amount,
        }

# DAMAGE (NEGATIVE HP)

@dataclass
class Damage(ResourceEffect):
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Damage amount must be positive")

    def apply(self, context: EffectContext):
        for target in context.targets:
            target.modify_resource(self.pool, -self.amount)

    def to_dict(self):
        return {
            "type": "Damage",
            "pool": self.pool,
            "amount": self.amount,
        }

# SPEND RESOURCE (COST)

@dataclass
class SpendResource(ResourceEffect):
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Spend amount must be positive")

    def apply(self, context: EffectContext):
        for target in context.targets:
            success = target.modify_resource(self.pool, -self.amount)

            if success is False:
                raise ValueError(
                    f"Not enough {self.pool} to spend {self.amount}"
                )

    def to_dict(self):
        return {
            "type": "SpendResource",
            "pool": self.pool,
            "amount": self.amount,
        }
