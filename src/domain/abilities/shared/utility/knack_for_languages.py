from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state

KNACK_FOR_LANGUAGES = {
        "name": "Knack for Languages",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Gain a bonus to Intelligence when speaking or reading an unknown language."
        ),
        "duration": "10 Minutes per Explorer Level",
        "effects": apply_state(
            "knack_for_languages_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _explorer_level(source) * 10,
                "intelligence_bonus_for_unknown_languages": _explorer_level(source),
                "applies_to": ("speaking_unknown_language", "reading_unknown_language"),
                "source_ability": "Knack for Languages",
            },
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    }

build_shared_ability("shared.utility", KNACK_FOR_LANGUAGES, source_type="shared")