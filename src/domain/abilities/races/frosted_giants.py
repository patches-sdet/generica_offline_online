from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import  buff

build_job("Frosted Giant", [
    {
    "name": "Don't Sveat de Smol Stuff",
    "required_level": 1,
    "type": "passive",
    "description": "Giants are particularly lazy when it comes to developing their smarts. It costs them 1 extra grind point whenever they wish to level a mental attribute. This skill has no levels.",
    "effects": lambda ctx: [
        buff(
            stats={"grind_point_cost": 1},
            condition=lambda ctx: (
                ctx.action_type == "raise_attribute_with_grind"
                and ctx.attribute_name in {"intelligence", "wisdom", "perception", "willpower"}
            ),
        )
    ],
    "scales_with_level": False,
},

    {
        "name": "Large and In Charge",
        "required_level": 1,
        "type": "passive",
        "description": "Your height is equal to 6 feet plus your Giant level. If you are taller than your enemy, you gan a buff to your attack rolls against it equal to your Giant level. This skill has no levels.",
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda ctx: ctx.get_progression_level("race", "Frosted Giant"),
                stats={"attack_roll": 1},
                condition=lambda ctx: ctx.source.height > ctx.target.height
            )
        ],
        "scales_with_level": False,
    },

    {
        "name": "Sving for de Bleachers",
        "required_level": 1,
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "description": "Your next attack has a chance to knock a foe back. Campare your margin of success to their strength; if it is greater, you knock them back a number of feet equal to your giant level. This skill has no levels.",
        "effects": [], # TODO: This is a complicated effect that might need a custom pattern or effect.
        "scales_with_level": False, 
    },

])