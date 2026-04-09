from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import  scaled_derived_buff

build_job("Halven", [
    {
    "name": "Fate's Friend",
    "required_level": 1,
    "type": "passive",
    "description": "You gain a bonus to your Fate equal to your Halven level.",
    "effects": lambda ctx: [
        scaled_derived_buff(
            scale_fn=lambda ctx: ctx.source.get_progression_level("race", "Halven"),
            stat="fate",
            )
        ],
    },

    {
    "name": "Small in a Good Way",
    "required_level": 1,
    "type": "passive",
    "description": "Whenever your size would be an advantage for the situation you're in, you gain a bonus to all rolls equal to your Halven level.",
    "effects": lambda ctx: [
        scaled_derived_buff(
            scale_fn=lambda ctx: ctx.source.get_progression_level("race", "Halven"),
            stat="all_rolls",
            condition=lambda ctx: ctx.metadata.get("size_advantage", False),
            )
        ],
    "scales_with_level": False,
    },
])