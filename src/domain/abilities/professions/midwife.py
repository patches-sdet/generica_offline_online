from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import scaled_stat_buff
from domain.conditions import IS_ALLY

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
        "effects": scaled_stat_buff(
                scale_fn=lambda ctx, target: ctx.source.get_skill_level("Newborn's Mercy"),
                stats={"luck": 1},
                condition=IS_ALLY,
                        ),
    },

])
