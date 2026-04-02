from domain.abilities.definitions._job_builder import build_job
from domain.abilities.patterns import buff, debuff, heal, aura, scaled_resource_effect
from domain.conditions import IS_ALLY, IS_ENEMY
from domain.effects import Heal
from domain.effects.special.roll import RollModifierEffect
from domain.effects.conditional import CompositeEffect


def restore_stamina(scale_fn, condition=None):
    return scaled_resource_effect(
        effect_cls=Heal,
        scale_fn=scale_fn,
        pool="stamina",
        condition=condition,
    )


build_job("Bard", [

    # Borrowed Skill 1
    {
        "name": "Borrowed Skill 1",
        "type": "passive",
        "description": "A Bard may 'replace' this skill with any other Tier One, level one Adventuring Job skill. Once chosen, it cannot be reset. Godspells and darkspells may NOT be chosen.",
        "effects": lambda ctx: [],
        "scales_with_level": False,
    },

    # Distracting Song
    {
        "name": "Distracting Song",
        "type": "skill",
        "cost": 5,
        "cost_pool": "moxie",
        "duration": "Until Ceased",
        "description": "(Costs 5 moxie per minute of use) Bards are able to use this song to distract their foes. Anyone not in their party within earshot suffers a debuff to their Charisma, Perception, and Willpower equal to the level of this skill. A Bard can only ever have one song active at a time.",
        "effects": lambda ctx: [
            aura(
                debuff(
                    scale_fn=lambda c: c.ability_levels.get("Distracting Song", 0),
                    stats={
                        "charisma": -1,
                        "perception": -1,
                        "willpower": -1,
                    },
                    condition=IS_ENEMY,
                ),
                aura_id="bard_song",
            )
        ],
    },

    # Heartening Song
    {
        "name": "Heartening Song",
        "type": "skill",
        "cost": 5,
        "cost_pool": "moxie",
        "duration": "Until Ceased",
        "description": "(Costs 5 moxie per minute of use) Bards are able to use this song to strengthen the arm and improve aim. All allies within earshot gain a buff to their attack and Strength rolls equal to the level of this skill. A Bard can only ever have one song active at a time.",
        "effects": lambda ctx: [
            aura(
                CompositeEffect(
                [
                    buff(
                        scale_fn=lambda c: c.ability_levels.get("Heartening Song", 0),
                        stats={"strength": 1},
                        condition=IS_ALLY,
                    ),
                    RollModifierEffect(
                        scale_fn=lambda c: c.ability_levels.get("Heartening Song", 0),
                        source_tag="heartening_song",
                        condition=IS_ALLY,
                    ),
                ]),
                aura_id="bard_song",
            )
        ],
    },

    # Just That Cool
    {
        "name": "Just That Cool",
        "type": "passive",
        "duration": "Passive Constant",
        "description": "Bards are so cool that they gain a bonus to their Cool equal to their Bard Level. This skill has no levels.",
        "target": "self",
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda c: c.get_progression_level("adventure", "Bard", 0),
                stats={"cool": 1},
            )
        ],
        "scales_with_level": False,
    },

    # Rejuvenating Song
    {
        "name": "Rejuvenating Song",
        "type": "skill",
        "cost": 5,
        "cost_pool": "moxie",
        "duration": "Until Ceased",
        "description": "(Costs 5 moxie per minute of use) The Bard can use this song to heal their allies. All allies within earshot can heal hit points and stamina equal to the level of this skill.\n A Bard can only have one song active at a time.",
        "effects": lambda ctx: [
            aura(
                CompositeEffect([
                    heal(
                        scale_fn=lambda c: c.ability_levels.get("Rejuvenating Song", 0),
                        condition=IS_ALLY,
                    ),
                    restore_stamina(
                        scale_fn=lambda c: c.ability_levels.get("Rejuvenating Song", 0),
                        condition=IS_ALLY,
                    ),
                ]),
                aura_id="bard_song",
            )
        ],
    },
])