from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, create_item, scaled_derived_buff, skill_check
from domain.conditions import IS_ALLY
from domain.effects.base import CONTEXT_OPTIONS

SEWING_DIFFICULTIES = {
    "common": 100,
    "uncommon": 200,
    "rare": 300,
}

build_job("Tailor", [

    # Sewing
    {
        "name": "Sewing",
        "required_level": 1,
        "type": "skill",
        "description": "You spend thirty seconds and an amount of ingredients equal to half the cost of the clothing you wish to create. This is a Intelligence plus Sewing skill check against the difficulty of the item. Common, uncommon, and rare items have a difficulty of 100, 200, and 300 respectively.",
        "effects": lambda ctx: [
            skill_check(
                ability="Sewing",
                stat="intelligence",
                difficulty=lambda ctx, target: SEWING_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE)],
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

])
