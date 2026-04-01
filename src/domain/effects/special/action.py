from dataclasses import dataclass
from typing import Callable
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class ExtraAttackEffect(Effect):
    count: int

    def apply(self, context: EffectContext) -> None:
        context.source.extra_attacks += self.count

@dataclass(slots=True)
class ActionOverrideEffect(Effect):
    modifier_fn: Callable[[EffectContext], None]

    def apply(self, context: EffectContext) -> None:
        self.modifier_fn(context)