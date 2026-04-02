from domain.abilities.definitions._job_builder import build_job
from domain.abilities.patterns import (
    buff,
    create_item,
    inspect,
    skill_check,
    summon,
)
from domain.effects.base import CONTEXT_OPTIONS

build_job("Conjuror", [

    # Conjuror's Eye
    {
        "name": "Conjuror's Eye",
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "1 minute",
        "description": (
            "You may examine the status of any arcane creature you look upon. This is "
            "an Intelligence skill check plus the level of this skill against a "
            "difficulty equal to the target's Willpower roll.\n"
            "On a success, you learn the target's type, current HP, attributes, jobs, "
            "and their levels. This skill is a spell."
        ),
        "target": "self",
        "effects": lambda ctx: [
            skill_check(
                ability="Conjuror's Eye",
                stat="intelligence",
                difficulty=lambda check_ctx, target: target.roll_willpower(),
                on_success=[
                    inspect(
                        reveal_fn=lambda inspect_ctx, target: {
                            "type": getattr(target, "type", None),
                            "hp": getattr(target, "hp", None),
                            "attributes": getattr(target, "attributes", None),
                            "adventure_jobs": getattr(target, "adventure_jobs", None),
                            "adventure_levels": getattr(target, "adventure_levels", None),
                            "profession_jobs": getattr(target, "profession_jobs", None),
                            "profession_levels": getattr(target, "profession_levels", None),
                        },
                    )
                ],
            )
        ],
    },

    # Dimensional Pocket
    {
        "name": "Dimensional Pocket",
        "type": "skill",
        "cost": 20,
        "cost_pool": "sanity",
        "duration": "1 Day",
        "description": (
            "You can turn anything with at least one pocket into a dimensional storage "
            "space. This allows you to store an item or identical collection of items "
            "equal to your level in this skill. This skill is a spell."
        ),
        "target": "self",
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda c: c.ability_levels.get("Dimensional Pocket", 0),
                stats={"capacity": 1},  # TODO: placeholder until container/inventory support exists
            ),
        ],
    },

    # Handy Creation
    {
        "name": "Handy Creation",
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "1 minute per level",
        "description": (
            "You can create a rough object out of common materials. It cannot exceed "
            "3 feet in any dimension and cannot be a dedicated crafting tool. It cannot "
            "weigh more than an amount equal to your Conjuror level in pounds. "
            "This skill is a spell."
        ),
        "target": "self",
        "effects": lambda ctx: [
            create_item(
                factory_fn=lambda item_ctx, target: {
                    "name": "Rough Object",
                    "description": "A summoned object of common materials.",
                    "weight_limit": item_ctx.source.get_progression_level("adventure", "Conjuror", 0),
                    ctx.metadata[CONTEXT_OPTIONS.CHOSEN_ITEM]: True,  # TODO: placeholder until item creation support exists
                }
            )
        ],
    },

    # Magic Snack
    {
        "name": "Magic Snack",
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "duration": "1 Meal",
        "description": (
            "Magic Snack provides a quick, bland but nourishing snack that is filling "
            "for anyone who eats it. This skill has no levels. This skill is a spell."
        ),
        "target": "self or ally",
        "effects": lambda ctx: [
            create_item(
                factory_fn=lambda item_ctx, target: {
                    "name": "Magic Snack",
                    "effect": "restores hunger",
                }
            )
        ],
        "scales_with_level": False,
    },

    # Summon Least
    {
        "name": "Summon Least",
        "type": "skill",
        "cost": 5,
        "cost_pool": "moxie",
        "duration": "15 minutes*",
        "description": (
            "You can call forth a lesser Arcane being. Typically a Class One creature "
            "of the Daemon, Djinn, Elemental, Manabeast, or Old One type. This is a "
            "Charisma plus the level of this skill against a difficulty of 100.\n"
            "For every fraction of twenty above the difficulty, the summoned creature "
            "will remain for one minute.\n"
            "The creature's level is equal to your Conjuror level, and its skill levels "
            "are equal to your level in this skill.\n"
            "This skill is a spell."
        ),
        "target": "self",
        "effects": lambda ctx: [
            skill_check(
                ability="Summon Least",
                stat="charisma",
                difficulty=100,
                on_success=[
                    summon(
                        factory_fn=lambda summon_ctx, target: {
                            "name": "Lesser Conjuration",
                            "type": "Arcane Creature",
                            "level": summon_ctx.source.get_progression_level("adventure", "Conjuror", 0),
                            "skill_level": summon_ctx.source.ability_levels.get("Summon Least", 0),
                            # TODO: duration from success margin
                        }
                    )
                ],
            )
        ],
    },

])