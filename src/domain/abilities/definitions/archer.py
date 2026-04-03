from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    modify_next_attack,
    extra_attacks,
    passive_modifier,
    action_override,
)


build_job("Archer", [

    # Aim
    {
        "name": "Aim",
        "type": "skill",
        "cost": 10,
        "cost_pool": "fortune",
        "duration": "1 turn",
        "description": "Improve accuracy for a single attack by the level of this skill.",
        "effects": lambda ctx, targets: [
            modify_next_attack(
                lambda ctx, attack: attack.add_bonus(
                    "accuracy",
                    ctx.source.ability_levels["Aim"],
                )
            )
        ],
    },

    # Missile Mastery
    {
        "name": "Missile Mastery",
        "type": "passive",
        "description": "When attacking with ranged weapons, Archers may substitute half of their highest ranged weapon skill instead of the skill they would normally use. This skill has no levels.",
        "effects": lambda ctx: [
            passive_modifier(
                lambda ctx: ctx.modify_attack_skill(
                    replacement=lambda original, character: (
                        max(getattr(character, "ranged_skills", {}).values(), default=0) // 2
                    )
                )
            )
        ],
        "scales_with_level": False,
    },

    # Quickdraw
    {"grant": "Quickdraw"},
    
    # Rapid Fire
    {
        "name": "Rapid Fire",
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "description": "The Archer may make two attacks as part of an attack action instead of one. All costs must be paid as normal. This skill can only be used once per turn. This skill has no levels.",
        "effects": lambda ctx, targets: [
            extra_attacks(1)
        ],
        "scales_with_level": False,
    },

    # Ricochet Shot
    {
        "name": "Ricochet Shot",
        "type": "skill",
        "cost": 5,
        "cost_pool": "fortune",
        "duration": "1 attack",
        "description": "Bounce a shot off a surface to hit difficult targets. Reduces penalties for these shots by this skill's level.",
        "effects": lambda ctx, targets: [
            modify_next_attack(
                lambda ctx, attack: attack.reduce_penalty(
                    ctx.source.ability_levels["Ricochet Shot"]
                )
            )
        ],
    },

])