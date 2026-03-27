from domain.effects.base import Effect


class ExtraAttackEffect(Effect):
    def __init__(self, count: int):
        self.count = count

    def apply(self, context):
        context.source.extra_attacks += self.count


class ActionOverrideEffect(Effect):
    def __init__(self, modifier_fn):
        self.modifier_fn = modifier_fn

    def apply(self, context):
        self.modifier_fn(context)
