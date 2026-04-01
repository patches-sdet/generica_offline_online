from dataclasses import dataclass
from domain.effects.base import Effect, EffectContext

@dataclass(slots=True)
class ApplyTagEffect(Effect):
    tag: str

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            if not hasattr(target, "tags"):
                target.tags = set()
            target.tags.add(self.tag)