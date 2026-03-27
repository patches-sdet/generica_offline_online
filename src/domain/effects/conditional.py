from domain.effects.base import Effect


class ConditionalEffect(Effect):
    def __init__(self, effect, condition):
        self.effect = effect
        self.condition = condition

    def apply(self, context):
        for target in context.targets:
            if self.condition(context, target):
                self.effect.apply(
                    type(context)(source=context.source, targets=[target])
                )


class CompositeEffect(Effect):
    def __init__(self, effects):
        self.effects = effects

    def apply(self, context):
        for effect in self.effects:
            effect.apply(context)
