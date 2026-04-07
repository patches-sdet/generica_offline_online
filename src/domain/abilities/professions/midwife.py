from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, create_item, scaled_derived_buff, skill_check
from domain.conditions import IS_ALLY
from domain.effects.base import CONTEXT_OPTIONS

JEWEL_DIFFICULTIES = {
    "common": 100,
    "uncommon": 200,
    "rare": 300,
}

build_job("Midwife", [

    # Newborn's Mercy
    {
        "name": "Newborn's Mercy",
        "required_level": 1,
        "type": "skill",
        "description": "You gently touch a newborn's forehead and buff its luck by an amount equal to your level in this skill. This buff can only be applied once per midwife per infant. For each year the newborn ages, the buff decreases by 10 until it is gone.",
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda ctx, target: ctx.source.get_skill_level("Newborn's Mercy"),
                stats={"luck": 1},
                condition=IS_ALLY,
                        ),
                ],
    },

])
