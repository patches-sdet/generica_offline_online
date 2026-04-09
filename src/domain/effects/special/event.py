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

@dataclass(slots=True)
class GainLevelPointsEffect(Effect):
    amount: int

    def apply(self, context: EffectContext) -> None:
        context.source.gain_grind_points(self.amount)

@dataclass(slots=True)
class ModifyLevelPointAwardEffect(Effect):
    amount: int
    minimum: int = 0

    def apply(self, context: EffectContext) -> None:
        current = getattr(context, "grind_points_awarded", 0)
        context.modify_grind_point_award(max(self.minimum, current + self.amount))

@dataclass(slots=True)
class GainGrindPointsEffect(Effect):
    amount: int

    def apply(self, context: EffectContext) -> None:
        context.source.gain_grind_points(self.amount)

@dataclass(slots=True)
class ModifyGrindPointAwardEffect(Effect):
    amount: int
    minimum: int = 0

    def apply(self, context: EffectContext) -> None:
        current = getattr(context, "grind_points_awarded", 0)
        context.modify_grind_point_award(max(self.minimum, current + self.amount))

@dataclass(slots=True)
class SpendGrindPointEffect(Effect):
    amount: int
    minimum: int = 1

    def apply(self, context: EffectContext) -> None:
        current = getattr(context, "grind_points_cost", 0)
        context.modify_grind_point_cost(max(self.minimum, current + self.amount))