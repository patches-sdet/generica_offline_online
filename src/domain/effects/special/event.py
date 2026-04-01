from dataclasses import dataclass
from typing import Callable
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class EventListenerEffect(Effect):
    event_name: str
    effect: Effect
    condition: Callable | None = None

    def apply(self, context: EffectContext) -> None:
        context.source.event_listeners.append(self)

    def matches(self, event_name: str) -> bool:
        return self.event_name == event_name

    def trigger(self, context: EffectContext, target=None) -> None:
        if self.condition and not self.condition(context, target):
            return
        self.effect.apply(context if target is None else context.with_targets([target]))