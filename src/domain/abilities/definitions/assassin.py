from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    modify_next_attack,
    conditional_damage,
    skill_check,
    inspect,
    action_override,
    buff,
    apply_state,
)
from domain.conditions.state import IS_SURPRISED, IS_HELPLESS
from domain.conditions.combat import IS_ENEMY

build_job("Assassin", [

    # Backstab — Conditional Bonus Damage
    {
        "name": "Backstab",
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "duration": "5 minutes",
        "description": "Add one point of damage per skill level to any attack made on a surprised or helpless target. At the GM's discretion, the Assassin may be able to add this bonus if they can attack a target's back.",
        "effects": lambda ctx, targets: [
            conditional_damage(
                scale_fn=lambda ctx: ctx.source.ability_levels["Backstab"],
                # applies_to="attack", once combat resolution is implemented
                condition=lambda effect_ctx, target: (
                    IS_SURPRISED(effect_ctx, target) 
                    or IS_HELPLESS(effect_ctx, target)
                ),
            ),
        ],
    },

    # Cold Read — Opposed Inspection
    {
        "name": "Cold Read",
        "type": "skill",
        "cost": 5,
        "cost_pool": "moxie",
        "duration": "1 turn",
        "description": "The Assassin can learn how tough the target is comparatively to themself, and if they have any vulnerabilities. This is a Perception plus Cold Read skill roll, resisted by the target's Charisma roll.",
        "effects": lambda ctx, targets: [
            skill_check(
                ability="Cold Read",
                stat="perception",
                difficulty=lambda ctx, target: target.roll_charisma(),
                on_success=[
                    inspect(
                        reveal_fn=lambda ctx, target: {
                            "relative_power": compare_total_levels(inspect_ctx.source, target),
                            "vulnerabilities": get_vulnerabilities(target),
                        }
                    ),
                ],
            ),
        ],
    },

    # Fast as Death — Speed/Initiative Buff
    {
        "name": "Fast as Death",
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "duration": "1 turn per level",
        "description": "For the duration of this skill, the Assassin adds 50 to both their initiative and the distance in feet they can run per action. This is a buff.",
        "effects": lambda ctx: [
            buff(
                stats={
                    "initiative": 50,
                    "movement": 50,
                },
            ),
        ],
    },

    # Quickdraw
    {"grant": "Quickdraw"},

    # Unobtrusive — Passive Social Stealth
    {
        "name": "Unobtrusive",
        "type": "passive",
        "description": "This skill allows an Assassin to blend in with a crowd, reducing the chance that their motives or presence will be questioned, or possibly even being noticed. This provides a bonus equalt to its level to Charisma when applicable.",
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda ctx: ctx.source.ability_levels["Unobtrusive"],
                stats={"charisma": 1},
            ),
            apply_state(
                "low_profile",
                target="self",
                ),
            ],
        },
]
)