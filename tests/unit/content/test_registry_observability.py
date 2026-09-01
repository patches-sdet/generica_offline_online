import logging

from domain.content_registry import initialize_content_registries


def test_initialize_content_registries_emits_structured_traces(clean_registries, caplog):
    caplog.set_level(logging.INFO)

    initialize_content_registries(force=True)

    start_record = next(
        record for record in caplog.records if record.event_name == "content.initialize.start"
    )
    complete_record = next(
        record for record in caplog.records if record.event_name == "content.initialize.complete"
    )

    assert start_record.inputs == {"force": True}
    assert start_record.outputs == {}
    assert start_record.failure_state is None

    assert complete_record.inputs == {"force": True}
    assert complete_record.failure_state is None
    assert complete_record.outputs["ability_modules_loaded"] >= 0
    assert complete_record.outputs["ability_count"] > 0
    assert complete_record.outputs["base_race_count"] > 0
