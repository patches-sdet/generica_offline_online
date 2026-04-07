from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    conditional_damage,
    skill_check,
    inspect,
    buff,
    apply_state,
)
from domain.conditions.state import IS_SURPRISED, IS_HELPLESS
from domain.conditions.combat import IS_ENEMY

build_job("Assassin", [

# Backstab — Conditional Bonus Damage
{
    "name": "Backstab",
    "cost": 10,
    "cost_pool": "stamina",
    "description": "Add one point of damage per skill level to any attack made on a surprised or helpless target. At the GM's discretion, the Assassin may be able to add this bonus if they can attack a target's back.",
    "duration": "5 minutes",
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
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": True,
    "target": "enemy",
    "type": "skill",
},

# Cold Read — Opposed Inspection
{
    "name": "Cold Read",
    "cost": 5,
    "cost_pool": "moxie",
    "description": "The Assassin can learn how tough the target is comparatively to themself, and if they have any vulnerabilities. This is a Perception plus Cold Read skill roll, resisted by the target's Charisma roll.",
    "duration": "1 turn",
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
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": True,
    "target": "enemy",
    "type": "skill",
},

# Fast as Death — Speed/Initiative Buff
{"grant": "Fast as Death", "required_level": 1},

# Quickdraw
{"grant": "Quickdraw", "required_level": 1},

# Unobtrusive — Passive Social Stealth
{
    "name": "Unobtrusive",
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
    "is_passive": True,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": True,
    "target": "self",
    "type": "passive",
    },
]
)