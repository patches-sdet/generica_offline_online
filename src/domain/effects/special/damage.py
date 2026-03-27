from domain.effects.base import Effect


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
