from domain.character import Character
from domain.abilities import make_ability
from domain.runtime import spend, heal, damage
from domain.effects import StatIncrease, MultiStatIncrease

def just_that_cool_execute(self):
    return [StatIncrease(stat=cool, value=c.adventure_level)]

def register():

    # Level 1

    make_ability(
        name="Borrowed Skill 1",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Bard")
            and c.get_adventure_level_by_name("Bard") >= 1
        ),
        description = "A Bard may 'replce' this skill with any other Tier One, level one Adventuring Job skill. Once chosen, it cannot be reset. Godspells and darkspells may NOT be chosen.",
        is_passive = False,
        is_skill = False,
    )

    make_ability(
        name="Distracting Song",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Bard")
            and c.get_adventure_level_by_name("Bard") >= 1
        ),
        cost = 5,
        cost_pool = "moxie",
        duration = "Until Ceased",
        description = "(Costs 5 moxie per minute of use) Bard's are able to use this song to distract their foes. Anyone not in their party within earshot suffers a debuff to their Charisma, Perception, and Willpower \n     equal to the level of this skill.\n     A Bard can only ever have one song active at a time.",
        is_passive = False,
        is_skill = True,
    )

    make_ability(
        name="Heartening Song",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Bard")
            and c.get_adventure_level_by_name("Bard") >= 1
        ),
        cost = 5,
        cost_pool = "moxie",
        duration = "Until Ceased",
        description = "(Costs 5 moxie per minute of use) Bards are able to use this song to strengthen the arm and improve aim. All allies within earshot gain a buff to their attack and Strength rolls equal to the level of this skill. \n     A Bard can only ever have one song active at a time.",
        is_passive = False,
        is_skill = True,
    )

    make_ability(
        name="Just That Cool",
        unlock_condition=lambda c: (
            c.has_adventure_job ("Bard")
            and c.get_adventure_level_by_name("Bard") >= 1
        ),
        duration = "Passive Constant",
        description = "Bards are so cool that they gain a bonus to their Cool equal to their Bard Level. This skill has no levels.",
        execute = just_that_cool_execute(self),
        is_passive = True,
        is_skill = False,
    )

    make_ability(
        name="Rejuvenating Song",
        unlock_condition=lambda c: (
        c.has_adventure_job ("Bard")
        and c.get_adventure_level_by_name("Bard") >= 1
        ),
        cost = 5,
        cost_pool = "moxie",
        duration = "Until Ceased",
        description = "(Costs 5 moxie per minute of use) The Bard can use this song to heal their allies. All allies within earshot can heal hit points and stamine equal to the level of this skill. \n     A Bard can only have one song active at a time.",
        is_passive = False,
        is_skill = True,
        )
