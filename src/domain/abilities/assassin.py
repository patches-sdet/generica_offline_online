from domain.abilities import make_ability
from domain.runtime import spend

def register():

    # Level 1

    make_ability(
        name="Backstab",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Assassin")
            and c.get_adventure_level_by_name("Assassin") >= 1
        ),
        cost = 10,
        cost_pool = "stamina",
        duration = "5 minutes",
        description = "Add one point of damage per skill level to any attack made on a surprised or helpless target. At the GM's discretion, the Assassin may be able to add this bonus if they can attack a target's back.",
    )

    make_ability(
        name="Cold Read",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Assassin")
            and c.get_adventure_level_by_name("Assassin") >= 1
        ),
        cost = 5,
        cost_pool = "moxie",
        duration = "1 turn",
        description = "The Assassin can learn how tough the target is comparatively to themself, and if they have any vulnerabilities. This is a Perception plus Cold Read skill roll, resisted by the target's Charisma roll.",
    )

    make_ability(
        name="Fast as Death",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Assassin")
            and c.get_adventure_level_by_name("Assassin") >= 1
        ),
        cost = 10,
        cost_pool = "stamina",
        duration = "1 turn per level",
        description = "For the duration of this skill, the Assassin adds 50 to both their initiative and the distance in feet they can run per action.\n     This is a buff.",
    )

    make_ability(
        name="Quickdraw",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Assassin")
            and c.get_adventure_level_by_name("Assassin") >= 1
        ),
        cost = 5,
        cost_pool = "stamina",
        duration = "1 minute",
        description = "After activating this skill, the Assassin does not need to spend an action to draw any weapon or item on their person. It still costs an action to draw from a pack. This skill has no levels.",
    )

    make_ability(
        name="Unobstrusive",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Assassin")
            and c.get_adventure_level_by_name("Assassin") >= 1
        ),
        cost = 10,
        cost_pool = "moxie",
        duration = "Passive Constant",
        description = "This skill allows an Assassin to blend in with a crowd, reducing the chance that their motives or presence will be questioned, or possibly even being noticed. This provides a bonus equalt to its level to Charisma when applicable.",
    )
