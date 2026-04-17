from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import apply_state


STAREDOWN = {
    "name": "Staredown",
    "cost": 25,
    "cost_pool": "moxie",
    "description": (
        "You glare at your target with raw fighting spirit. This is a Willpower plus Staredown attack "
        "against the target's Willpower, inflicting moxie damage if successful. Cool reduces damage as normal."
    ),
    "duration": "1 Attack",
    "effects": apply_state(
        "staredown_ready",
        value_fn=lambda source: {
            "active": True,
            "attack_stat": "willpower",
            "skill_name": "Staredown",
            "target_stat": "willpower",
            "damage_pool": "moxie",
            "damage_bonus": source.get_ability_effective_level("Staredown"),
            "damage_reduced_by": "cool",
            "source_ability": "Staredown",
        },
    ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "scales_with_level": True,
    "target": "enemy",
    "type": "skill",
}

build_shared_ability("shared.social", STAREDOWN, source_type="adventure")