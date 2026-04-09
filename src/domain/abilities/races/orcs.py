from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import  apply_state, scaled_stat_buff, scaled_derived_buff

build_job("Orc", [
    {"grant": "Darkspawn", "required_level": 1},

    {
        "name": "Twisted Rage",
        "required_level": 1,
        "type": "skill",
        "cost": 5,
        "cost_pool": "HP",
        "description": "You can fly into a rage so strong it warps your muscles and tears your flesh. While raging, you cannot use ranged attacks or spells and you suffer a Perception debuff equal to your Orc level. You may however, add your Orc level to all other rolls while raging. You cannot rage for more turns than you have levels in this skill.",
        "effects": lambda ctx: [
            apply_state("raging"),
            apply_state("cannot_use_ranged_attacks"),
            apply_state("cannot_cast_spells"),
            scaled_stat_buff(
                scale_fn=lambda c: c.get_progression_level("race", "Orc", 0),
                stats={"perception": -1},
            ),
            scaled_derived_buff(
                scale_fn=lambda c: c.get_progression_level("race", "Orc", 0),
                stat="all_rolls",
                condition=lambda c: "raging" in getattr(c.source, "states", {}),
            ),
        ],
        "duration": "1 turn per level",
        "scales_with_level": True,
    },
])