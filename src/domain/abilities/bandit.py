from domain.abilities import make_ability
from domain.runtime import spend

def register():

    # Level 1

    make_ability(
        name="Ambush",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Bandit")
            and c.get_adventure_level_by_name("Bandit") >= 1
        ),
        cost = 10,
        cost_pool = "stamina",
        duration = "1 turn",
        description = "After a successful stealth roll, the Bandit may call an Ambush, and every 'Bastard' or party member gains a bonus to their attack roll equal to the level of this skill.\n     This is a buff.",
    )

    make_ability(
        name="Band O' Bastards",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Bandit")
            and c.get_adventure_level_by_name("Bandit") >= 1
        ),
        cost = 10,
        cost_pool = "sanity",
        duration = "1 day",
        description = "The Bandit may choose any number of creatures to become a part of his Band O' Bastards. If the creatures chosen have a job level higher than the Bandit, they cannot benefit from this skill. Bastards gain a buff to their Hit Points equal to thelevel of this skill.\n     Being a Bastard also allows other Bandit buffs to apply."
    )

    make_ability(
        name="Keep the Boys in Line",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Bandit")
            and c.get_adventure_level_by_name("Bandit") >= 1
        ),
        cost = 10,
        cost_pool = "sanity",
        duration = "Passive Constant",
        description = "If any creature designated as a Bastard that wishes to attempt treachery against their Bandit must make a Willpower roll with the Bandit's Strength as the difficulty class. A failed roll results in the Bastard suffering Moxie damage equal to the level of this skill."
    )

    make_ability(
        name="Lay of the Land",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Bandit")
            and c.get_adventure_level_by_name("Bandit") >= 1
        ),
        cost = 5,
        cost_pool = "stamina",
        duration = "1 minute",
        description = "The Bandit can examine a site to determine if it can be used for an ambush. The Bandit can then make a Perception plus Lay of the Land roll against a difficulty set by the GM.",
    )

    make_ability(
        name="Subdue",
        unlock_condition=lambda c: (
        c.has_adventure_job ("Bandit")
        and c.get_adventure_level_by_name("Bandit") >= 1
        ),
        cost = 5,
        cost_pool = "stamina",
        duration = "1 turn/level",
        description = "The Bandit can convert their lethal damage to nonlethal, dealing stamina damage instead of HP without any penalties.",
        )
