from domain.abilities.job_builder import build_job
from domain.abilities.patterns import buff, heal, scaled_derived_buff
from domain.conditions import IS_ALLY

build_job("Model", [

    # -------------------------
    # Passive
    # -------------------------
    {
        "name": "Faith",
        "type": "passive",
        "effects": lambda c: scaled_derived_buff(
            stat="fate",
            scale_fn=lambda c: c.get_adventure_level_by_name("Model", 0),
        )(c),
        "description": "Your Fate increases with Model level.",
    },

    # -------------------------
    # Example Skill
    # -------------------------
    {
        "name": "Example Skill",
        "type": "skill",
        "cost": 1,
        "cost_pool": "fortune",
        "target": "ally",
        "effects": lambda caster, targets: [
            buff(
                scale_fn=lambda c: c.pools.get("fortune", 0),
                stats={"any": 1},
                condition=IS_ALLY,
            )
        ],
    },

])
