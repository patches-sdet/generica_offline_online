from dataclasses import dataclass
from typing import Callable
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class CreateItemEffect(Effect):
    """
    Create one item for the source inventory by default.
    If the effect context indicates a critical success, create two instead.
    The factory function receives:
    - source
    - target (or None if there is no target)
    """
    factory_fn: Callable

    def apply(self, context: EffectContext) -> None:
        target = context.targets[0] if context.targets else None

        item_count = 2 if context.metadata.get("critical_success", False) else 1

        for _ in range(item_count):
            item = self.factory_fn(context.source, target)
            context.source.inventory.append(item)