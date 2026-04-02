from domain.abilities.definitions._job_builder import build_job
from domain.abilities.patterns import create_item, damage, inspect, skill_check
from domain.conditions import IS_ENEMY
from domain.abilities.patterns import DifficultyTable, difficulty_from_table
from domain.effects.base import CONTEXT_OPTIONS

POTION_DIFFICULTIES = DifficultyTable({
    "basic": 100,
    "potent": 200,
    "greater": 300,
})

POTION_REAGENTS = {
    "basic": "red",
    "potent": "orange",
    "greater": "yellow",
}

DISTILL_COSTS = {
    "reagent": 50,
    "crystal": 100,
}

DISTILL_DIFFICULTIES = DifficultyTable({
    "reagent": 80,
    "crystal": 120,
})

build_job("Alchemist", [

    # Analyze
    {
        "name": "Analyze",
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "10 seconds",
        "description": "An Alchemist can use this skill to determine the properties of any liquid, powder, crystal, or reagent they study. This is an Intelligence plus Analyze skill roll against the difficulty of the substance. Failure means the Alchemist learns nothing from their study for that day.",
        "effects": lambda ctx, targets: [
            skill_check(
                ability="Analyze",
                stat="intelligence",
                difficulty=lambda ctx, target: getattr(target, "difficulty", 0),
                on_success=[
                    inspect(
                        reveal_fn=lambda ctx, target: {
                            "properties": getattr(target, "properties", None),
                            "rarity": getattr(target, "rarity", None),
                            "alchemy_value": estimate_alchemy_value(target),
                        }
                    )
                ],
            )
        ],
    },

    # Bomb
    {
        "name": "Bomb",
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "duration": "1 attack",
        "description": "The Alchemist pulls out some volatile vials and mixes them together before throwing it at an enemy. This is a ranged attack with a Dexterity plus Bomb skill roll, using the target's Agility as the difficulty number. The Bomb's damage is equal to your Alchemist level, and does damage all enemies within ten feet of the target.",
        "effects": lambda ctx, targets: [
            skill_check(
                ability="Bomb",
                stat="dexterity",
                difficulty=lambda ctx, target: target.roll_agility()
                if hasattr(target, "roll_agility")
                else getattr(getattr(target, "attributes", None), "agility", 0),
                on_success=[
                    damage(
                        scale_fn=lambda c: c.get_progression_level("adventure", "Alchemist", 0),
                        condition=IS_ENEMY,
                    )
                ],
            )
        ],
    },

    # Distill
    {
        "name": "Distill",
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": "This allows an Alchemist to turn valuable substances into red reagents and level 1 crystals. It takes 50 silver worth of components to create a reagent, and 100 silver to create a crystal. This is an Intelligence plus Distill skill roll. The components are consumed regardless of success. Red reagents have a difficulty of 80, and level one crystals have a difficulty of 120. An Alchemist may use more components (in silver) to gain a boost to this skill on a one for one basis.",
        "effects": lambda ctx: [
            skill_check(
                ability="Distill",
                stat="intelligence",
                difficulty=lambda ctx, target: DISTILL_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE)],
                on_success=[
                    create_item(
                        factory_fn=lambda item_ctx, target: create_distilled_material(
                            caster=item_ctx.source,
                            target=target,
                            product_type=item_ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE),
                        ),
                    ),
                ],
            )
        ],
    },

    # Healing Potion
    {
        "name": "Healing Potion",
        "type": "skill",
        "cost": 20,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": "This allows an Alchemist to create one vial of a basic healing potion. This requires an Intelligence plus Healing Potion skill roll (along with 1 Red Reagent) with a Difficulty of 100. A potent healing potion can be created with the same roll (but 1 orange reagent) with a Difficulty of 200. A greater healing potion can be created with a Difficulty of 300 (and a yellow reagent). A Critical success results in double potions created.",
        "effects": lambda ctx: [
            skill_check(
                ability="Healing Potion",
                stat="intelligence",
                difficulty=lambda ctx, target: POTION_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.TIER)],
                on_success=[
                    create_item(
                        factory_fn=lambda item_ctx, target: create_healing_potion(
                            caster=item_ctx.source,
                            tier=item_ctx.require_option(CONTEXT_OPTIONS.TIER),
                        )
                    )
                ],
            ),
        ],
    },

    # Mana Potion
    {
        "name": "Mana Potion",
        "type": "skill",
        "cost": 20,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description":" This allows an Alchemist to create one vial of a basic mana potion. This requires an Intelligence plus Mana Potion skill roll (along with 1 Red Reagent) with a Difficulty of 100. A potent mana potion can be created with the same roll (but 1 orange reagent) with a Difficulty of 200. A greater mana potion can be created with a Difficulty of 300 (and a yellow reagent). A Critical success results in double potions created.",
        "effects": lambda ctx: [
            skill_check(
                ability="Mana Potion",
                stat="intelligence",
                difficulty=lambda ctx, target: POTION_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.TIER)],
                on_success=[
                    create_item(
                        factory_fn=lambda item_ctx, target: create_mana_potion(
                            caster=item_ctx.source,
                            tier=item_ctx.require_option(CONTEXT_OPTIONS.TIER),
                        )
                    )
                ],
            )
        ],
    },
])