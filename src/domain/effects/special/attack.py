from dataclasses import dataclass
from typing import Callable
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class ModifyNextAttackEffect(Effect):
    modifier_fn: Callable[[EffectContext, object], None]

    def apply(self, context: EffectContext) -> None:
        context.source.next_attack_modifiers.append(self.modifier_fn)