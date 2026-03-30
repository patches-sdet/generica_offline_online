from domain.abilities.factory import make_ability
from domain.effects import StatIncrease
from domain.abilities.patterns import buff, heal, scaled_derived_buff
from domain.conditions import IS_ALLY#, IS_ENEMY # leave this here for the damaging version of Lesser Healing, which is still being worked on
from domain.effects.stat_effects import DerivedStatBonus

def blessing_execute(caster, targets):
    return [
        buff(
            scale_fn=lambda c: c.pools.get("fortune", 0),
            stats={"any": 1},  # placeholder until stat selection system exists
            condition=IS_ALLY,
        )
    ]

def faith_effects(character):
    return [
        scaled_derived_buff(
            stat="fate",
            scale_fn=lambda c: c.get_adventure_level_by_name("Cleric", 0),
        )
    ]

def holy_smite_execute(caster, targets):
    return [
        buff(
            scale_fn=lambda c: c.skills.get("Holy Smite", 0),
            stats={"damage": 1},
        )
    ]


def lesser_healing_execute(caster, targets):
    return [
        heal(
            scale_fn=lambda c: (
                c.get_adventure_level_by_name("Cleric", 0)
                + c.skills.get("Lesser Healing", 0)
            ) // 2,
            condition=IS_ALLY,
        )
    ]


def divinity_shield_execute(caster, targets):
    return [
        buff(
            scale_fn=lambda c: c.skills.get("Shield of Divinity", 0),
            stats={"armor": 1},
            condition=IS_ALLY,
        )
    ]

# Registration

def register():

    # Blessing

    make_ability(
        name="Blessing",
        unlock_condition=lambda c: (
            c.has_adventure_job("Cleric")
            and c.get_adventure_level_by_name("Cleric") >= 1
        ),
        execute=blessing_execute,
        cost=1,
        cost_pool="fortune",
        duration="Until Cancelled or Dispelled",
        description="A Cleric can bless someone, spending at least 1 Fortune to increase a single attribute by an equal amount. The Cleric's Fortune remains at this level until they choose to cancel the spell.\n     A creature can only be under the influence of a single blessing at a time. \n     A Cleric can only bestor one blessing at a time. This skill is a spell.",
        is_passive=False,
        is_skill=True,
        target_type="ally",
    )

    # Faith

    make_ability(
        name="Faith",
        unlock_condition=lambda c: (
            c.has_adventure_job("Cleric")
            and c.get_adventure_level_by_name("Cleric") >= 1
        ),
        effect_generator=faith_effects,
        duration="Passive Constant",
        description="Your Fate is increased by your Cleric Level.",
        is_passive=True,
        is_skill=False,
        target_type="self",
    )

    make_ability(
        name="Godspell",    # this is going to be tricky, because there needs to be a sub-selection when you become a Cleric
                            # for your deity of choice, which then assigns the matching Godspell.
                            # Probably should be part of the effect_on_acquire function of the Cleric job
        unlock_condition=lambda c: (
            c.has_adventure_job("Cleric")
            and c.get_adventure_level_by_name("Cleric") >= 1
        ),
        #effect_generator=godspell_effects,
        description="You can access to your chosen deity's Godspell, which is a unique ability that can only be used by Clerics of that deity. Each Godspell is unique and acts as its own skill. It may or may not be a Spell.",
        is_passive=True,
        is_skill=False,
        target_type="self",
    )

    make_ability(
        name="Holy Smite",
        unlock_condition=lambda c: (
            c.has_adventure_job("Cleric")
            and c.get_adventure_level_by_name("Cleric") >= 1
        ),
        execute=holy_smite_execute,
        cost=10,
        cost_pool="fortune",
        duration="1 Minute per level",
        description="Holy Smite increases your melee attack damage by 1 per level of this skill. This skill is a spell.",
        is_passive=False,
        is_skill=True,
        target_type="self",
    )

    make_ability( # this also needs to have a secondary execution that is for damaging undead or dark-aligned targets.
        name="Lesser Healing",
        unlock_condition=lambda c: (
            c.has_adventure_job("Cleric")
            and c.get_adventure_level_by_name("Cleric") >= 1
        ),
        execute=lesser_healing_execute,
        cost=5,
        cost_pool="sanity",
        duration="1 Action",
        description="Instantly heal a living creature within 100 feet for an amount equal to your Cleric level plus the level of this skill, divided by 2. This skill is a spell.\n     If used on Undead or Dark-aligned targets,\n     it instead inflicts the same amount of damage, bypassing defenses and automatically hitting. This skill is a spell.",
        is_passive=False,
        is_skill=True,
        target_type="ally or enemy",
    )

    make_ability(
        name="Shield of Divinity",
        unlock_condition=lambda c: (
            c.has_adventure_job("Cleric")
            and c.get_adventure_level_by_name("Cleric") >= 1
        ),
        execute=divinity_shield_execute,
        cost=5,
        cost_pool="sanity",
        duration="1 Action",
        description="You can buff the armor of a target by an amount equal to the level of this skill. You can only apply this buff to a single target at a time. This skill is a spell.",
        is_passive=False,
        is_skill=True,
        target_type="ally or self",
    )
