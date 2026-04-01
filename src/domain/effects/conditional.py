from dataclasses import dataclass
from typing import Callable
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class ConditionalEffect(Effect):
    effect: Effect
    condition: Callable

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            if self.condition(context, target):
                self.effect.apply(context.with_targets([target]))

@dataclass(slots=True)
class CompositeEffect(Effect):
    effects: list[Effect]

    def apply(self, context: EffectContext) -> None:
        for effect in self.effects:
            if effect is None:
                continue
            effect.apply(context)