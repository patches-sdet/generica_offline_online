import logging

from observability import context_snapshot, describe_exception, log_trace


_LISTENERS = []
LOGGER = logging.getLogger(__name__)


def register_listener(listener):
    _LISTENERS.append(listener)


def emit_event(event_name: str, context, **kwargs):
    matched_listeners = 0
    triggered_listeners = 0

    log_trace(
        LOGGER,
        "events.emit.start",
        entity=getattr(context, "source", None),
        inputs={
            "emitted_event": event_name,
            "listener_count": len(_LISTENERS),
            "context": context_snapshot(context),
            "payload": kwargs,
        },
    )

    try:
        for listener in _LISTENERS:
            if getattr(listener, "event_name", None) == event_name:
                matched_listeners += 1
                if not listener.condition or listener.condition(context, context.source):
                    triggered_listeners += 1
                    listener.effect.apply(context)

        log_trace(
            LOGGER,
            "events.emit.complete",
            entity=getattr(context, "source", None),
            outputs={
                "emitted_event": event_name,
                "matched_listener_count": matched_listeners,
                "triggered_listener_count": triggered_listeners,
            },
        )
    except Exception as error:
        log_trace(
            LOGGER,
            "events.emit.failed",
            entity=getattr(context, "source", None),
            inputs={
                "emitted_event": event_name,
                "context": context_snapshot(context),
                "payload": kwargs,
            },
            outputs={
                "matched_listener_count": matched_listeners,
                "triggered_listener_count": triggered_listeners,
            },
            failure_state=describe_exception(error),
        )
        raise
