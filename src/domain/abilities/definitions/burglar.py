from domain.abilities import make_ability
from domain.abilities.patterns import (
    buff,
    conditional_effect,
    inspect,

    
)

from domain.conditions import (
    IS_ALLY,
    IS_ENEMY,
)

# Passive — Just That Cool

def case_the_joint_execute(character):
    return [
        inspect(
            scale_fn=lambda c: c.get_adventure_level_by_name("Burglar"),
            stats={"cool": 1},
        )
    ]

# Songs (Auras)

def find_trap_execute(caster, targets):
    return [
        inspect(
            scale_fn=lambda c: c.skills.get("Find Trap", 0),
            stats={
                "perception": {caster.skills.get("Find Trap", 0)},  # this needs to be a roll that can be compared to trap difficulties
            },
        )
    ]

def locksmith_effects(character):
    return [
        buff(
            scale_fn=lambda c: 
                 c.ability_levels.get("Locksmith", 0), 
                 stats={
                     skill_check_bonus: (scale_fn: lambda c: c.ability_levels.get("Locksmith", 0)) {character.skills.get("Lockpicking", 0): {character.ability_levels.get("Locksmith", 0)}}})]


def lootbag_execute(caster, targets): # this is going to be really tricky to implement in a way that works with the inventory system, 
    # so for now this is just a placeholder that applies a buff to the character that would need to be checked when they try to pick up or interact with items
    return [
            buff(
                scale_fn=lambda c: c.skills.get("Lootbag", 0),
                stats={
                    "strength": 1,
                },
                target=caster,
            ),
    ]


def stealthy_step_execute(caster, targets):
    return [
            conditional_effect(
                scale_fn=lambda c: c.skills.get("Stealthy Step", 0),
                effect=buff(
                    stats={
                        "stealth": {caster.skills.get("Stealthy Step", 0)}, # this needs to be applied to all stealth checks, not just a single stat
                    },
                    target=caster,
                ),
                condition=IS_ALLY,
            ),
    ]

# Registration

def register():

    # Case the Joint

    make_ability(
        name="Case the Joint",
        unlock_condition=lambda c: (
            c.has_adventure_job("Burglar")
            and c.get_adventure_level_by_name("Burglar") >= 1
        ),
        execute=case_the_joint_execute,
        cost=10,
        cost_pool="fortune",
        duration="1 Inspection",
        description="A Burglar can use this ability to case a location, allowing them to see the rough security level, and difficulty of any locks or traps. It is a Perception plus the level of this skill.\n     Some example difficulties include:\n     - Simple Location: 80\n     - Merchant House: 120\n     - Large Castle: 180\n     - Multi-floor Dungeon: 250\n     - Legendary Dragon Lair: 400",
        is_passive=False,
        is_skill=True,
    )

    # Find Trap

    make_ability(
        name="Find Trap",
        unlock_condition=lambda c: (
            c.has_adventure_job("Burglar")
            and c.get_adventure_level_by_name("Burglar") >= 1
        ),
        execute=find_trap_execute,
        cost=5,
        cost_pool="fortune",
        duration="1 Minute per Burglar Level",
        description="A Burglar can use this ability to find traps in a location. It is a Perception plus the level of this skill, and allows the Burglar to find traps with a difficulty equal to or less than the roll.\n     Some example difficulties include:\n     - Simple Pitfall: 50\n     - Poison Dart Trap: 100\n     - Explosive Rune: 150\n     - Teleportation Trap: 200\n     - Legendary Mimic: 300",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Locksmith",
        unlock_condition=lambda c: (
            c.has_adventure_job("Burglar")
            and c.get_adventure_level_by_name("Burglar") >= 1
        ),
        effect_generator=locksmith_effects,
        duration="Passive Constant",
        description="You automatically know the difficulty of any lock you examine, including magical ones. You can add your Locksmith level to any roll to open a lock. This is an increase, not a buff.",
        is_passive=True,
        is_skill=True,
    )

    make_ability(
        name="Lootbag",
        unlock_condition=lambda c: (
            c.has_adventure_job("Burglar")
            and c.get_adventure_level_by_name("Burglar") >= 1
        ),
        execute=lootbag_execute,
        cost=10,
        cost_pool="fortune",
        duration="1 Hour",
        duration="Passive Constant",
        description="You can temporarily enchant a bag or sack to carry one item or set of identical items per skill level, regardless of weight or size. The item(s) must be able to fit through the bag's opening. If the bag is destroyed, the item(s) are dropped in the bag's location.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Stealthy Step",
        unlock_condition=lambda c: (
            c.has_adventure_job("Burglar")
            and c.get_adventure_level_by_name("Burglar") >= 1
        ),
        execute=stealthy_step_execute,
        cost=10,
        cost_pool="stamina",
        duration="1 Minute per Burglar Level",
        description="You can add your Stealth Step level to all stealth checks. This is an increase, not a buff.",
        is_passive=False,
        is_skill=True,
        target_type="self"
    )
