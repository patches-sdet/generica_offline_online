from domain.effects.base import Effect


class ModifyNextAttackEffect(Effect):
    def __init__(self, modifier_fn):
        self.modifier_fn = modifier_fn

    def apply(self, context):
        context.source.next_attack_modifiers.append(self.modifier_fn)
