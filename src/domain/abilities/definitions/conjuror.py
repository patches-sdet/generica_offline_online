from domain.abilities import make_ability
from domain.effects import StatIncrease
from domain.abilities.patterns import (
    buff,
    conditional_effect,
    create_item,
    heal,
    inspect,
    scaled_stat_buff,
    skill_check,
    summon,
)

from domain.conditions import (
    IS_ALLY,
    IS_ENEMY,
)

# Conjuror's Eye — Inspect / Analyze

def conjuror_eye_execute(caster, targets):
    return [
        skill_check(
            skill="Conjuror's Eye",
            stat="intelligence",
            difficulty=lambda ctx, target: target.roll_willpower(),
        on_success=inspect(
            reveal_fn=lambda target: {
                "type": getattr(target, "type", None),
                "hp": getattr(target, "hp", None),
                "attributes": getattr(target, "attributes", None),
                "adventure_jobs": getattr(target, "adventure_jobs", None),
                "adventure_levels": getattr(target, "adventure_levels", None),
                "profession_jobs": getattr(target, "profession_jobs", None),
                "profession_levels": getattr(target, "profession_levels", None),
            },
            ),
        )
    ]

def dimensional_pocket_execute(caster, targets): # this is going to be really tricky to implement in a way that works with the inventory system, 
    # so for now this is just a placeholder that applies a buff to the character that would need to be checked when they try to pick up or interact with items
    return [
            buff(
                scale_fn=lambda c: c.skills.get("Lootbag", 0),
                stats={
                    "strength": 1,
                },
                target=caster,
            ),
    ]

def handy_creation_execute(character):
    return [
            create_item(
                factory_fn=lambda c: {
                    "name": "Rough Object",
                    "description": "A summoned object of common materials."
                    "weight": f"Maximum {c.get_adventure_level_by_name("Conjuror", 0)} pounds", # this needs to be implemented in a way that allows the player to choose the item type when they use the skill, and then that choice needs to be stored in the item so it can be created correctly  
            )
    ]


def summon_least_execute(caster, targets):
    return [
        skill_check(
            skill="Summon Least",
            stat="charisma",
            difficulty=100,
            on_success=summon(factory_fn=lambda c: {
                "name": "Lesser Conjuration",
                "type": "Daemon, Djinn, Elemental, Manabeast, or Old One",
                "description": "A summoned Class One creature of the chosen type, equal to the Conjuror's level in power. The creature is friendly to the caster and obeys their commands.",
            }),
        )
    ]

# Registration

def register():

    make_ability(
        name="Conjuror's Eye",
        unlock_condition=lambda c: (
            c.has_adventure_job("Conjuror")
            and c.get_adventure_level_by_name("Conjuror") >= 1
        ),
        execute=conjuror_eye_execute,
        cost=5,
        cost_pool="sanity",
        duration="1 minute",
        description="You may examine the status of any arcane creature you look upon. This is an Intelligence skill check plus the level of this skill against a difficulty equal to the target's Willpower roll.\n     On a success, you learn the target's type, current HP, attributes, jobs, and their levels. This skill is a spell.",
        is_passive=False,
        is_skill=True,
        target_type="self",
    )

    make_ability(
        name="Dimensional Pocket",
        unlock_condition=lambda c: (
            c.has_adventure_job("Conjuror")
            and c.get_adventure_level_by_name("Conjuror") >= 1
        ),
        execute=dimensional_pocket_execute,
        cost=20,
        cost_pool="sanity",
        duration="1 Day",
        description="You can turn anything with at least one pocket into a dimensional storage space. This allows you to store an item or identical collection of items equal to your level in this skill. This skill is a spell.",
        is_passive=False,
        is_skill=True,
        target_type="self",
    )

    make_ability(
        name="Handy Creation",
        unlock_condition=lambda c: (
            c.has_adventure_job("Conjuror")
            and c.get_adventure_level_by_name("Conjuror") >= 1
        ),
        execute=handy_creation_execute,
        cost=5,
        cost_pool="sanity",
        duration="1 minute per level",
        description="You can create a rough object out of common materials. It cannot exceed 3 feet in any dimension and cannot be a dedicated crafting tool. It cannot weigh more than an amount equal to your Conjuror level in pounds. This skill is a spell.",
        is_passive=False,
        is_skill=True,
        target_type="self",
    )

    make_ability(
        name="Magic Snack",
        unlock_condition=lambda c: (
            c.has_adventure_job("Conjuror")
            and c.get_adventure_level_by_name("Conjuror") >= 1
        ),
        cost=10,
        cost_pool="sanity",
        duration="1 Meal",
        description="Magic Snack provides a quick, bland but nourishing snack that is filling for anyone who eats it. This skill has no levels. This skill is a spell.",
        is_passive=False,
        is_skill=False,
        target_type="self or ally",
    )

    make_ability(
        name="Summon Least",
        unlock_condition=lambda c: (
            c.has_adventure_job("Conjuror")
            and c.get_adventure_level_by_name("Conjuror") >= 1
        ),
        execute= summon_least_execute,
        cost=5,
        cost_pool="moxie",
        duration="15 minutes*",
        description="You can call forth a lesser Arcane being. Typically a Class One creature of the Daemon, Djinn, Elemental, Manabeast, or Old One type. This is a Charisma plus the level of this skill against a difficulty of 100.\n     For every fraction of twenty above the difficulty, the summoned creature will remain for one minute.\n     The creature's level is equal to your Conjuror level, and its skill levels are equal to your level in this skill.\n     This skill is a spell.",
        is_passive=False,
        is_skill=True,
        target_type="self",
    )

    make_ability(
        name="Shield of Divinity",
        unlock_condition=lambda c: (
            c.has_adventure_job("Conjuror")
            and c.get_adventure_level_by_name("Conjuror") >= 1
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
