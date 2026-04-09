from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import scaled_stat_buff, aura, heal_hp, heal_stamina, scaled_derived_buff
from domain.conditions import IS_ALLY, IS_ENEMY
from domain.effects.special.roll import RollModifierEffect
from domain.effects.conditional import CompositeEffect


build_job("Bard", [

# Borrowed Skill 1
# {
#     "name": "Borrowed Skill 1",
#     "description": "A Bard may 'replace' this skill with any other Tier One, level one Adventuring Job skill. Once chosen, it cannot be reset. Godspells and darkspells may NOT be chosen.",
#     "effects": [], # Need to build the method for this to actually work, but for now this is a placeholder
#     "scales_with_level": False,
#     "type": "passive",
# },

# Distracting Song
{
    "name": "Distracting Song",
    "cost": 5,
    "cost_pool": "moxie",
    "description": "(Costs 5 moxie per minute of use) Bards are able to use this song to distract their foes. Anyone not in their party within earshot suffers a debuff to their Charisma, Perception, and Willpower equal to the level of this skill. A Bard can only ever have one song active at a time.",
    "duration": "Until Ceased",
    "effects": aura(
            scaled_stat_buff(
                scale_fn=lambda c: c.ability_levels.get("Distracting Song", 0),
                stats={
                    "charisma": -1,
                    "perception": -1,
                    "willpower": -1,
                },
                condition=IS_ENEMY,
            ),
            aura_id="bard_song",
        ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": True,
    "target": "enemy",
    "type": "skill",
},

# Heartening Song
{
    "name": "Heartening Song",
    "cost": 5,
    "cost_pool": "moxie",
    "description": "(Costs 5 moxie per minute of use) Bards are able to use this song to strengthen the arm and improve aim. All allies within earshot gain a buff to their attack and Strength rolls equal to the level of this skill. A Bard can only ever have one song active at a time.",
    "duration": "Until Ceased",
    "effects": aura(
            CompositeEffect(
            [
                scaled_stat_buff(
                    scale_fn=lambda c: c.ability_levels.get("Heartening Song", 0),
                    stats={"strength": 1},
                    condition=IS_ALLY,
                ) and
                RollModifierEffect(
                    scale_fn=lambda c: c.ability_levels.get("Heartening Song", 0),
                    source_tag="heartening_song",
                    condition=IS_ALLY,
                ),
            ]),
            aura_id="bard_song",
        ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": True,
    "target": "ally",
    "type": "skill",
},

# Just That Cool
{
    "name": "Just That Cool",
    "description": "Bards are so cool that they gain a bonus to their Cool equal to their Bard Level. This skill has no levels.",
    "duration": "Passive Constant",
    "effects": scaled_derived_buff(
            scale_fn=lambda c: c.get_progression_level("adventure", "Bard", 0),
            stat="cool",
        ),
    "is_passive": True,
    "is_skill": False,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": False,
    "target": "self",
    "type": "passive",
},

# Rejuvenating Song
{
    "name": "Rejuvenating Song",
    "cost": 5,
    "cost_pool": "moxie",
    "description": "(Costs 5 moxie per minute of use) The Bard can use this song to heal their allies. All allies within earshot can heal hit points and stamina equal to the level of this skill.\n A Bard can only have one song active at a time.",
    "duration": "Until Ceased",
    "effects": aura(
            CompositeEffect([
                heal_hp(
                    scale_fn=lambda c: c.ability_levels.get("Rejuvenating Song", 0),
                    condition=IS_ALLY,
                ),
                heal_stamina(
                    scale_fn=lambda c: c.ability_levels.get("Rejuvenating Song", 0),
                    condition=IS_ALLY,
                ),
            ]),
            aura_id="bard_song",
        ),
    "is_passive": False,
    "is_skill": True,
    "is_spell": False,
    "required_level": 1,
    "scales_with_level": True,
    "target": "ally",
    "type": "skill",
},

])