from domain.abilities import make_ability
from domain.abilities.patterns import (
    buff,
    skill_check,
    inspect,
    apply_tag,
    tagged,
    on_event,
    convert_damage,
)

from domain.conditions import (
    IS_ALLY,
)

# =========================================================
# Ambush — Group Attack Buff (Conditional)
# =========================================================

def ambush_execute(caster, targets):
    return [
        skill_check(
            skill="Ambush",
            stat="stealth",
            difficulty=50,  # or environment-based later
            on_success=buff(
                scale_fn=lambda c: c.skills.get("Ambush", 0),
                stats={"attack": 1},
                condition=lambda ctx, target: (
                    IS_ALLY(ctx, target) or tagged("bastard")(ctx, target)
                ),
            ),
        )
    ]


# =========================================================
# Band O' Bastards — Tag + Buff
# =========================================================

def band_of_bastards_execute(caster, targets):
    return [
        apply_tag("bastard"),
        buff(
            scale_fn=lambda c: c.skills.get("Band O' Bastards", 0),
            stats={"hp": 1},
            condition=tagged("bastard"),
        ),
    ]


# =========================================================
# Keep the Boys in Line — Reactive Punishment
# =========================================================

def keep_the_boys_effects(character):
    return [
        on_event(
            event_name="attempt_treachery",
            effect=skill_check(
                skill="Keep the Boys in Line",
                stat="strength",
                difficulty=lambda ctx, target: target.roll_willpower(),
                on_failure=convert_damage("moxie", "moxie"),  # damage applied directly
            ),
            condition=tagged("bastard"),
        )
    ]


# =========================================================
# Lay of the Land — Environmental Analysis
# =========================================================

def lay_of_the_land_execute(caster, targets):
    return [
        skill_check(
            skill="Lay of the Land",
            stat="perception",
            difficulty=lambda ctx, target: target.difficulty,
            on_success=inspect(
                reveal_fn=lambda caster, target: {
                    "ambush_quality": evaluate_ambush_site(target),
                    "terrain_advantages": get_terrain_advantages(target),
                }
            ),
        )
    ]


# =========================================================
# Subdue — Damage Conversion
# =========================================================

def subdue_execute(caster, targets):
    return [
        convert_damage("hp", "stamina")
    ]


# =========================================================
# Registration
# =========================================================

def register():

    make_ability(
        name="Ambush",
        unlock_condition=lambda c: (
            c.has_adventure_job("Bandit")
            and c.get_adventure_level_by_name("Bandit") >= 1
        ),
        execute=ambush_execute,
        cost=10,
        cost_pool="stamina",
        duration="1 turn",
        description="This skill allows an Assassin to blend in with a crowd, reducing the chance that their motives or presence will be questioned, or possibly even being noticed. This provides a bonus equalt to its level to Charisma when applicable.\n     After a successful stealth roll, the Bandit may call an Ambush, and every 'Bastard' or party member gains a bonus to their attack roll equal to the level of this skill.\n     This is a buff.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Band O' Bastards",
        unlock_condition=lambda c: (
            c.has_adventure_job("Bandit")
            and c.get_adventure_level_by_name("Bandit") >= 1
        ),
        execute=band_of_bastards_execute,
        cost=10,
        cost_pool="sanity",
        duration="1 day",
        description="The Bandit may choose any number of creatures to become a part of his Band O' Bastards. If the creatures chosen have a job level higher than the Bandit, they cannot benefit from this skill. Bastards gain a buff to their Hit Points equal to thelevel of this skill.\n     Being a Bastard also allows other Bandit buffs to apply.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Keep the Boys in Line",
        unlock_condition=lambda c: (
            c.has_adventure_job("Bandit")
            and c.get_adventure_level_by_name("Bandit") >= 1
        ),
        effect_generator=keep_the_boys_effects,
        duration="Passive Constant",
        description="If any creature designated as a Bastard that wishes to attempt treachery against their Bandit must make a Willpower roll with the Bandit's Strength as the difficulty class. A failed roll results in the Bastard suffering Moxie damage equal to the level of this skill.",
        is_passive=True,
        is_skill=False,
    )

    make_ability(
        name="Lay of the Land",
        unlock_condition=lambda c: (
            c.has_adventure_job("Bandit")
            and c.get_adventure_level_by_name("Bandit") >= 1
        ),
        execute=lay_of_the_land_execute,
        cost=5,
        cost_pool="stamina",
        duration="1 minute",
        description="The Bandit can examine a site to determine if it can be used for an ambush. The Bandit can then make a Perception plus Lay of the Land roll against a difficulty set by the GM.",
        is_passive=False,
        is_skill=True,
    )

    make_ability(
        name="Subdue",
        unlock_condition=lambda c: (
            c.has_adventure_job("Bandit")
            and c.get_adventure_level_by_name("Bandit") >= 1
        ),
        execute=subdue_execute,
        cost=5,
        cost_pool="stamina",
        duration="1 turn/level",
        description="The Bandit can convert their lethal damage to nonlethal, dealing stamina damage instead of HP without any penalties",
        is_passive=False,
        is_skill=True,
    )
