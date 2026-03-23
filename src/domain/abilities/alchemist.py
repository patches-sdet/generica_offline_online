from domain.abilities import make_ability

def register():

    make_ability(
            name = "Analyze",
            unlock_condition = lambda c: (
                c.adventure_job
                and c.adventure_job.name == "Alchemist"
                and c.adventure_level >= 1
                ),
            )

    make_ability(
            name = "Bomb",
            unlock_condition = lambda c: (
                c.adventure_job
                and c.adventure_job.name == "Alchemist"
                and c.adventure_level >= 1
                ),
            )

    make_ability(
            name = "Distill",
            unlock_condition = lambda c: (
                c.adventure_job
                and c.adventure_job.name == "Alchemist"
                and c.adventure_level >= 1
                ),
            )

    make_ability(
            name = "Healing Potion",
            unlock_condition = lambda c: (
                c.adventure_job
                and c.adventure_job.name == "Alchemist"
                and c.adventure_level >= 1
                ),
            )

    make_ability(
            name = "Mana Potion",
            unlock_condition = lambda c: (
                c.adventure_job
                and c.adventure_job.name == "Alchemist"
                and c.adventure_level >= 1
                ),
            )
