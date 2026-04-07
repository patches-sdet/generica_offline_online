from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import DifficultyTable, buff, create_item, skill_check
from domain.effects.base import CONTEXT_OPTIONS

DRINK_DIFFICULTIES = DifficultyTable({
    "common": 100,
    "uncommon": 200,
    "rare": 300,
})

DRINK_COSTS = {
    "common": 1,
    "uncommon": 10,
    "rare": 30,
}

build_job("Brewer", [

    # Passive
    {
        "name": "Alcohol Tolerance",
        "required_level": 1,
        "type": "passive",
        "description": "You have a high tolerance for alcohol, adding your constitution whenever you have to roll against the drunk or hungover condition.",
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda ctx: ctx.source.attributes.constitution,
                stats={"constitution": 1},
                condition=lambda ctx: (
                    ctx.action_type == "condition_resistance_roll"
                    and ctx.metadata.get("condition_name") in {"drunk", "hungover"}
                )
            ),
        ],
    },

    # Brewing
    {
        "name": "Brewing",
        "required_level": 1,
        "type": "skill",
        "target": "self",
        "description": "You spend thirty seconds and an amount of ingredients equal to half the cost of the drink you wish to create. This is a Wisdom plus Brewing skill check against the difficulty of the drink. Common, uncommon, and rare drinks have a difficulty of 100, 200, and 300 respectively.",
        "effects": lambda ctx: [
            skill_check(
                ability="Brewing",
                stat="wisdom",
                difficulty=lambda ctx, target: DRINK_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE)],
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
        "name": "Sommelier",
        "required_level": "5",
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "description": "By spending a turn sniffing a drink or other liquid, you can analyze its nature, learn the name of its creator, and determine the year it was crafted. This skill has no levels.",
        "effects": [], # There's no mechanical effect, it just succeeds
        "is_passive": True,
        "is_skill": True,
    },

    {
        "name": "Mixed Drinks",
        "required_level": 10,
        "type": "skill",
        "cost": 25,
        "cost_pool": "sanity",
        "description": "By spending 30 seconds mixing two liquids together, you can combine any properties and effects they have. This requires a Wisdom check plus your level in this skill against the crafting difficulty of the highest drink used. Failure means both liquids are ruined.",
        "effects": [
            skill_check(
                ability="Mixed Drinks",
                stat="wisdom",
                difficulty=lambda ctx, target: DRINK_DIFFICULTIES[max(
                    ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE_1),
                    ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE_2),
                )],
                on_success=[
                    create_item(
                        factory_fn=lambda item_ctx, target: create_item(
                            caster=item_ctx.source,
                            target=target,
                            product_type=item_ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE_1),
                        ),
                    ),
                    create_item(
                        factory_fn=lambda item_ctx, target: create_item(
                            caster=item_ctx.source,
                            target=target,
                            product_type=item_ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE_2),
                        ),
                    ),
                ],
                on_failure=[
                    create_item(
                        factory_fn=lambda item_ctx, target: create_item(
                            caster=item_ctx.source,
                            target=target,
                            product_type=None,  # Ruined product
                        ),
                    ),
                ],
            )
        ],
        "is_passive": False,
        "is_skill": True,
        "scales_with_level": True,
    },

    {
        "name": "Accelerate Aging",
        "required_level": 20,
        "type": "skill",
        "cost": 50,
        "cost_pool": "sanity",
        "description": "This skill has two effects. First, it fast-ages a liquid, causing it to gain a year's worth of age with every use. Secondly, it will fool anyone using the Sommelier skill.",
        "effects": [], # The aging effect is typically just narrative, but may increase the value of the liquid.
        "is_passive": False,
        "is_skill": True,
        "scales_with_level": False,
    }
])
