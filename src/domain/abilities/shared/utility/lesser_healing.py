from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import heal_hp
from domain.conditions.combat import IS_ALLY

LESSER_HEALING = {
        "name": "Lesser Healing",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Instantly heal a living creature within 100 feet for an amount equal to "
            "your Cleric level plus the level of this skill, divided by 2. This skill "
            "is a spell.\n"
            "If used on Undead or Dark-aligned targets, it instead inflicts the same "
            "amount of damage, bypassing defenses and automatically hitting. This skill "
            "is a spell."
        ),
        "duration": "1 Action",
        "effects": lambda ctx: [
            heal_hp(
                scale_fn=lambda c: (
                    c.get_progression_level("adventure", "Cleric", 0)
                    + c.ability_levels.get("Lesser Healing", 0)
                ) // 2,
                condition=IS_ALLY,
            )
            # damaging undead/dark branch still to be added
        ],
        "is_passive": False,
        "is_skill": True,
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "ally or enemy",
        "type": "skill",
    }

build_shared_ability("shared.utility", LESSER_HEALING)