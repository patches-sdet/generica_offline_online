from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import create_item, skill_check
from domain.effects.base import CONTEXT_OPTIONS

build_job("Herbalist", [

    # Gathering
    {
        "name": "Gathering",
        "description": "You spend thirty seconds and an amount of ingredients equal to half the cost of the food item you wish to create. This is a Wisdom plus Gathering skill check against the difficulty of the item. Common, uncommon, and rare items have a difficulty of 100, 200, and 300 respectively.",
        "effects": skill_check(
                ability="Gathering",
                stat="wisdom",
                difficulty=100,
                on_success=[
                    create_item(
                        factory_fn=lambda item_ctx, target: create_item(
                            caster=item_ctx.source,
                            target=target,
                            product_type=item_ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE), # TODO: This needs to be updated when herbs are added to the equipment/items
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

],
source_type="profession",
)