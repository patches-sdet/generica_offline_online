import logging
from types import SimpleNamespace

import pytest

from domain.effects.aggregation import collect_effects


def test_collect_effects_logs_failure_state_for_bad_passive_output(caplog):
    caplog.set_level(logging.INFO)
    character = SimpleNamespace(
        name="Broken Passive Character",
        progressions={},
        abilities=[
            SimpleNamespace(
                name="Broken Passive",
                is_passive=True,
                effect_generator=lambda _: "invalid",
            )
        ],
        equipment=[],
        inventory=[],
        active_effects=[],
    )

    with pytest.raises(TypeError):
        collect_effects(character)

    failed_record = next(
        record for record in caplog.records if record.event_name == "effects.collect.failed"
    )

    assert failed_record.entity_id == "Broken Passive Character"
    assert failed_record.inputs["current_source"] == "passive ability Broken Passive"
    assert failed_record.outputs["effect_count"] == 0
    assert failed_record.failure_state["error_type"] == "TypeError"
