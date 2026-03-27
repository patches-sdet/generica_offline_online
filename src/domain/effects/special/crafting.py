from domain.effects.base import Effect


class CreateItemEffect(Effect):
    def __init__(self, factory_fn):
        self.factory_fn = factory_fn

    def apply(self, context):
        for target in context.targets:
            item = self.factory_fn(context.source, target)
            context.source.inventory.append(item)
