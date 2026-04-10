from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import create_item, skill_check
from domain.effects.base import CONTEXT_OPTIONS

CROP_DIFFICULTIES = {
    "common": 100,
    "uncommon": 200,
    "rare": 300,
}

build_job("Farmer", [

   {
        "name": "Farming",
        "description": ("You spend thirty seconds and an amount of ingredients equal to half the cost of the crops you wish to plant, or have two livestock nearby. This is a Wisdom plus Farming skill check against the difficulty of the crops. Common, uncommon, and rare items have a difficulty of 100, 200, and 300 respectively.",
        "Note: This ability is different from other crafting skills in that it does not instantly create the crops, they still must be grown, but now only take a month or two. For livestock, it instantly breeds them, and speeds up the pregnancy to only a couple of months.",
            ),
        "effects": skill_check(
                ability="Farming",
                stat="wisdom",
                difficulty=lambda ctx: CROP_DIFFICULTIES[ctx.require_option(CONTEXT_OPTIONS.PRODUCT_TYPE)],
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

],
source_type="profession",
)