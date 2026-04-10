from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    scaled_derived_buff,
    skill_check,
    inspect,
    apply_tag,
    moxie_damage,
    stamina_damage,
    tagged,
    on_event,
)
from domain.conditions import IS_ALLY, IS_ENEMY
from domain.effects.conditional import CompositeEffect

def bastard_is_eligible(ctx, target):
    """
    Bastards only benefit if their total level is not higher than the Bandit's.
    Adjust this helper later if you decide 'job level' should mean something narrower.
    """
    source_total = getattr(ctx.source, "total_level", lambda: 0)()
    target_total = getattr(target, "total_level", lambda: 0)()
    return tagged("bastard")(ctx, target) and target_total <= source_total

build_job("Bandit", [

# Ambush
{
    "name": "Ambush",
    "cost": 10,
    "cost_pool": "stamina",
    "description": "After a successful stealth roll, the Bandit may call an Ambush, and every 'Bastard' or party member gains a bonus to their attack roll equal to the level of this skill. This is a buff.",
    "duration": "1 turn",
    "effects": skill_check(
            ability="Ambush",
            stat="perception",
            # GM still verifies the stealth/setup precondition
            difficulty=50,
            on_success=[
                scaled_derived_buff(
                    scale_fn=lambda c: c.ability_levels.get("Ambush", 0),
                    stat="attack",
                    condition=lambda effect_ctx, target: (
                        IS_ALLY(effect_ctx, target)
                        or tagged("bastard")(effect_ctx, target)
                    ),
                )
            ],
        ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": True,
    "target": "self",
    "type": "skill",
},

# Band O' Bastards
{
    "name": "Band O' Bastards",
    "cost": 10,
    "cost_pool": "sanity",
    "description": "The Bandit may choose any number of creatures to become a part of his Band O' Bastards. If the creatures chosen have a job level higher than the Bandit, they cannot benefit from this skill. Bastards gain a buff to their Hit Points equal to the level of this skill.\nBeing a Bastard also allows other Bandit buffs to apply.",
    "duration": "1 day",
    "effects": CompositeEffect(
        apply_tag("bastard") and
        scaled_derived_buff(
            scale_fn=lambda c: c.ability_levels.get("Band O' Bastards", 0),
            stat="hp",
            condition=bastard_is_eligible,
        ),
    ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": True,
    "target": "creature",
    "type": "skill",
},

# Keep the Boys in Line
{ # TODO: I think I need to rework this so that it compels the Bastard to make the roll with their willpower against a difficulty of the Bandit's strength...
    "name": "Keep the Boys in Line",
    "description": "If any creature designated as a Bastard that wishes to attempt treachery against their Bandit must make a Willpower roll with the Bandit's Strength as the difficulty class. A failed roll results in the Bastard suffering Moxie damage equal to the level of this skill.",
    "effects": on_event(
            event_name="attempt_treachery",
            effect=skill_check(
                ability="Keep the Boys in Line",
                stat="strength",
                difficulty=lambda target: target.roll_willpower(),
                on_failure=[
                    moxie_damage(
                        scale_fn=lambda c: c.ability_levels.get("Keep the Boys in Line", 0),
                        condition=tagged("bastard"),
                    )
                ],
            ),
            condition=tagged("bastard"),
        ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": True,
    "target": "bastard",
    "type": "passive",
},
# Lay of the Land
{
    "name": "Lay of the Land",
    "cost": 5,
    "cost_pool": "stamina",
    "description": "The Bandit can examine a site to determine if it can be used for an ambush. The Bandit can then make a Perception plus Lay of the Land roll against a difficulty set by the GM.",
    "duration": "1 minute",
    "effects": skill_check(
            ability="Lay of the Land",
            stat="perception",
            difficulty=lambda target: target.difficulty,
            on_success=[
                inspect(
                    reveal_fn=lambda target: {
                        "ambush_quality": evaluate_ambush_site(target),
                        "terrain_advantages": get_terrain_advantages(target),
                    }
                )
            ],
        ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": True,
    "target": "site",
    "type": "skill",
},
# Subdue
{
    "name": "Subdue",
    "cost": 5,
    "cost_pool": "stamina",
    "description": "The Bandit can convert their lethal damage to nonlethal, dealing stamina damage instead of HP without any penalties.",
    "duration": "1 turn/level",
    "effects": stamina_damage(
            scale_fn=lambda c: c.ability_levels.get("Subdue", 0),
            condition=lambda effect_ctx, target: IS_ENEMY(effect_ctx, target),
        ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": True,
    "target": "enemy",
    "type": "skill",
},
],
source_type="adventure"
)