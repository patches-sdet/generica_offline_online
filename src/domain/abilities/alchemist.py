from domain.abilities import make_ability
from domain.runtime import damage, heal, spend

def register():

    make_ability(
            name = "Analyze",
            unlock_condition = lambda c: (
                c.has_adventure_job ("Alchemist")
                and c.get_adventure_level_by_name("Alchemist") >= 1
                ),
            cost = 5,
            cost_pool = "sanity",
            duration = "10 seconds",
            description = "An Alchemist can use this skill to determine the properties of any liquid, powder, crystal, or reagent they study. This is an Intelligence plus Analyze skill roll against the difficulty of the substance. \n     Failure means the Alchemist learns nothing from their study for that day.",
            is_passive = False,
            is_skill = True,
            )

    make_ability(
            name = "Bomb",
            unlock_condition = lambda c: (
                c.has_adventure_job ("Alchemist")
                and c.get_adventure_level_by_name("Alchemist") >= 1
                ),
            cost = 10,
            cost_pool = "stamina",
            duration = "1 attack",
            description = "The Alchemist pulls out some volatile vials and mixes them together before throwing it at an enemy. This is a ranged attack with a Dexterity plus Bomb skill roll, using the target's Agility as the difficulty\n     number. The Bomb's damage is equal to your Alchemist level, and does damage all enemies within ten feet of the target.",
            is_passive = False,
            is_skill = True,
            )

    make_ability(
            name = "Distill",
            unlock_condition = lambda c: (
                c.has_adventure_job ("Alchemist")
                and c.get_adventure_level_by_name("Alchemist") >= 1
                ),
            cost = 10,
            cost_pool = "sanity",
            duration = "Permanent",
            description = "This allows an Alchemist to turn valuable substances into red reagents and level 1 crystals. It takes 50 silver worth of components to create a reagent, and 100 silver to create a crystal. This is an Intelligence\n     plus Distill skill roll. The components are consumed regardless of success. Red reagents have a difficulty of 80, and level one crystals have a difficulty of 120. An Alchemist may use more components (in silver) to gain a boost\n     to this skill on a one for one basis.",
            is_passive = False,
            is_skill = True,
            )

    make_ability(
            name = "Healing Potion",
            unlock_condition = lambda c: (
                c.has_adventure_job ("Alchemist")
                and c.get_adventure_level_by_name("Alchemist") >= 1
                ),
            cost = 20, # and a red reagent
            cost_pool = "sanity",
            duration = "Permanent",
            description = "This allows an Alchemist to create one vial of a basic healing potion. This requires an Intelligence plus Healing Potion skill roll (along with 1 Red Reagent) with a Difficulty of 100. A potent healing potion\n     can be created with the same roll (but 1 orange reagent) with a Difficulty of 200. A greater healing potion can be created with a Difficulty of 300 (and a yellow reagent). A Critical success results in double potions created.",
            is_passive = False,
            is_skill = True,
            )

    make_ability(
            name = "Mana Potion",
            unlock_condition = lambda c: (
                c.has_adventure_job ("Alchemist")
                and c.get_adventure_level_by_name("Alchemist") >= 1
                ),
            cost = 20, # and reagents
            cost_pool = "sanity",
            duration = "Permanent",
            description = "This allows an Alchemist to create one vial of a basic mana potion. This requires an Intelligence plus Mana Potion skill roll (along with 1 Red Reagent) with a Difficulty of 100. A potent mana potion\n     can be created with the same roll (but 1 orange reagent) with a Difficulty of 200. A greater mana potion can be created with a Difficulty of 300 (and a yellow reagent). A Critical success results in double potions created.",
            is_passive = False,
            is_skill = True,
            )
