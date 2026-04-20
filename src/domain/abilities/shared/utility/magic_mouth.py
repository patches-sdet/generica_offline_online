from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state


MAGIC_MOUTH = {
    "name": "Magic Mouth",
    "cost": 20,
    "cost_pool": "sanity",
    "description": (
        "Create a mouth on any visible object. It may be visible or invisible, can speak through the "
        "object at will, or can hold a programmed message that triggers when someone approaches."
    ),
    "duration": "1 Minute per Sensate Level",
    "effects": apply_state(
        "magic_mouth_active",
        value_fn=lambda source: {
            "active": True,
            "duration_minutes": source.get_progression_level("adventure", "Sensate", 0),
            "requires_visible_object": True,
            "mouth_may_be_visible_or_invisible": True,
            "caster_may_speak_through_it_at_will": True,
            "can_store_programmed_message": True,
            "trigger": "when_anyone_draws_near",
            "message_duration": "any_duration",
            "source_ability": "Magic Mouth",
        },
    ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": True,
    "required_level": 1,
    "scales_with_level": False,
    "target": "item",
    "type": "skill",
}

build_shared_ability("shared.utility", MAGIC_MOUTH, source_type="adventure")