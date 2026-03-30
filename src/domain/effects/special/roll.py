from dataclasses import dataclass
from domain.effects.base import Effect, EffectContext
from typing import Optional


@dataclass
class RollModifierEffect(Effect):
    scale_fn: callable
    source_tag: str = "generic"

    def apply(self, context: EffectContext):
        for target in context.targets:
            amount = self.scale_fn(context.source)

            if not hasattr(target, "roll_modifiers"):
                target.roll_modifiers = []

            target.roll_modifiers.append({
                "amount": amount,
                "source": context.source,
                "tag": self.source_tag,
            })