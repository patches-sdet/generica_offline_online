from domain.effects.base import Effect, EffectContext


class BonusDamageEffect(Effect):
    def __init__(self, scale_fn):
        self.scale_fn = scale_fn

    def apply(self, context):
        bonus = self.scale_fn(context.source)
        context.source.bonus_damage += bonus


class ConvertDamageEffect(Effect):
    def __init__(self, from_pool, to_pool):
        self.from_pool = from_pool
        self.to_pool = to_pool

    def apply(self, context):
        context.source.damage_conversion = (self.from_pool, self.to_pool)

class TransferEffect(Effect):
    def __init__(self, amount_fn, condition=None):
        self.amount_fn = amount_fn
        self.condition = condition

    def apply(self, context: EffectContext):
        caster = context.source
        amount = self.amount_fn(caster, context)

        for target in context.targets:
            if not self.condition or self.condition(caster, target):
                # Damage target
                target.modify_health(-amount)

                # Heal caster
                caster.modify_health(amount)
