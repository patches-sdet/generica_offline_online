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

@dataclass(slots=True)
class InspectEffect(Effect):
    reveal_fn: Callable[[EffectContext, object], dict]

    def apply(self, context: EffectContext) -> None:
        target = context.targets[0] if context.targets else None
        info = self.reveal_fn(context, target)
        context.source.receive_inspection_info(info)
        return info