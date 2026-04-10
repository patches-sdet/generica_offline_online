from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import scaled_derived_buff
from domain.conditions import IS_ALLY
from domain.effects.conditional import CompositeEffect

build_job("Ruler", [

    {
        "name": "Emboldening Speech",
        "cost": 10,
        "cost_pool": "moxie",
        "description": "You give an emboldening speech to your party, granting them increased Moxie and Sanity equal to your Charisma divided by 5, plus your level in this skill. Activating this takes a full turn, but lasts for one minute per Ruler level.",
        "duration": "1 Minute/Ruler level",
        "effects": [
            CompositeEffect(
                effects=[
                    scaled_derived_buff(
                        stat="moxie",
                        scale_fn=lambda ctx: (ctx.user.charisma // 5) + ctx.ability_levels.get("Emboldening Speech", 0),
                        condition=IS_ALLY,
                    ),
                    scaled_derived_buff(
                        stat="sanity",
                        scale_fn=lambda ctx: (ctx.user.charisma // 5) + ctx.ability_levels.get("Emboldening Speech", 0),
                        condition=IS_ALLY,
                    ),
                ]
            )
        ],
        "is_passive": False,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "allies",
        "type": "skill",
    },
],
source_type="adventure"
)