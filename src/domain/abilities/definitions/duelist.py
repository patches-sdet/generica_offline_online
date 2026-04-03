from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, scaled_derived_buff, skill_check, conditional_effect, ApplyChallengedEffect
from domain.conditions import IS_ALLY

build_job("Duelist", [

    # -------------------------
    # Passive
    # -------------------------
    {
        "name": "Weapon Specialist",
        "type": "passive",
        "effects": lambda c: scaled_derived_buff(
            stat="weapon", # needs to be a derived stat based on highest weapon skill
            scale_fn=lambda c: c.get_adventure_level_by_name("Duelist", 0),
        )(c),
        "description": "Enhances your highest weapon skill. If you have two or more that are equal, you may choose which one to specialize in.",
    },

    # -------------------------
    # Active
    # -------------------------
    {
    "name": "Challenge",
    "type": "skill",
    "cost": 5,
    "cost_pool": "moxie",
    "duration": "5 minutes",
    "target": "enemy",
    "effects": lambda ctx: [
        skill_check(
            ability="Challenge",
            stat="charisma",
            difficulty=lambda check_ctx, target: target.roll_charisma(),
            on_success=lambda check_ctx, target: [
                clear_existing_challenges(check_ctx.source),
                conditional_effect(
                    ApplyChallengedEffect(
                        challenger=check_ctx.source,
                        penalty=check_ctx.source.get_progression_level("adventure", "Duelist"),
                        duration="5 minutes",
                    ),
                    condition=lambda inner_ctx, inner_target: inner_target is target,
                    )
                ],
            )
        ],"description": "Challenge an enemy to a duel. If you succeed, they become Challenged, taking penalties to their rolls based on your Duelist level. Only one enemy can be Challenged at a time.",
    },

    {
    "name": "Dazzling Entrance",
    "type": "skill",
    "cost": 10,
    "cost_pool": "moxie",
    "duration": "1 Turn/level",
    "target": "self",
    "effects": lambda ctx: buff (
        scale_fn=lambda c: c.get_progression_level("adventure", "Duelist"),
        stats = {
            "charisma": 1,
            "cool": 1}
    ),"description": "Used before revealing yourself to foes, the more dramatic your entrance, the better. This buffs your Charisma and Cool equal to your Duelist level. Lasts for a number of turns equal to the level of this skill.",
    },

    {
    "name": "Fancy Flourish",
    "type": "skill",
    "cost": 5,
    "cost_pool": "moxie",
    "duration": "5 minutes",
    "target": "enemy",
    "effects": lambda ctx: [
        skill_check(
            ability="Challenge",
            stat="charisma",
            difficulty=lambda check_ctx, target: target.roll_charisma(),
            on_success=lambda check_ctx, target: [
                clear_existing_challenges(check_ctx.source),
                conditional_effect(
                    ApplyChallengedEffect(
                        challenger=check_ctx.source,
                        penalty=check_ctx.source.get_progression_level("adventure", "Duelist"),
                        duration="5 minutes",
                    ),
                    condition=lambda inner_ctx, inner_target: inner_target is target,
                    )
                ],
            )
        ],"description": "Challenge an enemy to a duel. If you succeed, they become Challenged, taking penalties to their rolls based on your Duelist level. Only one enemy can be Challenged at a time.",
    },

    {
    "name": "Guard Stance",
    "type": "skill",
    "cost": 5,
    "cost_pool": "moxie",
    "duration": "5 minutes",
    "target": "enemy",
    "effects": lambda ctx: [
        skill_check(
            ability="Challenge",
            stat="charisma",
            difficulty=lambda check_ctx, target: target.roll_charisma(),
            on_success=lambda check_ctx, target: [
                clear_existing_challenges(check_ctx.source),
                conditional_effect(
                    ApplyChallengedEffect(
                        challenger=check_ctx.source,
                        penalty=check_ctx.source.get_progression_level("adventure", "Duelist"),
                        duration="5 minutes",
                    ),
                    condition=lambda inner_ctx, inner_target: inner_target is target,
                    )
                ],
            )
        ],"description": "Challenge an enemy to a duel. If you succeed, they become Challenged, taking penalties to their rolls based on your Duelist level. Only one enemy can be Challenged at a time.",
    }
])
