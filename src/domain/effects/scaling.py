from typing import Callable, Dict
from domain.effects.base import Effect, EffectContext


class ScalingEffect(Effect):
    def __init__(
        self,
        *,
        effect_cls: Callable[[int], Effect],
        scale_fn: Callable[[float], float],
        stats: Dict[str, float],
    ):
        self.effect_cls = effect_cls
        self.scale_fn = scale_fn
        self.stats = stats

    def apply(self, context: EffectContext):
        character = context.character

        total = sum(
            character.get_stat(stat) * weight
            for stat, weight in self.stats.items()
        )

        amount = int(self.scale_fn(total))

        effect = self.effect_factory(amount)
        effect.apply(context)