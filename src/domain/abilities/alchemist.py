from domain.abilities import make_ability

def register():

    make_ability(
            name = "Analyze",
            unlock_condition = lambda c: (
                c.has_adventure_job ("Alchemist")
                and c.get_adventure_level_by_name("Alchemist") >= 1
                ),
            )

    make_ability(
            name = "Bomb",
            unlock_condition = lambda c: (
                c.has_adventure_job ("Alchemist")
                and c.get_adventure_level_by_name("Alchemist") >= 1
                ),
            )

    make_ability(
            name = "Distill",
            unlock_condition = lambda c: (
                c.has_adventure_job ("Alchemist")
                and c.get_adventure_level_by_name("Alchemist") >= 1
                ),
            )

    make_ability(
            name = "Healing Potion",
            unlock_condition = lambda c: (
                c.has_adventure_job ("Alchemist")
                and c.get_adventure_level_by_name("Alchemist") >= 1
                ),
            )

    make_ability(
            name = "Mana Potion",
            unlock_condition = lambda c: (
                c.has_adventure_job ("Alchemist")
                and c.get_adventure_level_by_name("Alchemist") >= 1
                ),
            )
