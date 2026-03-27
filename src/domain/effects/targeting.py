from domain.effects.base import Effect


class TargetFilterEffect(Effect):
    def __init__(self, effect, condition):
        self.effect = effect
        self.condition = condition

    def apply(self, context):
        filtered = [t for t in context.targets if self.condition(context, t)]
        if filtered:
            self.effect.apply(
                type(context)(source=context.source, targets=filtered)
            )
