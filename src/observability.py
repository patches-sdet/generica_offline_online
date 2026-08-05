import json
import logging
from typing import Any


TRACE_RECORD_DEFAULTS = {
    "event_name": None,
    "entity_id": None,
    "ability_id": None,
    "effect_id": None,
    "inputs": {},
    "outputs": {},
    "failure_state": None,
}


class StructuredTraceFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for field_name, default_value in TRACE_RECORD_DEFAULTS.items():
            payload[field_name] = _sanitize(getattr(record, field_name, default_value))

        return json.dumps(payload, sort_keys=True)


def configure_logging(*, force: bool = False) -> None:
    root_logger = logging.getLogger()

    if root_logger.handlers and not force:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(StructuredTraceFormatter())

    logging.basicConfig(level=logging.WARNING, handlers=[handler], force=force)


def _sanitize(value: Any):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value

    if isinstance(value, dict):
        return {str(key): _sanitize(val) for key, val in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_sanitize(item) for item in value]

    return getattr(value, "name", repr(value))


def describe_exception(error: Exception) -> dict[str, str]:
    return {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }


def entity_id(entity: Any) -> str | None:
    if entity is None:
        return None

    return getattr(entity, "name", entity.__class__.__name__)


def effect_id(effect: Any) -> str | None:
    if effect is None:
        return None

    return getattr(effect, "name", effect.__class__.__name__)


def context_snapshot(context) -> dict[str, Any] | None:
    if context is None:
        return None

    return {
        "source": entity_id(getattr(context, "source", None)),
        "targets": [entity_id(target) for target in getattr(context, "targets", [])],
        "metadata": _sanitize(getattr(context, "metadata", {})),
        "spent_amount": getattr(context, "spent_amount", None),
        "chosen_stat": getattr(context, "chosen_stat", None),
    }


def log_trace(
    logger: logging.Logger,
    trace_name: str,
    *,
    entity: Any = None,
    ability: Any = None,
    effect: Any = None,
    inputs: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
    failure_state: dict[str, Any] | None = None,
) -> None:
    payload = {
        "event_name": trace_name,
        "entity_id": entity_id(entity),
        "ability_id": entity_id(ability),
        "effect_id": effect_id(effect),
        "inputs": _sanitize(inputs or {}),
        "outputs": _sanitize(outputs or {}),
        "failure_state": _sanitize(failure_state),
    }

    level = logging.ERROR if failure_state else logging.INFO
    logger.log(level, trace_name, extra=payload)
