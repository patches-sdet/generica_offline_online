from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import DifficultyTable, create_item, scaled_derived_buff, skill_check
from domain.conditions.entity import IS_FOOD
from domain.effects.base import CONTEXT_OPTIONS

FOOD_DIFFICULTIES = DifficultyTable({
    "common": 100,
    "uncommon": 200,
    "rare": 300,
})

FOOD_COSTS = {
    "common": 1,
    "uncommon": 10,
    "rare": 30,
}

build_job("Carpenter", [

    # Level 1
    {
        "name": "Sniff",
        "cost": 5,
        "cost_pool": "fortune",
        "description": "By taking a bif whiff of food or drink, you can determine if it's healthy, unhealthy, poisoned, spoiled, or otherwise dangerous. This skill requires no roll and has no levels.",
        "effects": [], # This just kinda works.
        "is_passive": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": False,
        "type": "skill",
    },

    # Cooking
    {
        "name": "Cooking",
        "description": "You spend thirty seconds and an amount of ingredients equal to half the cost of the food item you wish to create. This is a Wisdom plus Cooking skill check against the difficulty of the item. Common, uncommon, and rare items have a difficulty of 100, 200, and 300 respectively.",
        "effects": skill_check(
                ability="Cooking",
                stat="wisdom",
                difficulty=lambda ctx: FOOD_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE)],
                on_success=[
                    create_item(
                        factory_fn=lambda item_ctx, target: create_item(
                            caster=item_ctx.source,
                            target=target,
                            product_type=item_ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE),
                        ),
                    ),
                ],
            ),
        "is_passive": False,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "type": "skill",
    },

    # Level 5
    {
        "name": "Freshen",
        "cost": 10,
        "cost_pool": "fortune",
        "description": "You have a chance of removing any rot and reversing any decay or spoilage on a particular ingredient or foodstuff. This is a Luck plus your level in this skill roll. The difficulty is determined by the rarity of the item being purified - 120 for something recently gone bad, 180 for something a week to a month old, and 250 for anything older up to one year old.",
        "effects": skill_check(
                ability="Freshen",
                stat="luck",
                difficulty=lambda ctx: FOOD_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.TARGET_FOOD_AGE)],
                on_success=[
                    scaled_derived_buff(
                        scale_fn=lambda ctx: -ctx.ability_levels.get("Freshen", 0),
                        stat="freshness",
                        condition=IS_FOOD,
                    )
                ],
            ),
        "is_passive": False,
        "is_skill": True,
        "required_level": 5,
        "scales_with_level": True,
        "type": "skill",
    },

    {
        "name": "Banquet",
        "cost": 25,
        "cost_pool": "fortune",
        "description": "You can prepare a feast for a crowd rather than just individuals. Target a dish you've just finished and make a Perception plus Banquet roll. For every increment of 25 within your roll, the dish will feed one additional person.",
        "duration": "Permanent",
        "effects": skill_check(
                ability="Banquet",
                stat="perception",
                difficulty=100,
                on_success=[], # TODO: Some kind of way to track how a dish can be multiplied like the skill is asking for.
            ),
        "is_passive": False,
        "is_skill": True,
        "required_level": 10,
        "scales_with_level": True,
        "type": "skill",
    },

    {
        "name": "Leftovers",
        "cost": 50,
        "cost_pool": "fortune",
        "description": "You can create a 'doggy bag' from a meal you or an ally has just finished. You have a number of hours to eat this meal equal to your Cook level.",
        "duration": lambda ctx: f"{ctx.source.get_progression_level("Professions", "Cook")} hours",
        "effects": create_item(
                    factory_fn=lambda item_ctx, target: create_item(
                        caster=item_ctx.source,
                        target=target,
                        product_type=item_ctx.require_option(CONTEXT_OPTIONS.TARGET_WOOD_TYPE),
                        ),
                    ),
        "is_passive": False,
        "is_skill": True,
        "required_level": 20,
        "scales_with_level": True,
        "type": "skill",
        }
],
source_type="profession",
)
