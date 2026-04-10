from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import conditional_effect, scaled_stat_buff

POISON_RESISTANCE = {
    "name": "Poison Resistance",
    "type": "passive",
    "description": "You may make Constitution rolls to resist poison and add your level in this skill to the roll.",
    "effects": conditional_effect(
        scaled_stat_buff(
            scale_fn=lambda ctx: ctx.ability_levels.get("Poison Resistance", 0),
            stats="constitution",
        ),
        condition=lambda ctx: ctx.action_type == "resist_poison",
    ),
    "is_passive": True,
    "is_skill": True,
    "scales_with_level": True,
}

build_shared_ability("shared.utility", POISON_RESISTANCE, source_type="shared")