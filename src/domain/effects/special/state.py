from domain.effects.base import Effect


class ApplyStateEffect(Effect):
    def __init__(self, state_name: str, value_fn=None):
        self.state_name = state_name
        self.value_fn = value_fn

    def apply(self, context):
        value = self.value_fn(context.source) if self.value_fn else True
        context.source.states[self.state_name] = value
