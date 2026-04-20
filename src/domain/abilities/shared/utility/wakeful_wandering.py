from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state

WAKEFUL_WANDERING = {
    "name": "Wakeful Wandering",
    "cost": 5,
    "cost_pool": "sanity",
    "description": (
        "Forgo sleep for a time. While active, you suffer no penalty from exhaustion or insomnia "
        "and continue to regain your pools naturally. When it ends, roll Constitution plus Wakeful "
        "Wandering against a difficulty equal to hours active times ten. Margin of failure determines "
        "how many minutes you collapse unconscious afterward."
    ),
    "duration": "Until Released",
    "effects": apply_state(
        "wakeful_wandering_active",
        value_fn=lambda source: {
            "active": True,
            "cost_per_hour": 5,
            "cost_pool": "sanity",
            "ignore_exhaustion_penalties": True,
            "ignore_insomnia_penalties": True,
            "natural_pool_regeneration_continues": True,
            "end_check": {
                "stat": "constitution",
                "skill": "Wakeful Wandering",
                "difficulty": "hours_active * 10",
            },
            "failure_result": {
                "collapse_unconscious": True,
                "unconscious_duration_minutes": "margin_of_failure",
                "insensate_while_unconscious": True,
            },
            "source_ability": "Wakeful Wandering",
        },
    ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": False,
    "target": "self",
    "type": "skill",
}

build_shared_ability("shared.utility", WAKEFUL_WANDERING, source_type="adventure")