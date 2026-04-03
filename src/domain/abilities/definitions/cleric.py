from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    buff,
    heal,
    scaled_derived_buff,
    modify_next_attack,
)
from domain.conditions import IS_ALLY
from domain.effects import CompositeEffect
from domain.effects.base import CONTEXT_OPTIONS


build_job("Cleric", [

    # Blessing
    {
        "name": "Blessing",
        "type": "skill",
        "cost": 1,
        "cost_pool": "fortune",
        "duration": "Until Cancelled or Dispelled",
        "description": (
            "A Cleric can bless someone, spending at least 1 Fortune to increase a "
            "single attribute by an equal amount. The Cleric's Fortune remains at this "
            "level until they choose to cancel the spell.\n"
            "A creature can only be under the influence of a single blessing at a time.\n"
            "A Cleric can only bestow one blessing at a time. This skill is a spell."
        ),
        "target": "ally",
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda c: c.pools.get("fortune", 0),
                stat=ctx.metadata.get(CONTEXT_OPTIONS.BLESSING_STAT),
                condition=IS_ALLY,
            )
        ],
    },

    # Faith
    {
        "name": "Faith",
        "type": "passive",
        "duration": "Passive Constant",
        "description": "Your Fate is increased by your Cleric Level.",
        "target": "self",
        "effects": lambda ctx: [
            scaled_derived_buff(
                stat="fate",
                scale_fn=lambda c: c.get_progression_level("adventure", "Cleric", 0),
            )
        ],
        "scales_with_level": False,
    },

    # Godspell
    {
        "name": "Godspell",
        "type": "passive",
        "description": (
            "You can access your chosen deity's Godspell, which is a unique ability "
            "that can only be used by Clerics of that deity. Each Godspell is unique "
            "and acts as its own skill. It may or may not be a Spell."
        ),
        "target": "self",
        "effects": lambda ctx: [],
        "scales_with_level": False,
    },

    # Holy Smite
    {
        "name": "Holy Smite",
        "type": "skill",
        "cost": 10,
        "cost_pool": "fortune",
        "duration": "1 Minute per level",
        "description": (
            "Holy Smite increases your melee attack damage by 1 per level of this skill. "
            "This skill is a spell."
        ),
        "target": "self",
        "effects": lambda ctx: [
            modify_next_attack(
                lambda attack_ctx, attack: attack.add_bonus(
                    "damage",
                    attack_ctx.source.ability_levels.get("Holy Smite", 0),
                )
            )
        ],
    },

    # Lesser Healing
    {
        "name": "Lesser Healing",
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "1 Action",
        "description": (
            "Instantly heal a living creature within 100 feet for an amount equal to "
            "your Cleric level plus the level of this skill, divided by 2. This skill "
            "is a spell.\n"
            "If used on Undead or Dark-aligned targets, it instead inflicts the same "
            "amount of damage, bypassing defenses and automatically hitting. This skill "
            "is a spell."
        ),
        "target": "ally or enemy",
        "effects": lambda ctx: [
            heal(
                scale_fn=lambda c: (
                    c.get_progression_level("adventure", "Cleric", 0)
                    + c.ability_levels.get("Lesser Healing", 0)
                ) // 2,
                condition=IS_ALLY,
            )
            # damaging undead/dark branch still to be added
        ],
    },

    # Shield of Divinity
    {
        "name": "Shield of Divinity",
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "1 Action",
        "description": (
            "You can buff the armor of a target by an amount equal to the level of this "
            "skill. You can only apply this buff to a single target at a time. This "
            "skill is a spell."
        ),
        "target": "ally or self",
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda c: c.ability_levels.get("Shield of Divinity", 0),
                stats={"armor": 1},
                condition=IS_ALLY,
            )
        ],
    },

])