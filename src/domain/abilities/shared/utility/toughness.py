from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import scaled_derived_buff

TOUGHNESS = {
    "name": "Toughness",
    "type": "passive",
    "description": "Can increase whenever you take serious damage. Increases your Maximum HP by two for each level this skill has.",
    "effects": scaled_derived_buff (
            scale_fn=lambda ctx: ctx.source.ability_levels["Toughness"] * 2,
            stat="max_hp",
            condition=lambda ctx: ctx.damage_taken >= {"constitution" + "toughness"},
        ),
    "is_passive": True,
    "is_skill": True,
    "scales_with_level": True,
}

build_shared_ability("shared.utility", TOUGHNESS)