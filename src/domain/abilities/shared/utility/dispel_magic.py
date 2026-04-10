from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import skill_check

DISPEL_MAGIC = {
    "name": "Dispel Magic",
    "type": "skill",
    "cost": 50,
    "cost_pool": "sanity",
    "duration": "1 Action",
    "description": "You can attempt to dispel a magical effect on a target, location, fixed spell, or other similar effects. You make a Wisdom plus Dispel Magic roll versus the target's Willpower. The margin of success determines the number of effects dispelled. A critical success removes ALL effects. This skill is a spell.",
    "effects": skill_check(
            ability="Dispel Magic",
            stat="willpower",
            difficulty=lambda target: target.roll_willpower(),
            on_success=lambda ctx, target: ctx.dispel_effects(target, amount=ctx.margin_of_success),
        ),
    "is_passive": False,
    "is_skill": True,
    "scales_with_level": True,
}

build_shared_ability("shared.utility", DISPEL_MAGIC, source_type="adventure")