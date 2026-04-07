from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, scaled_derived_buff, scaled_stat_buff
from domain.conditions import IS_ALLY

build_job("Scout", [

    {
        "name": "Keen Eye",
        "cost": 5,
        "cost_pool": "stamina",
        "description": "Your Perception is boosted by an amount equal to your level in this skill.",
        "duration": "1 minute/Scout level",
        "effects": [
            scaled_stat_buff(
                scale_fn=lambda c: c.ability_levels.get("Keen Eye", 0),
                stats="perception",
                condition=None,
            )
        ],
        "is_passive": False,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

])
