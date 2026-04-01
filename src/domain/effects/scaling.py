from dataclasses import dataclass, field
from typing import Any, Callable
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class ScalingEffect(Effect):
    effect_cls: type[Effect]
    scale_fn: Callable[[Any], float]
    effect_kwargs: dict[str, Any] = field(default_factory=dict)

    def apply(self, context: EffectContext) -> None:
        """
        Compute a scaled amount from the source/context and instantiate
        the wrapped effect class with that amount plus any extra kwargs.
        """
        amount = int(self.scale_fn(context.source))
        effect = self.effect_cls(amount=amount, **self.effect_kwargs)
        effect.apply(context)