from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    modify_next_attack,
    extra_attacks,
    passive_modifier,
)


build_job("Archer", [

    # Aim
    {
        "name": "Aim",
        "cost": 10,
        "cost_pool": "fortune",
        "description": "Improve accuracy for a single attack by the level of this skill.",
        "duration": "1 turn",
        "effects": lambda ctx, targets: [
            modify_next_attack(
                lambda ctx, attack: attack.add_bonus(
                    "accuracy",
                    ctx.source.ability_levels["Aim"],
                )
            )
        ],
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Missile Mastery
    {
        "name": "Missile Mastery",
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
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Quickdraw
    {"grant": "Quickdraw", "required_level": 1},
    
    # Rapid Fire
    {
        "name": "Rapid Fire",
        "cost": 10,
        "cost_pool": "stamina",
        "description": "The Archer may make two attacks as part of an attack action instead of one. All costs must be paid as normal. This skill can only be used once per turn. This skill has no levels.",
        "effects": lambda ctx, targets: [
            extra_attacks(1)
        ],
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Ricochet Shot
    {
        "name": "Ricochet Shot",
        "cost": 5,
        "cost_pool": "fortune",
        "description": "Bounce a shot off a surface to hit difficult targets. Reduces penalties for these shots by this skill's level.",
        "duration": "1 attack",
        "effects": lambda ctx, targets: [
            modify_next_attack(
                lambda ctx, attack: attack.reduce_penalty(
                    ctx.source.ability_levels["Ricochet Shot"]
                )
            )
        ],
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

])