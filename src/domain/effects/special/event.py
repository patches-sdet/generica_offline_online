from domain.effects.base import Effect


class EventListenerEffect(Effect):
    def __init__(self, event_name, effect, condition=None):
        self.event_name = event_name
        self.effect = effect
        self.condition = condition

    def apply(self, context):
        context.source.event_listeners.append(self)
