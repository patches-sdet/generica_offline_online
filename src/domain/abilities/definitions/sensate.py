from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, scaled_derived_buff, skill_check
from domain.conditions import IS_ALLY, IS_ENEMY

build_job("Sensate", [

    {
        "name": "Dull Sense",
        "cost": 5,
        "cost_pool": "sanity",
        "description": "This debuff reduces the target's Perception by an amount equal to your level in this skill, if you succeed on an Intelligence plus Dull Sense roll against their Wisdom. If you succeed, the target is unaware of the effect. This skill is a spell.",
        "duration": "1 minute/Sensate level",
        "effects": [
            skill_check(
                ability="Dull Sense",
                stat="intelligence",
                difficulty=lambda target: target.roll_wisdom(),
                on_success=lambda ctx: [
            buff(
                stat="perception",
                scale_fn=lambda c: -c.ability_levels.get("Dull Sense", 0),
                conditions=IS_ENEMY,
                    )
                ]
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
