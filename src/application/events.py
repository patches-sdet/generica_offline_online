_LISTENERS = []


def register_listener(listener):
    _LISTENERS.append(listener)


def emit_event(event_name: str, context, **kwargs):
    for listener in _LISTENERS:
        if getattr(listener, "event_name", None) == event_name:
            if not listener.condition or listener.condition(context, context.source):
                listener.effect.apply(context)
