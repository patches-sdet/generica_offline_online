from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state

MANA_FOCUS = {
    "name": "Mana Focus",
    "description": (
        "This skill increases your maximum sanity pool by a percentage equal to the "
        "level of the job granting it. Mana Focus from different jobs does not stack."
    ),
    "duration": "Passive Constant",
    "effects": apply_state(
        "mana_focus",
        value_fn=lambda source: {
            "active": True,
            "non_stacking": True,
            "affects_pool": "sanity",
            "bonus_type": "percent",
            "pending_source_resolution": True,
            "source_ability": "Mana Focus",
        },
    ),
    "is_passive": True,
    "is_skill": False,
    "is_spell": False,
    "scales_with_level": False,
    "target": "self",
    "type": "passive",
}

build_shared_ability("shared.utility", MANA_FOCUS, source_type="adventure")