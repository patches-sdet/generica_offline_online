from domain.abilities import make_ability
from domain.abilities.patterns import (
    buff,
    inspect,
    skill_check,
    conditional_damage,
    action_override,
    apply_state,
)

from domain.conditions import (
    IS_SURPRISED,
    IS_HELpless,
    IS_ENEMY,
)

# =========================================================
# Backstab — Conditional Bonus Damage
# =========================================================

def backstab_execute(caster, targets):
    return [
        conditional_damage(
            scale_fn=lambda c: c.skills.get("Backstab", 0),
            condition=lambda ctx, target: (
                IS_SURPRISED(ctx, target) or IS_HELpless(ctx, target)
            ),
        )
    ]


# =========================================================
# Cold Read — Opposed Inspection
# =========================================================

def cold_read_execute(caster, targets):
    return [
        skill_check(
            skill="Cold Read",
            stat="perception",
            difficulty=lambda ctx, target: target.roll_charisma(),
            on_success=inspect(
                reveal_fn=lambda caster, target: {
                    "relative_power": compare_power(caster, target),
                    "vulnerabilities": get_vulnerabilities(target),
                }
            ),
        )
    ]


# =========================================================
# Fast as Death — Speed/Initiative Buff
# =========================================================

def fast_as_death_execute(caster, targets):
    return [
        buff(
            scale_fn=lambda c: 50,  # flat bonus
            stats={
                "initiative": 1,
                "movement": 1,
            },
        )
    ]


# =========================================================
# Quickdraw — Action Override (same pattern as Archer)
# =========================================================

def quickdraw_execute(caster, targets):
    return [
        action_override(
            lambda ctx: ctx.set_draw_cost(0)
        )
    ]


# =========================================================
# Unobtrusive — Passive Social Stealth
# =========================================================

def unobtrusive_effects(character):
    return [
        buff(
            scale_fn=lambda c: c.skills.get("Unobtrusive", 0),
            stats={"charisma": 1},
        ),
        apply_state("low_profile"),
    ]


# =========================================================
# Registration
# =========================================================

def register():

    make_ability(
        name="Backstab",
        unlock_condition=lambda c: (
            c.has_adventure_job("Assassin")
            and c.get_adventure_level_by_name("Assassin") >= 1
        ),
        execute=backstab_execute,
        cost=10,
        cost_pool="stamina",
        duration="5 minutes",
        description="Add one point of damage per skill level to any attack made on a surprised or helpless target. At the GM's discretion, the Assassin may be able to add this bonus if they can attack a target's back.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Cold Read",
        unlock_condition=lambda c: (
            c.has_adventure_job("Assassin")
            and c.get_adventure_level_by_name("Assassin") >= 1
        ),
        execute=cold_read_execute,
        cost=5,
        cost_pool="moxie",
        duration="1 turn",
        description="The Assassin can learn how tough the target is comparatively to themself, and if they have any vulnerabilities. This is a Perception plus Cold Read skill roll, resisted by the target's Charisma roll.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Fast as Death",
        unlock_condition=lambda c: (
            c.has_adventure_job("Assassin")
            and c.get_adventure_level_by_name("Assassin") >= 1
        ),
        execute=fast_as_death_execute,
        cost=10,
        cost_pool="stamina",
        duration="1 turn per level",
        description="For the duration of this skill, the Assassin adds 50 to both their initiative and the distance in feet they can run per action.\n     This is a buff.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Quickdraw",
        unlock_condition=lambda c: (
            c.has_adventure_job("Assassin")
            and c.get_adventure_level_by_name("Assassin") >= 1
        ),
        execute=quickdraw_execute,
        cost=5,
        cost_pool="stamina",
        duration="1 minute",
        description="After activating this skill, the Assassin does not need to spend an action to draw any weapon or item on their person. It still costs an action to draw from a pack. This skill has no levels.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Unobtrusive",
        unlock_condition=lambda c: (
            c.has_adventure_job("Assassin")
            and c.get_adventure_level_by_name("Assassin") >= 1
        ),
        effect_generator=unobtrusive_effects,
        duration="Passive Constant",
        description="This skill allows an Assassin to blend in with a crowd, reducing the chance that their motives or presence will be questioned, or possibly even being noticed. This provides a bonus equalt to its level to Charisma when applicable.",
        is_passive=True,
        is_skill=False,
    )
