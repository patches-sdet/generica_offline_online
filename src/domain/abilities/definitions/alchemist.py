from abilities import make_ability
from patterns import (
    create_item,
    damage,
    inspect,
    on_success,
    skill_check,
)

from domain.conditions import (
    IS_ENEMY,
    IS_MATERIAL,
)

# Analyze — Inspect / Learn Properties

def analyze_execute(caster, targets):
    return [
        skill_check(
            skill="Analyze",
            difficulty=lambda ctr, target: target.difficulty,
            on_success=inspect(
                reveal_fn=lambda caster, target:{
                "properties": getattr(target, "properties", None),
                "rarity": getattr(target, "rarity", None),
                "alchemy_value": estimate_alchemy_value(target),
                },
            ),
        ),
    ]

# Bomb — AoE Damage

def bomb_execute(caster, targets):
    return [
        damage(
            scale_fn=lambda c: c.get_adventure_level_by_name("Alchemist"),
            condition=IS_ENEMY,
        )
        # NOTE:
        # AoE is implied by targeting system (targets passed in)
        # Later: add explicit radius/area pattern if needed
    ]

# Distill — Craft Reagents / Crystals

def distill_execute(caster, targets):
    return [
        skill_check(
            skill="Distill",
            difficulty=lambda ctx, target: target.difficulty,
            on_success=create_item(
                factory_fn=lambda caster, target: create_distilled_material(
                    caster, target
                )
            ),
        )
    ]

# Healing Potion — Craft Healing Items

def healing_potion_execute(caster, targets):
    return [
        on_success(
            success_condition=lambda ctx, target: (
                ctx.source.roll_intelligence("Healing Potion") >= 100
            ),
            effect=create_item(
                factory_fn=lambda caster, target: create_healing_potion(
                    caster=caster,
                    tier=determine_potion_tier(caster, "Healing Potion")
                )
            ),
        )
    ]

# Mana Potion — Craft Mana Items

def mana_potion_execute(caster, targets):
    return [
        on_success(
            success_condition=lambda ctx, target: (
                ctx.source.roll_intelligence("Mana Potion") >= 100
            ),
            effect=create_item(
                factory_fn=lambda caster, target: create_mana_potion(
                    caster=caster,
                    tier=determine_potion_tier(caster, "Mana Potion")
                )
            ),
        )
    ]

# Registration

def register():

    make_ability(
        name="Analyze",
        unlock_condition=lambda c: (
            c.has_adventure_job("Alchemist")
            and c.get_adventure_level_by_name("Alchemist") >= 1
        ),
        execute=analyze_execute,
        cost=5,
        cost_pool="sanity",
        duration="10 seconds",
        description="An Alchemist can use this skill to determine the properties of any liquid, powder, crystal, or reagent they study. This is an Intelligence plus Analyze skill roll against the difficulty of the substance. \n     Failure means the Alchemist learns nothing from their study for that day.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Bomb",
        unlock_condition=lambda c: (
            c.has_adventure_job("Alchemist")
            and c.get_adventure_level_by_name("Alchemist") >= 1
        ),
        execute=bomb_execute,
        cost=10,
        cost_pool="stamina",
        duration="1 attack",
        description="The Alchemist pulls out some volatile vials and mixes them together before throwing it at an enemy. This is a ranged attack with a Dexterity plus Bomb skill roll, using the target's Agility as the difficulty\n     number. The Bomb's damage is equal to your Alchemist level, and does damage all enemies within ten feet of the target.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Distill",
        unlock_condition=lambda c: (
            c.has_adventure_job("Alchemist")
            and c.get_adventure_level_by_name("Alchemist") >= 1
        ),
        execute=distill_execute,
        cost=10,
        cost_pool="sanity",
        duration="Permanent",
        description="This allows an Alchemist to turn valuable substances into red reagents and level 1 crystals. It takes 50 silver worth of components to create a reagent, and 100 silver to create a crystal. This is an Intelligence\n     plus Distill skill roll. The components are consumed regardless of success. Red reagents have a difficulty of 80, and level one crystals have a difficulty of 120. An Alchemist may use more components (in silver) to gain a boost\n     to this skill on a one for one basis.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Healing Potion",
        unlock_condition=lambda c: (
            c.has_adventure_job("Alchemist")
            and c.get_adventure_level_by_name("Alchemist") >= 1
        ),
        execute=healing_potion_execute,
        cost=20,
        cost_pool="sanity",
        duration="Permanent",
        description="This allows an Alchemist to create one vial of a basic healing potion. This requires an Intelligence plus Healing Potion skill roll (along with 1 Red Reagent) with a Difficulty of 100. A potent healing potion\n     can be created with the same roll (but 1 orange reagent) with a Difficulty of 200. A greater healing potion can be created with a Difficulty of 300 (and a yellow reagent). A Critical success results in double potions created.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Mana Potion",
        unlock_condition=lambda c: (
            c.has_adventure_job("Alchemist")
            and c.get_adventure_level_by_name("Alchemist") >= 1
        ),
        execute=mana_potion_execute,
        cost=20,
        cost_pool="sanity",
        duration="Permanent",
        description="This allows an Alchemist to create one vial of a basic mana potion. This requires an Intelligence plus Mana Potion skill roll (along with 1 Red Reagent) with a Difficulty of 100. A potent mana potion\n     can be created with the same roll (but 1 orange reagent) with a Difficulty of 200. A greater mana potion can be created with a Difficulty of 300 (and a yellow reagent). A Critical success results in double potions created.",
        is_passive=False,
        is_skill=True,
    )
