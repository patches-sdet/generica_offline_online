from domain.abilities import make_ability
from domain.runtime import spend

def ricochet_execute(character):
    print("Ricochet Shot activated: Penalities reduced for this attack by {ability_level}")


def register():

    # Level 1

    make_ability(
        name="Aim",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Archer")
            and c.get_adventure_level_by_name("Archer") >= 1
        ),
        cost = 10,
        cost_pool = "fortune",
        duration = "1 turn",
        description = "Improve accuracy for a single attack by the level of this skill.",
    )

    make_ability(
        name="Missile Mastery",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Archer")
            and c.get_adventure_level_by_name("Archer") >= 1
        ),
        description = "When attacking with ranged weapons, Archers may substitute half of their highest ranged weapon skill, instead of the skill they would normally use.\n     The experience roll for this attack uses the skill that this skill replaces. Affected skill groups are Archery, Magic Bolts, Throwing, Guns, and Siege Engines. This skill has no levels."
    )

    make_ability(
        name="Quickdraw",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Archer")
            and c.get_adventure_level_by_name("Archer") >= 1
        ),
        cost = 5,
        cost_pool = "stamina",
        duration = "1 minute",
        description = "After activating this skill, the Archer does not need to spend an action to draw any weapon or item on their person. It still costs an action to draw from a pack. This skill has no levels."
    )

    make_ability(
        name="Rapid Fire",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Archer")
            and c.get_adventure_level_by_name("Archer") >= 1
        ),
        cost = 10,
        cost_pool = "stamina",
        description = "The Archer may make two attacks as part of an attack action, instead of one. All costs must be paid as normal. \n     This skill can only be used once per turn. This skill has no levels."
    )

    make_ability(
        name="Ricochet Shot",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Archer")
            and c.get_adventure_level_by_name("Archer") >= 1
        ),
        cost = 5,
        cost_pool = "fortune",
        duration = "1 attack",
        description = "Bounce a shot off a surface to hit difficult targets. Reduces penalties for these shots by this skill's level.",
        execute=ricochet_execute,
    )
