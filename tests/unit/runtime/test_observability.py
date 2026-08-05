import logging
from io import StringIO
import json
from types import SimpleNamespace

import pytest

from application.events import emit_event
from application.runtime import execute_ability
from domain.abilities.factory import make_ability
from domain.character import Character
from domain.content_registry import initialize_content_registries, register_ability
from domain.effects.base import Effect, EffectContext
from observability import configure_logging


class BoomEffect(Effect):
    def apply(self, context: EffectContext):
        raise RuntimeError("boom")


def test_execute_ability_emits_consistent_structured_traces(clean_registries, caplog):
    caplog.set_level(logging.INFO)
    initialize_content_registries(force=True)

    character = Character(name="Observability Runtime Test")
    character.current_sanity = 50
    character.max_sanity = 50

    ability = make_ability(
        name="Observed Runtime Ability",
        unlock_condition=lambda _: True,
        execute=lambda caster, targets: [],
        cost=5,
        cost_pool="sanity",
        is_skill=True,
        auto_register=False,
    )
    register_ability(ability)

    execute_ability(character, "Observed Runtime Ability", explicit_targets=[character])

    start_record = next(
        record for record in caplog.records if record.event_name == "runtime.execute_ability.start"
    )
    complete_record = next(
        record for record in caplog.records if record.event_name == "runtime.execute_ability.complete"
    )
    apply_record = next(
        record for record in caplog.records if record.event_name == "runtime.apply_effects.complete"
    )
    emit_start_record = next(
        record
        for record in caplog.records
        if record.event_name == "events.emit.start"
        and record.inputs["emitted_event"] == "ability_started"
    )

    assert start_record.entity_id == "Observability Runtime Test"
    assert start_record.ability_id is None
    assert start_record.failure_state is None
    assert start_record.inputs["ability_name"] == "Observed Runtime Ability"

    assert complete_record.entity_id == "Observability Runtime Test"
    assert complete_record.ability_id == "Observed Runtime Ability"
    assert complete_record.outputs["effect_count"] == 1
    assert complete_record.failure_state is None

    assert apply_record.outputs["effect_count"] == 1
    assert emit_start_record.inputs["emitted_event"] == "ability_started"
    assert emit_start_record.failure_state is None


def test_execute_ability_logs_failure_trace_for_effect_errors(clean_registries, caplog):
    caplog.set_level(logging.INFO)
    initialize_content_registries(force=True)

    character = Character(name="Observed Failure Runtime Test")

    ability = make_ability(
        name="Observed Failing Ability",
        unlock_condition=lambda _: True,
        execute=lambda caster, targets: [BoomEffect()],
        is_skill=True,
        auto_register=False,
    )
    register_ability(ability)

    with pytest.raises(RuntimeError, match="boom"):
        execute_ability(character, "Observed Failing Ability", explicit_targets=[character])

    apply_failed_record = next(
        record for record in caplog.records if record.event_name == "runtime.apply_effects.failed"
    )
    ability_failed_record = next(
        record for record in caplog.records if record.event_name == "runtime.execute_ability.failed"
    )

    assert apply_failed_record.effect_id == "BoomEffect"
    assert apply_failed_record.failure_state["error_type"] == "RuntimeError"
    assert ability_failed_record.ability_id == "Observed Failing Ability"
    assert ability_failed_record.failure_state["error_message"] == "boom"


def test_emit_event_logs_failure_trace_when_listener_effect_raises(monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    monkeypatch.setattr(
        "application.events._LISTENERS",
        [SimpleNamespace(event_name="observed_event", condition=None, effect=BoomEffect())],
    )
    context = EffectContext(source=Character(name="Event Trace Test"), targets=[])

    with pytest.raises(RuntimeError, match="boom"):
        emit_event("observed_event", context)

    failed_record = next(
        record for record in caplog.records if record.event_name == "events.emit.failed"
    )

    assert failed_record.entity_id == "Event Trace Test"
    assert failed_record.inputs["emitted_event"] == "observed_event"
    assert failed_record.failure_state["error_type"] == "RuntimeError"


def test_configured_logging_emits_stable_structured_trace_shape(monkeypatch):
    stream = StringIO()
    logger = logging.getLogger("tests.observability")
    logger.setLevel(logging.INFO)

    monkeypatch.setattr("sys.stderr", stream)

    configure_logging(force=True)

    logger.info(
        "runtime.execute_ability.complete",
        extra={
            "event_name": "runtime.execute_ability.complete",
            "entity_id": "Observed Runtime Test",
            "ability_id": "Observed Ability",
            "inputs": {"ability_name": "Observed Ability"},
            "outputs": {"effect_count": 1},
        },
    )

    emitted = json.loads(stream.getvalue().strip())

    assert emitted["level"] == "INFO"
    assert emitted["logger"] == "tests.observability"
    assert emitted["message"] == "runtime.execute_ability.complete"
    assert emitted["event_name"] == "runtime.execute_ability.complete"
    assert emitted["entity_id"] == "Observed Runtime Test"
    assert emitted["ability_id"] == "Observed Ability"
    assert emitted["effect_id"] is None
    assert emitted["inputs"] == {"ability_name": "Observed Ability"}
    assert emitted["outputs"] == {"effect_count": 1}
    assert emitted["failure_state"] is None
    assert emitted["timestamp"]


def test_configured_logging_keeps_default_shape_for_non_trace_records(monkeypatch):
    stream = StringIO()
    logger = logging.getLogger("tests.observability.defaults")
    logger.setLevel(logging.WARNING)

    monkeypatch.setattr("sys.stderr", stream)

    configure_logging(force=True)

    logger.warning("plain warning")

    emitted = json.loads(stream.getvalue().strip())

    assert emitted["level"] == "WARNING"
    assert emitted["message"] == "plain warning"
    assert emitted["event_name"] is None
    assert emitted["entity_id"] is None
    assert emitted["ability_id"] is None
    assert emitted["effect_id"] is None
    assert emitted["inputs"] == {}
    assert emitted["outputs"] == {}
    assert emitted["failure_state"] is None
