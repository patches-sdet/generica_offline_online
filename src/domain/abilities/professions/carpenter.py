from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import DifficultyTable, create_item, skill_check
from domain.effects.base import CONTEXT_OPTIONS

WOOD_DIFFICULTIES = DifficultyTable({
    "common": 100,
    "uncommon": 200,
    "rare": 300,
})

WOOD_COSTS = {
    "common": 1,
    "uncommon": 10,
    "rare": 30,
}

build_job("Carpenter", [

    # Level 1
    {
        "name": "Straighten Wood",
        "required_level": 1,
        "cost": 5,
        "cost_pool": "sanity",
        "type": "skill",
        "description": "You can straighten warped or crooked wood, rendering it suitable to be turned into planks. This skill requires no roll and has no levels.",
        "effects": [],
        "is_passive": True,
        "is_skill": True,
        "scales_with_level": False,
    },

    # Carpentry
    {
        "name": "Carpentry",
        "required_level": 1,
        "type": "skill",
        "description": "You spend thirty seconds and an amount of ingredients equal to half the cost of the wooden item you wish to create. This is a Intelligence plus Carpentry skill check against the difficulty of the item. Common, uncommon, and rare items have a difficulty of 100, 200, and 300 respectively.",
        "effects": lambda ctx: [
            skill_check(
                ability="Carpentry",
                stat="intelligence",
                difficulty=lambda ctx, target: WOOD_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE)],
                on_success=[
                    create_item(
                        factory_fn=lambda item_ctx, target: create_item(
                            caster=item_ctx.source,
                            target=target,
                            product_type=item_ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE),
                        ),
                    ),
                ],
            )
        ],
    },

    # Level 5
    {
        "name": "Timber",
        "required_level": "5",
        "type": "skill",
        "cost": 20,
        "cost_pool": "stamina",
        "description": "You spend thirty seconds chopping at a tree with an axe, and the tree can be instantly felled. This will knock down treants and other treelike or wooden monsters.",
        "effects": [], # There's no mechanical effect, it just succeeds at felling a tree or treelike monster.
        "is_passive": False,
        "is_skill": True,
        "scales_with_level": False,
    },

    {
        "name": "Weatherproofing: Wood",
        "required_level": 10,
        "type": "skill",
        "cost": 30,
        "cost_pool": "sanity",
        "duration": "1 year",
        "description": "By spending five minutes hammering and working on a wooden structure or item meant for outside use, you render it immune to weather-related damage for one year.",
        "effects": [],
        "is_passive": False,
        "is_skill": True,
        "scales_with_level": False,
    },

    {
        "name": "Transmute Wood",
        "required_level": 20,
        "type": "skill",
        "cost": 50,
        "cost_pool": "sanity",
        "description": "By spending thirty seconds polishing a wooden object, you can transform it into a different type of wood. You must know the name and properties of the wood you are transmuting. Certain rare wood types may require an Intelligence roll plus your level in this skill.",
        "effects": [
            skill_check(
                ability="Transmute Wood",
                stat="intelligence",
                difficulty=lambda ctx, target: WOOD_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.TARGET_WOOD_TYPE)],
                on_success=[
                    create_item(
                        factory_fn=lambda item_ctx, target: create_item(
                            caster=item_ctx.source,
                            target=target,
                            product_type=item_ctx.require_option(CONTEXT_OPTIONS.TARGET_WOOD_TYPE),
                        ),
                    ),
                ],
            )
        ],
        "is_passive": False,
        "is_skill": True,
        "scales_with_level": True,
    }
])
