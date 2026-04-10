from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import create_item, skill_check
from domain.effects.base import CONTEXT_OPTIONS

LEATHER_DIFFICULTIES = {
    "common": 100,
    "uncommon": 200,
    "rare": 300,
}

build_job("Tanner", [

    # Tanning
    {
        "name": "Tanning",
        "required_level": 1,
        "type": "skill",
        "description": "You spend thirty seconds and an amount of ingredients equal to half the cost of the leather you wish to create. This is a Intelligence plus Tanning skill check against the difficulty of the item. Common, uncommon, and rare items have a difficulty of 100, 200, and 300 respectively.",
        "effects":skill_check(
                ability="Tanning",
                stat="intelligence",
                difficulty=lambda ctx: LEATHER_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE)],
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
    },
],
source_type="profession",
)