from dataclasses import dataclass
from typing import Callable
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class TargetFilterEffect(Effect):
    effect: Effect
    condition: Callable

    def apply(self, context: EffectContext) -> None:
        filtered = [target for target in context.targets if self.condition(context, target)]

        if filtered:
            self.effect.apply(context.with_targets(filtered))