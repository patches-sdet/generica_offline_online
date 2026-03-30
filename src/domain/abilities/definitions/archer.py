from domain.abilities import make_ability
from domain.abilities.patterns import modify_next_attack, extra_attacks, passive_modifier, action_override

# Aim — Buff Next Attack Accuracy

def aim_execute(caster, targets):
    return [
        modify_next_attack(
            lambda attack: attack.add_bonus(
                "accuracy",
                caster.skills.get("Aim", 0)
            )
        )
    ]

# Missile Mastery — Passive Skill Substitution

def missile_mastery_effects(character):
    return [
        passive_modifier(
            lambda ctx: ctx.modify_attack_skill(
                replacement=lambda original, character: (
                    max(character.ranged_skills.values()) // 2
                )
            )
        )
    ]

# Quickdraw — Action Economy Override

def quickdraw_execute(caster, targets):
    return [
        action_override(
            lambda ctx: ctx.set_draw_cost(0)
        )
    ]

# Rapid Fire — Extra Attacks

def rapid_fire_execute(caster, targets):
    return [
        extra_attacks(1)  # +1 attack (total = 2)
    ]

# Ricochet Shot — Ignore Penalties

def ricochet_execute(caster, targets):
    return [
        modify_next_attack(
            lambda attack: attack.reduce_penalty(
                caster.skills.get("Ricochet Shot", 0)
            )
        )
    ]

# Registration

def register():

    make_ability(
        name="Aim",
        unlock_condition=lambda c: (
            c.has_adventure_job("Archer")
            and c.get_adventure_level_by_name("Archer") >= 1
        ),
        execute=aim_execute,
        cost=10,
        cost_pool="fortune",
        duration="1 turn",
        description="Improve accuracy for a single attack by the level of this skill.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Missile Mastery",
        unlock_condition=lambda c: (
            c.has_adventure_job("Archer")
            and c.get_adventure_level_by_name("Archer") >= 1
        ),
        effect_generator=missile_mastery_effects,
        description="When attacking with ranged weapons, Archers may substitute half of their highest ranged weapon skill, instead of the skill they would normally use.\n     The experience roll for this attack uses the skill that this skill replaces. Affected skill groups are Archery, Magic Bolts, Throwing, Guns, and Siege Engines. This skill has no levels.",
        is_passive=True,
        is_skill=False,
    )

    make_ability(
        name="Quickdraw",
        unlock_condition=lambda c: (
            c.has_adventure_job("Archer")
            and c.get_adventure_level_by_name("Archer") >= 1
        ),
        execute=quickdraw_execute,
        cost=5,
        cost_pool="stamina",
        duration="1 minute",
        description="After activating this skill, the Archer does not need to spend an action to draw any weapon or item on their person. It still costs an action to draw from a pack. This skill has no levels.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Rapid Fire",
        unlock_condition=lambda c: (
            c.has_adventure_job("Archer")
            and c.get_adventure_level_by_name("Archer") >= 1
        ),
        execute=rapid_fire_execute,
        cost=10,
        cost_pool="stamina",
        description="The Archer may make two attacks as part of an attack action, instead of one. All costs must be paid as normal. \n     This skill can only be used once per turn. This skill has no levels.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Ricochet Shot",
        unlock_condition=lambda c: (
            c.has_adventure_job("Archer")
            and c.get_adventure_level_by_name("Archer") >= 1
        ),
        execute=ricochet_execute,
        cost=5,
        cost_pool="fortune",
        duration="1 attack",
        description="Bounce a shot off a surface to hit difficult targets. Reduces penalties for these shots by this skill's level.",
        is_passive=False,
        is_skill=True,
    )
