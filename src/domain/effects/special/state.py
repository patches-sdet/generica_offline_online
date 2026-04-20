from dataclasses import dataclass
from typing import Callable
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class ApplyStateEffect(Effect):
    state_name: str
    value_fn: Callable | None = None
    aura_id: Callable | None = None

    def apply(self, context: EffectContext) -> None:
        value = self.value_fn(context.source) if self.value_fn else True
        context.source.states[self.state_name] = value