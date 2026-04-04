from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import DifficultyTable, buff, create_item, heal, scaled_derived_buff, skill_check
from domain.conditions import IS_ALLY
from src.domain.effects.base import CONTEXT_OPTIONS

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
        "type": "passive",
        "description": "You have a high tolerance for alcohol, adding your constitution whenever you have to roll against the drunk or hungover condition.",
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda ctx: ctx.source.constitution,
                stats={"constitution": 1},
                condition=lambda ctx: ctx.has_condition("drunk") or ctx.has_condition("hungover"),
            ),
        ],
    },

    # Brewing
    {
        "name": "Brewing",
        "type": "skill",
        "target": "self",
        "description": "You spend thirty seconds and an amount of ingredients equal to half the cost of the drink you wish to create. This is a Wisdom plus Brewing skill check against the difficulty of the drink. Common, uncommon, and rare drinks have a difficulty of 100, 200, and 300 respectively.",
        "effects": lambda ctx: [
            skill_check(
                ability="Brewing",
                stat="intelligence",
                difficulty=lambda ctx, target: DRINK_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE)],
                on_success=[
                    create_item(
                        factory_fn=lambda item_ctx, target: create_drink(
                            caster=item_ctx.source,
                            target=target,
                            product_type=item_ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE),
                        ),
                    ),
                ],
            )
        ],
    },
])
