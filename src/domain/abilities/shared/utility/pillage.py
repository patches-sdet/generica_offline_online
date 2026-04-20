from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state

PILLAGE = {
        "name": "Pillage",
        "cost": 25,
        "cost_pool": "fortune",
        "description": (
            "Add Pillage level to perception rolls to detect hidden treasure or other valuables."
        ),
        "duration": "1 Minute",
        "effects": apply_state(
            "pillage_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": 1,
                "perception_bonus_for_valuables": _ability_level(source, "Pillage"),
                "source_ability": "Pillage",
            },
        ),
        "required_level": 15,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    }

build_shared_ability("shared.utility", PILLAGE, source_type="shared")