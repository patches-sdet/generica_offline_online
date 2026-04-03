from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    buff,
    skill_check,
    inspect,
    apply_tag,
    tagged,
    on_event,
    scaled_resource_effect,
)
from domain.effects import Damage
from domain.conditions import IS_ALLY

def bastard_is_eligible(ctx, target):
    """
    Bastards only benefit if their total level is not higher than the Bandit's.
    Adjust this helper later if you decide 'job level' should mean something narrower.
    """
    source_total = getattr(ctx.source, "total_level", lambda: 0)()
    target_total = getattr(target, "total_level", lambda: 0)()
    return tagged("bastard")(ctx, target) and target_total <= source_total

def moxie_damage(scale_fn, condition=None):
    return scaled_resource_effect(
        effect_cls=Damage,
        scale_fn=scale_fn,
        pool="moxie",
        condition=condition,
    )

build_job("Bandit", [

    # Ambush
    {
        "name": "Ambush",
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "duration": "1 turn",
        "description": "After a successful stealth roll, the Bandit may call an Ambush, and every 'Bastard' or party member gains a bonus to their attack roll equal to the This is a buff.",
        "effects": lambda ctx: [
            skill_check(
                ability="Ambush",
                stat="perception",
                # GM still verifies the stealth/setup precondition
                difficulty=50,
                on_success=[
                    buff(
                        scale_fn=lambda c: c.ability_levels.get("Ambush", 0),
                        stats={"attack": 1},
                        condition=lambda effect_ctx, target: (
                            IS_ALLY(effect_ctx, target)
                            or tagged("bastard")(effect_ctx, target)
                        ),
                    )
                ],
            )
        ],
    },

    # Band O' Bastards
    {
        "name": "Band O' Bastards",
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "duration": "1 day",
        "description": "The Bandit may choose any number of creatures to become a part of his Band O' Bastards. If the creatures chosen have a job level higher than the Bandit, they cannot benefit from this skill. Bastards gain a buff to their Hit Points equal to the level of this skill.\nBeing a Bastard also allows other Bandit buffs to apply.",
        "effects": lambda ctx: [
            apply_tag("bastard"),
            buff(
                scale_fn=lambda c: c.ability_levels.get("Band O' Bastards", 0),
                stats={"hp": 1},
                condition=bastard_is_eligible,
            ),
        ],
    },

    # Keep the Boys in Line
    {
        "name": "Keep the Boys in Line",
        "type": "passive",
        "description": "If any creature designated as a Bastard that wishes to attempt treachery against their Bandit must make a Willpower roll with the Bandit's Strength as the difficulty class. A failed roll results in the Bastard suffering Moxie damage equal to the level of this skill.",
        "effects": lambda ctx: [
            on_event(
                event_name="attempt_treachery",
                effect=skill_check(
                    ability="Keep the Boys in Line",
                    stat="strength",
                    difficulty=lambda check_ctx, target: target.roll_willpower(),
                    on_failure=[
                        moxie_damage(
                            scale_fn=lambda c: c.ability_levels.get("Keep the Boys in Line", 0),
                            condition=tagged("bastard"),
                        )
                    ],
                ),
                condition=tagged("bastard"),
            )
        ],
    },
    # Lay of the Land
    {
        "name": "Lay of the Land",
        "type": "skill",
        "cost": 5,
        "cost_pool": "stamina",
        "duration": "1 minute",
        "description": "The Bandit can examine a site to determine if it can be used for an ambush. The Bandit can then make a Perception plus Lay of the Land roll against a difficulty set by the GM.",
        "effects": lambda ctx: [
            skill_check(
                ability="Lay of the Land",
                stat="perception",
                difficulty=lambda check_ctx, target: target.difficulty,
                on_success=[
                    inspect(
                        reveal_fn=lambda inspect_ctx, target: {
                            "ambush_quality": evaluate_ambush_site(target),
                            "terrain_advantages": get_terrain_advantages(target),
                        }
                    )
                ],
            )
        ],
    },
    # Subdue
    {
        "name": "Subdue",
        "type": "skill",
        "cost": 5,
        "cost_pool": "stamina",
        "duration": "1 turn/level",
        "description": "The Bandit can convert their lethal damage to nonlethal, dealing stamina damage instead of HP without any penalties.",
        "effects": lambda ctx: [
            moxie_damage(
                scale_fn=lambda c: c.ability_levels.get("Subdue", 0),
            )
        ],
    },
])