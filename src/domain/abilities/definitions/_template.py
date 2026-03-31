from domain.abilities.factory import make_ability
from domain.abilities.patterns import buff, heal, scaled_derived_buff
from domain.conditions import IS_ALLY

# Constants / Helpers

JOB = "<JobName>"

def level(c):
    return c.get_adventure_level_by_name(JOB, 0)

# PASSIVE ABILITIES

def faith_effects(character):
    return scaled_derived_buff(
        stat="fate",
        scale_fn=lambda c: level(c),
    )(character)  # ALWAYS CALL


make_ability(
    name="Faith",
    unlock_condition=lambda c: (
        c.has_adventure_job(JOB)
        and level(c) >= 1
    ),
    effect_generator=faith_effects,
    duration="Passive Constant",
    description="Your Fate increases with your level.",
    is_passive=True,
    is_skill=False,
    target_type="self",
)

# ACTIVE ABILITIES

def blessing_execute(caster, targets):
    return [
        buff(
            scale_fn=lambda c: c.pools.get("fortune", 0),
            stats={"any": 1},
            condition=IS_ALLY,
        )
    ]


make_ability(
    name="Blessing",
    unlock_condition=lambda c: (
        c.has_adventure_job(JOB)
        and level(c) >= 1
    ),
    execute=blessing_execute,
    cost=1,
    cost_pool="fortune",
    duration="Until Cancelled",
    description="Buff a target using Fortune.",
    is_passive=False,
    is_skill=True,
    target_type="ally",
)


def holy_smite_execute(caster, targets):
    return [
        buff(
            scale_fn=lambda c: c.skills.get("Holy Smite", 0),
            stats={"damage": 1},
        )
    ]


make_ability(
    name="Holy Smite",
    unlock_condition=lambda c: (
        c.has_adventure_job(JOB)
        and level(c) >= 1
    ),
    execute=holy_smite_execute,
    cost=10,
    cost_pool="fortune",
    duration="1 Minute per level",
    description="Increase damage.",
    is_passive=False,
    is_skill=True,
    target_type="self",
)


def lesser_healing_execute(caster, targets):
    return [
        heal(
            scale_fn=lambda c: (
                level(c) + c.skills.get("Lesser Healing", 0)
            ) // 2,
            condition=IS_ALLY,
        )
    ]


make_ability(
    name="Lesser Healing",
    unlock_condition=lambda c: (
        c.has_adventure_job(JOB)
        and level(c) >= 1
    ),
    execute=lesser_healing_execute,
    cost=5,
    cost_pool="sanity",
    duration="1 Action",
    description="Heal based on level + skill.",
    is_passive=False,
    is_skill=True,
    target_type="ally",
)


def divinity_shield_execute(caster, targets):
    return [
        buff(
            scale_fn=lambda c: c.skills.get("Shield of Divinity", 0),
            stats={"armor": 1},
            condition=IS_ALLY,
        )
    ]


make_ability(
    name="Shield of Divinity",
    unlock_condition=lambda c: (
        c.has_adventure_job(JOB)
        and level(c) >= 1
    ),
    execute=divinity_shield_execute,
    cost=5,
    cost_pool="sanity",
    duration="1 Action",
    description="Increase armor.",
    is_passive=False,
    is_skill=True,
    target_type="ally",
)