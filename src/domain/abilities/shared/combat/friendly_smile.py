from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state

FRIENDLY_SMILE = {
        "name": "Friendly Smile",
        "cost": 15,
        "cost_pool": "moxie",
        "description": (
            "Smile at a target to prevent them from attacking you on success, and gain a bonus "
            "to Charisma rolls against them."
        ),
        "duration": "1 Turn",
        "effects": apply_state(
            "friendly_smile_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns_on_success": _merchant_level(source),
                "contest": {
                    "caster_stat": "charisma",
                    "caster_skill": "Friendly Smile",
                    "target_stat": "willpower",
                },
                "target_must_see_smile": True,
                "no_vocalization_required": True,
                "prevents_target_attacking_caster": True,
                "charisma_bonus_against_target": _merchant_level(source),
                "source_ability": "Friendly Smile",
            },
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    }

build_shared_ability("shared.combat", FRIENDLY_SMILE, source_type="shared")