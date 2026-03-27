from domain.effects.base import Effect


class ApplyTagEffect(Effect):
    def __init__(self, tag: str):
        self.tag = tag

    def apply(self, context):
        for target in context.targets:
            if not hasattr(target, "tags"):
                target.tags = set()
            target.tags.add(self.tag)
