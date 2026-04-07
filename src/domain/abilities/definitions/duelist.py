from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, scaled_derived_buff, skill_check, conditional_effect, clear_existing_challenges, ApplyChallengedEffect
from domain.effects.conditional import HighestWeaponSkillBonus

build_job("Duelist", [

    # Passive
    {
        "name": "Weapon Specialist",
        "description": "Enhances your highest weapon skill. If you have two or more that are equal, you may choose which one to specialize in.",
        "effects": lambda ctx: HighestWeaponSkillBonus(
            scale_fn=lambda c: c.get_progression_level("adventure", "Duelist"),
        ),
        "is_passive": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "passive",
    },

    # Active
    {
    "name": "Challenge",
    "cost": 5,
    "cost_pool": "moxie",
    "description": "Challenge an enemy to a duel. If you succeed, they become Challenged, taking penalties to their rolls based on your Duelist level. Only one enemy can be Challenged at a time.",
    "duration": "5 minutes",
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
        ],
    "is_skill": True,
    "required_level": 1,
    "scales_with_level": True,
    "target": "enemy",
    "type": "skill",
    },

    {
    "name": "Dazzling Entrance",
    "cost": 10,
    "cost_pool": "moxie",
    "description": "Used before revealing yourself to foes, the more dramatic your entrance, the better. This buffs your Charisma and Cool equal to your Duelist level. Lasts for a number of turns equal to the level of this skill.",
    "duration": "1 Turn/level",
    "effects": lambda ctx: buff (
        scale_fn=lambda c: c.get_progression_level("adventure", "Duelist"),
        stats = {
            "charisma": 1,
            "cool": 1}
    ),
    "is_skill": True,
    "required_level": 1,
    "scales_with_level": True,
    "target": "self",
    "type": "skill",
    },

    {
    "name": "Fancy Flourish",
    "cost": 5,
    "cost_pool": "moxie",
    "description": "Challenge an enemy to a duel. If you succeed, they become Challenged, taking penalties to their rolls based on your Duelist level. Only one enemy can be Challenged at a time.",
    "duration": "5 minutes",
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
        ],
    "is_skill": True,
    "required_level": 1,
    "scales_with_level": True,
    "target": "enemy",
    "type": "skill",
    },

    {
    "name": "Guard Stance",
    "cost": 5,
    "cost_pool": "moxie",
    "duration": "5 minutes",
    "description": "Challenge an enemy to a duel. If you succeed, they become Challenged, taking penalties to their rolls based on your Duelist level. Only one enemy can be Challenged at a time.",
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
        ],
    "is_skill": True,
    "required_level": 1,
    "scales_with_level": True,
    "target": "enemy",
    "type": "skill",
    }
])
