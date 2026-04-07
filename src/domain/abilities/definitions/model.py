from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, scaled_derived_buff
from domain.conditions import IS_ALLY

build_job("Model", [

    {
        "name": "Work it Baby!",
        "description": "All worn and wielded items that give bonuses have those bonuses increased by 1 for each level of this skill.",
        "duration": "Passive Constant",
        "effects": [ # TODO: This is a hack to get things to work for now, but it will need a way to increase equipment effects
                buff(
                    scale_fn=lambda c: c.ability_levels.get("Work it Baby!", 0),
                    stats={"all": 1},
                    condition=None,
                )
        ],
        "is_passive": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

])
