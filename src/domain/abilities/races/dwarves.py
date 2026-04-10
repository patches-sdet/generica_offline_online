from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import  scaled_stat_buff

build_job("Dwarf", [
    {
    "name": "Stonecrafty",
    "required_level": 1,
    "type": "skill",
    "cost": 5,
    "cost_pool": "fortune",
    "description": "This skill adds its level to your Perception rolls when you examine stone, are moving around a mostly stone environment, or trying to detect someone standing on a stone surface. This skill is a buff.",
    "effects": lambda ctx: [
        scaled_stat_buff(
            scale_fn=lambda ctx: ctx.source.ability_levels["Stonecrafty"],
            stats={"perception": 1},
            condition=lambda ctx: ctx.action_type in {
            "examine_stone",
            "navigate_stone_environment",
            "detect_on_stone_surface",
                },
            )
        ],
    },

    {"grant": "Sturdy", "required_level": 1},
],
source_type="race",
)