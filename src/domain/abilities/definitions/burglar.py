from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    buff,
    inspect,
    skill_check,
)
from domain.effects.special.roll import RollModifierEffect


build_job("Burglar", [

    # Case the Joint
    {
        "name": "Case the Joint",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "A Burglar can use this ability to case a location, allowing them to see "
            "the rough security level, and difficulty of any locks or traps. It is a "
            "Perception plus Case the Joint roll.\n"
            "Some example difficulties include:\n"
            "- Simple Location: 80\n"
            "- Merchant House: 120\n"
            "- Large Castle: 180\n"
            "- Multi-floor Dungeon: 250\n"
            "- Legendary Dragon Lair: 400"
        ),
        "duration": "1 Inspection",
        "effects": lambda ctx: [
            inspect(
                reveal_fn=lambda inspect_ctx, target: {
                    "security_level": getattr(target, "security_level", None),
                    "lock_difficulty": getattr(target, "lock_difficulty", None),
                    "trap_difficulty": getattr(target, "trap_difficulty", None),
                }
            )
        ],
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "location",
        "type": "skill",
    },

    # Find Trap
    {
        "name": "Find Trap",
        "cost": 5,
        "cost_pool": "fortune",
        "description": (
            "A Burglar can use this ability to find traps in a location. It is a "
            "Perception plus Find Trap roll, and allows the Burglar to find "
            "traps with a difficulty equal to or less than the roll.\n"
            "Some example difficulties include:\n"
            "- Simple Pitfall: 50\n"
            "- Poison Dart Trap: 100\n"
            "- Explosive Rune: 150\n"
            "- Teleportation Trap: 200\n"
            "- Legendary Mimic: 300"
        ),
        "duration": "1 Minute per Burglar Level",
        "effects": lambda ctx: [
            skill_check(
                ability="Find Trap",
                stat="perception",
                difficulty=lambda check_ctx, target: target.trap_difficulty,
                on_success=[],
            )
        ],
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "location",
        "type": "skill",
    },

    # Locksmith
    {
        "name": "Locksmith",
        "description": (
            "You automatically know the difficulty of any lock you examine, including "
            "magical ones. You can add your Locksmith level to any roll to open a lock. "
            "This is an increase, not a buff."
        ),
        "duration": "Passive Constant",
        "effects": lambda ctx: [
            RollModifierEffect(
                scale_fn=lambda c: c.ability_levels.get("Locksmith", 0),
                source_tag="locksmith",
            )
        ],
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "passive",
    },

    # Lootbag
    {
        "name": "Lootbag",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "You can temporarily enchant a bag or sack to carry one item or set of "
            "identical items per skill level, regardless of weight or size. The item(s) "
            "must be able to fit through the bag's opening. If the bag is destroyed, "
            "the item(s) are dropped in the bag's location."
        ),
        "duration": "1 Hour",
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda c: c.ability_levels.get("Lootbag", 0),
                stats={"strength": 1},
            ),
        ],
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Stealthy Step
    {
        "name": "Stealthy Step",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "You can add your Stealth Step level to all stealth checks. "
            "This is an increase, not a buff."
        ),
        "duration": "1 Minute per Burglar Level",
        "effects": lambda ctx: [
            RollModifierEffect(
                scale_fn=lambda c: c.ability_levels.get("Stealthy Step", 0),
                source_tag="stealthy_step",
            )
        ],
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },
])