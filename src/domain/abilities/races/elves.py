from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import on_event, scaled_stat_buff
from domain.effects.special.event import ModifyGrindPointAwardEffect, GainGrindPointsEffect
from domain.effects.conditional import CompositeEffect

build_job("Elf", [
    {
    "name": "Elven Eyes",
    "required_level": 1,
    "type": "skill",
    "cost": 10,
    "cost_pool": "fortune",
    "description": "This buff adds its level to all your perception rolls while active.",
    "duration": "1 minute",
    "effects": scaled_stat_buff(
            scale_fn=lambda ctx: ctx.source.ability_levels["Elven Eyes"],
            stats={"perception": 1},
            condition=lambda ctx: getattr(ctx, "roll_type", None) == "perception",
        ),
    "scales_with_level": True,
    },

    {
    "name": "Double-edged Immortality",
    "required_level": 1,
    "type": "passive",
    "description": "Whenever the GM hands out grind point based on time, you receive one less, minimum of 1. Whenever you critically fail a roll, you instead gain 2 grind points. This skill has no levels.",
    "effects": CompositeEffect(
        on_event(
            "grind_points_awarded",
            ModifyGrindPointAwardEffect(-1, minimum=1),
            condition=lambda ctx, target: ctx.metadata.get("reason") == "time",
        ),
        on_event(
            "critical_failure",
            GainGrindPointsEffect(2),
            ),
    ),
    "scales_with_level": False,
    }
],
source_type="race",
)