from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import scaled_stat_buff

build_job("Model", [

    {
        "name": "Work it Baby!",
        "description": "All worn and wielded items that give bonuses have those bonuses increased by 1 for each level of this skill.",
        "duration": "Passive Constant",
        "effects": scaled_stat_buff( # TODO: This is a hack to get things to work for now, but it will need a way to increase equipment effects
                    scale_fn=lambda c: c.ability_levels.get("Work it Baby!", 0),
                    stats={"all": 1},
                    condition=None,
                ),
        "is_passive": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

])
