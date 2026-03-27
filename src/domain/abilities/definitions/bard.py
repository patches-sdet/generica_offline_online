from domain.abilities import make_ability
from domain.abilities.patterns import (
    buff,
    debuff,
    heal,
    aura,
)

from domain.conditions import (
    IS_ALLY,
    IS_ENEMY,
)

# =========================================================
# Passive — Just That Cool
# =========================================================

def just_that_cool_effects(character):
    return [
        buff(
            scale_fn=lambda c: c.get_adventure_level_by_name("Bard"),
            stats={"cool": 1},
        )
    ]


# =========================================================
# Songs (Auras)
# =========================================================

def distracting_song_execute(caster, targets):
    return [
        aura(
            debuff(
                scale_fn=lambda c: c.skills.get("Distracting Song", 0),
                stats={
                    "charisma": -1,
                    "perception": -1,
                    "willpower": -1,
                },
                condition=IS_ENEMY,
            ),
            aura_id="bard_song",
        )
    ]


def heartening_song_execute(caster, targets):
    return [
        aura(
            buff(
                scale_fn=lambda c: c.skills.get("Heartening Song", 0),
                stats={
                    "strength": 1,
                    "attack": 1,  # assuming this maps to a derived stat
                },
                condition=IS_ALLY,
            ),
            aura_id="bard_song",
        )
    ]


def rejuvenating_song_execute(caster, targets):
    return [
        aura(
            heal(
                scale_fn=lambda c: c.skills.get("Rejuvenating Song", 0),
                condition=IS_ALLY,
            ),
            aura_id="bard_song",
        )
    ]


# =========================================================
# Registration
# =========================================================

def register():

    # -------------------------
    # Borrowed Skill (Special Case)
    # -------------------------

    make_ability(
        name="Borrowed Skill 1",
        unlock_condition=lambda c: (
            c.has_adventure_job("Bard")
            and c.get_adventure_level_by_name("Bard") >= 1
        ),
        description="A Bard may 'replce' this skill with any other Tier One, level one Adventuring Job skill. Once chosen, it cannot be reset. Godspells and darkspells may NOT be chosen.",
        is_passive=False,
        is_skill=False,
    )

    # -------------------------
    # Songs
    # -------------------------

    make_ability(
        name="Distracting Song",
        unlock_condition=lambda c: (
            c.has_adventure_job("Bard")
            and c.get_adventure_level_by_name("Bard") >= 1
        ),
        execute=distracting_song_execute,
        cost=5,
        cost_pool="moxie",
        duration="Until Ceased",
        description="(Costs 5 moxie per minute of use) Bard's are able to use this song to distract their foes. Anyone not in their party within earshot suffers a debuff to their Charisma, Perception, and Willpower \n     equal to the level of this skill.\n     A Bard can only ever have one song active at a time.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Heartening Song",
        unlock_condition=lambda c: (
            c.has_adventure_job("Bard")
            and c.get_adventure_level_by_name("Bard") >= 1
        ),
        execute=heartening_song_execute,
        cost=5,
        cost_pool="moxie",
        duration="Until Ceased",
        description="(Costs 5 moxie per minute of use) Bards are able to use this song to strengthen the arm and improve aim. All allies within earshot gain a buff to their attack and Strength rolls equal to the level of this skill. \n     A Bard can only ever have one song active at a time.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Just That Cool",
        unlock_condition=lambda c: (
            c.has_adventure_job("Bard")
            and c.get_adventure_level_by_name("Bard") >= 1
        ),
        effect_generator=just_that_cool_effects,
        duration="Passive Constant",
        description="Bards are so cool that they gain a bonus to their Cool equal to their Bard Level. This skill has no levels.",
        is_passive=True,
        is_skill=False,
    )

    make_ability(
        name="Rejuvenating Song",
        unlock_condition=lambda c: (
            c.has_adventure_job("Bard")
            and c.get_adventure_level_by_name("Bard") >= 1
        ),
        execute=rejuvenating_song_execute,
        cost=5,
        cost_pool="moxie",
        duration="Until Ceased",
        description="(Costs 5 moxie per minute of use) The Bard can use this song to heal their allies. All allies within earshot can heal hit points and stamine equal to the level of this skill. \n     A Bard can only have one song active at a time.",
        is_passive=False,
        is_skill=True,
    )
