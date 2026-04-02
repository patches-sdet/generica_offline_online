from domain.abilities.definitions._job_builder import build_job
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
        "type": "skill",
        "cost": 10,
        "cost_pool": "fortune",
        "duration": "1 Inspection",
        "description": (
            "A Burglar can use this ability to case a location, allowing them to see "
            "the rough security level, and difficulty of any locks or traps. It is a "
            "Perception plus the level of this skill.\n"
            "Some example difficulties include:\n"
            "- Simple Location: 80\n"
            "- Merchant House: 120\n"
            "- Large Castle: 180\n"
            "- Multi-floor Dungeon: 250\n"
            "- Legendary Dragon Lair: 400"
        ),
        "effects": lambda ctx: [
            inspect(
                reveal_fn=lambda inspect_ctx, target: {
                    "security_level": getattr(target, "security_level", None),
                    "lock_difficulty": getattr(target, "lock_difficulty", None),
                    "trap_difficulty": getattr(target, "trap_difficulty", None),
                }
            )
        ],
    },

    # Find Trap
    {
        "name": "Find Trap",
        "type": "skill",
        "cost": 5,
        "cost_pool": "fortune",
        "duration": "1 Minute per Burglar Level",
        "description": (
            "A Burglar can use this ability to find traps in a location. It is a "
            "Perception plus the level of this skill, and allows the Burglar to find "
            "traps with a difficulty equal to or less than the roll.\n"
            "Some example difficulties include:\n"
            "- Simple Pitfall: 50\n"
            "- Poison Dart Trap: 100\n"
            "- Explosive Rune: 150\n"
            "- Teleportation Trap: 200\n"
            "- Legendary Mimic: 300"
        ),
        "effects": lambda ctx: [
            skill_check(
                ability="Find Trap",
                stat="perception",
                difficulty=lambda check_ctx, target: target.trap_difficulty,
                on_success=[],
            )
        ],
    },

    # Locksmith
    {
        "name": "Locksmith",
        "type": "passive",
        "duration": "Passive Constant",
        "description": (
            "You automatically know the difficulty of any lock you examine, including "
            "magical ones. You can add your Locksmith level to any roll to open a lock. "
            "This is an increase, not a buff."
        ),
        "effects": lambda ctx: [
            RollModifierEffect(
                scale_fn=lambda c: c.ability_levels.get("Locksmith", 0),
                source_tag="locksmith",
            )
        ],
    },

    # Lootbag
    {
        "name": "Lootbag",
        "type": "skill",
        "cost": 10,
        "cost_pool": "fortune",
        "duration": "1 Hour",
        "description": (
            "You can temporarily enchant a bag or sack to carry one item or set of "
            "identical items per skill level, regardless of weight or size. The item(s) "
            "must be able to fit through the bag's opening. If the bag is destroyed, "
            "the item(s) are dropped in the bag's location."
        ),
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda c: c.ability_levels.get("Lootbag", 0),
                stats={"strength": 1},
            ),
        ],
    },

    # Stealthy Step
    {
        "name": "Stealthy Step",
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "duration": "1 Minute per Burglar Level",
        "description": (
            "You can add your Stealth Step level to all stealth checks. "
            "This is an increase, not a buff."
        ),
        "target": "self",
        "effects": lambda ctx: [
            RollModifierEffect(
                scale_fn=lambda c: c.ability_levels.get("Stealthy Step", 0),
                source_tag="stealthy_step",
            )
        ],
    },
])