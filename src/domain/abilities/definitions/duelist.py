from dataclasses import dataclass
from typing import Any
from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import scaled_stat_buff, skill_check, conditional_effect, scaled_derived_buff
from domain.effects.conditional import CompositeEffect, HighestWeaponSkillBonus
from domain.effects.base import Effect, EffectContext
    
@dataclass(slots=True)
class ApplyChallengedEffect(Effect):
    challenger: Any
    penalty: int
    duration: Any

    def apply(self, context: EffectContext):
        for target in context.targets:
            target.states["challenged"] = {
                "challenger": self.challenger,
                "penalty": self.penalty,
                "duration": self.duration,
            }

def clear_existing_challenges(character):
    if "challenged" in character.states:
        del character.states["challenged"]

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
    "effects": skill_check(
            ability="Challenge",
            stat="charisma",
            difficulty=lambda target: target.roll_charisma(),
            on_success=lambda check_ctx, target: [
                clear_existing_challenges(check_ctx.source),
                conditional_effect(
                    ApplyChallengedEffect(
                        challenger=check_ctx.source,
                        penalty=check_ctx.source.get_progression_level("adventure", "Duelist"),
                        duration="5 minutes",
                    ),
                    condition=lambda inner_target: inner_target is target,
                    )
                ],
            ),
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
    "effects": CompositeEffect(
        scaled_stat_buff(
        scale_fn=lambda c: c.get_progression_level("adventure", "Duelist"),
        stats = {
            "charisma": 1}
        ) and
        scaled_derived_buff(
        scale_fn=lambda c: c.get_progression_level("adventure", "Duelist"),
        stat = "cool",
        ),
    ),
    "is_skill": True,
    "required_level": 1,
    "scales_with_level": True,
    "target": "self",
    "type": "skill",
    },

    { # TODO: This is not what the skill does, need to update it
    "name": "Fancy Flourish",
    "cost": 5,
    "cost_pool": "moxie",
    "description": "Challenge an enemy to a duel. If you succeed, they become Challenged, taking penalties to their rolls based on your Duelist level. Only one enemy can be Challenged at a time.",
    "duration": "5 minutes",
    "effects": skill_check(
            ability="Challenge",
            stat="charisma",
            difficulty=lambda target: target.roll_charisma(),
            on_success=lambda check_ctx, target: [
                clear_existing_challenges(check_ctx.source),
                conditional_effect(
                    ApplyChallengedEffect(
                        challenger=check_ctx.source,
                        penalty=check_ctx.source.get_progression_level("adventure", "Duelist"),
                        duration="5 minutes",
                    ),
                    condition=lambda inner_target: inner_target is target,
                    )
                ],
            ),
    "is_skill": True,
    "required_level": 1,
    "scales_with_level": True,
    "target": "enemy",
    "type": "skill",
    },

    { # TODO: This is not what the skill does, need to update it
    "name": "Guard Stance",
    "cost": 5,
    "cost_pool": "moxie",
    "duration": "5 minutes",
    "description": "Challenge an enemy to a duel. If you succeed, they become Challenged, taking penalties to their rolls based on your Duelist level. Only one enemy can be Challenged at a time.",
    "effects": skill_check(
            ability="Challenge",
            stat="charisma",
            difficulty=lambda target: target.roll_charisma(),
            on_success=lambda check_ctx, target: [
                clear_existing_challenges(check_ctx.source),
                conditional_effect(
                    ApplyChallengedEffect(
                        challenger=check_ctx.source,
                        penalty=check_ctx.source.get_progression_level("adventure", "Duelist"),
                        duration="5 minutes",
                    ),
                    condition=lambda inner_target: inner_target is target,
                    )
                ],
            ),
    "is_skill": True,
    "required_level": 1,
    "scales_with_level": True,
    "target": "enemy",
    "type": "skill",
    }
],
source_type="adventure"
)