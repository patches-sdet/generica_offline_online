from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import create_item, skill_check
from domain.effects.base import CONTEXT_OPTIONS

ORE_DIFFICULTIES = {
    "common": 100,
    "uncommon": 200,
    "rare": 300,
}

build_job("Miner", [

    # Mining
    {
        "name": "Mining",
        "required_level": 1,
        "type": "skill",
        "description": "You spend thirty seconds digging in an area that contains ore and gather metal or stone components. This requires one crate costing 5 copper for each attempt, and produces metal or stone worth a number of copper equal to your Strength plus Mining skill roll divided by 10, rounded down.",
        "effects": skill_check(
                ability="Mining",
                stat="strength",
                difficulty=100,  # Simplified difficulty for mining
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