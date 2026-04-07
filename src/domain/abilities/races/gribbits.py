from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import  buff

build_job("Gribbit", [
    {
    "name": "Amphibious",
    "required_level": 1,
    "type": "skill",
    "cost": 5,
    "cost_pool": "stamina",
    "description": "Renders you immune to drowning while this buff is active. This skill has no levels.",
    "effects": lambda ctx: [
        buff(
            stats={"drowning_immunity": 1},
        )
    ],
    "scales_with_level": False,
},

    {
        "name": "Hop",
        "required_level": 1,
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "description": "You can leap a number of feet equal to 3 times your Gribbit level without any roll required. This skill has no levels.",
        "effects": [], # TODO: This is a complicated effect that might need a custom pattern or effect.
        "scales_with_level": False,
    },

])