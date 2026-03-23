from domain.abilities import make_ability
from domain.runtime import spend

def ricochet_execute(character):
    print("Ricochet Shot activated: Penalities reduced for this attack by {ability_level}")


def register():

    # -------------------------
    # AIM (Level 1)
    # -------------------------
    make_ability(
        name="Aim",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Archer"
            and c.adventure_level >= 1
        ),
        description = "Improve accuracy for a single attack by the level of this skill.",
    )

    make_ability(
        name="Ricochet Shot",
        unlock_condition=lambda c: (
            c.adventure_job
            and c.adventure_job.name == "Archer"
            and c.adventure_level >= 1
        ),
        cost = 5,
        cost_pool = "fortune",
        duration = "1 attack",
        description = ("Bounce a shot off a surface to hit difficult targets. ",
        "Reduces penalties for these shots by this skill's level."
        ),
        execute=ricochet_execute,
    )
