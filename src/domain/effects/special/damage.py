from dataclasses import dataclass
from typing import Callable
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class BonusDamageEffect(Effect):
    scale_fn: Callable

    def apply(self, context: EffectContext) -> None:
        bonus = int(self.scale_fn(context.source))
        context.source.bonus_damage += bonus

@dataclass(slots=True)
class ConvertDamageEffect(Effect):
    from_pool: str
    to_pool: str

    def apply(self, context: EffectContext) -> None:
        context.source.damage_conversion = (self.from_pool, self.to_pool)

@dataclass(slots=True)
class TransferEffect(Effect):
    amount_fn: Callable
    condition: Callable | None = None

    def apply(self, context: EffectContext) -> None:
        caster = context.source
        amount = int(self.amount_fn(caster, context))

        for target in context.targets:
            if self.condition and not self.condition(caster, target):
                continue

            target.modify_resource("hp", -amount)
            caster.modify_resource("hp", amount)