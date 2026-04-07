from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, scaled_derived_buff
from domain.conditions import IS_ALLY

def create_soulstone(level):
    # This is a placeholder implementation.
    return {
        "type": "create_soulstone",
        "level": level,
    }


build_job("Necromancer", [

    {
        "name": "Soulstone",
        "cost": 20,
        "cost_pool": "sanity",
        "description": "You can create a level 1 soulstone crystal, which can house a newly-deceased spirit or an existing incorporeal undead. The spirit can be talked to (with the proper skill), used to create new undead creatures, or released from the stone. While in the soulstone, the spirit has a level equal to your level in this skill dividede by ten, rounded up. The crystal can only be used for enchantment or crafting IF it has a spirit inside. This skill is a spell.",
        "duration": "Permanent",
        "effects": [
                create_soulstone (
                    level=lambda c: (c.ability_levels.get("Soulstone", 0) // 10)
                )
        ],
        "is_passive": False,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

])
