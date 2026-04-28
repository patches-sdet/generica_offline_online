from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import create_item, skill_check, heal_hp, apply_state
from domain.effects.base import CONTEXT_OPTIONS
from domain.conditions import IS_ALLY

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

    {
        "name": "Dirtbuster",
        "cost": 5,
        "cost_pool": "stamina",
        "description": "Activate this skill to double the length of any furrow you just ploughed. This skill has no levels.",
        "duration": "1 Action",
        "effects": [],
        "required_level": 1,
        "scales_with_level": False,
        "type": "skill",
    },

    {
        "name": "Heal Beast",
        "cost": 20,
        "cost_pool": "sanity",
        "description": "Instantly heal a beast that you're touching, restoring HP equal to your Wisdom plus the level of this skill.",
        "duration": "1 Action",
        "effects": heal_hp(
                scale_fn=lambda c: (
                    c.attributes.get("wisdom")
                    + c.get_ability_effective_level("Heal Beast", 0)
                ),
                condition=IS_ALLY,
            ),
            "required_level": 5,
            "scales_with_level": True,
            "type": "skill",
    },

    {
        "name": "Almanac",
        "description": "Once a year, starting the morning after you hit level 10, you will find a copy of a mysterious book known only as 'The Almanac' on your doorstep, or to the closest equivalent. This book grants a bonus equal to your Farmer level to all farming-relating tasks while it is on your person.",
        # The effect also includes granting the 'Call Winds' ability from Shaman, equal to the Farmer's level, but it consumes the Almanac if used
        "duration": "Passive Constant",
        "effects": [],
        "required_level": 10,
        "scales_with_level": False,
        "type": "passive",
    },

    {
        "name": "Bugbane",
        "cost": 50,
        "cost_pool": "fortune",
        "description": "You verminproof an acre of land which drives away harmful insects without damaging beneficial ones. Any bugs considered harmful must succeed a Constitution roll against your Wisdom plus Bugbane skill level. Failure results in the bug taking damage equal to your Farmer level every turn, ignoring defenses",
        "duration": "1 day/Farmer level",
        "effects": [],
        "required_level": 20,
        "scales_with_level": True,
        "type": "skill",
    }
],
source_type="profession",
)