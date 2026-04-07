from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, conditional_effect
from domain.conditions import IS_LYING

build_job("Grifter", [

    {
        "name": "Silver Tongue",
        "cost": 10,
        "cost_pool": "moxie",
        "description": "The Grifter gets a bonus to Charisma equal to their level in this ability, but only while lying.",
        "duration": "10 minutes/level",
        "effects": [
            conditional_effect(
                effect=buff(
                    scale_fn=lambda char_ctx: char_ctx.ability_levels.get("Silver Tongue", 0),
                    stats={"charisma": 1},
                    condition=None,
                ),
                condition=IS_LYING,
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
