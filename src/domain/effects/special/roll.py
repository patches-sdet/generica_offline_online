from dataclasses import dataclass
from typing import Callable
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class RollModifierEffect(Effect):
    scale_fn: Callable
    source_tag: str = "generic"
    condition: Callable | None = None

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            if self.condition and not self.condition(context, target):
                continue

            amount = int(self.scale_fn(context.source))

            if not hasattr(target, "roll_modifiers"):
                target.roll_modifiers = []

            target.roll_modifiers.append({
                "amount": amount,
                "source": context.source,
                "tag": self.source_tag,
            })