from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import buff, scaled_stat_buff, scaled_skill_buff
from domain.conditions import IS_ALLY, IN_PARTY
from domain.effects.conditional import CompositeEffect

build_job("Mercenary", [

    {
        "name": "Fight the Battles",
        "cost": 10,
        "cost_pool": "fortune",
        "description": "You are strongest when fighting with allies. You can use this skill to buff yourself and your party members' Strength, Constitution, Armor, and all Generic Weapon skills by an amount equal to your level in this skill.",
        "duration": "1 Turn/level",
        "effects": lambda ctx: [
            CompositeEffect([
                scaled_stat_buff(
                    stats=["strength", "constitution", "armor"],
                    scale_fn=lambda c: c.ability_levels.get("Fight the Battles", 0),
                    condition=IN_PARTY,
                ),
                scaled_skill_buff(
                    skills=["melee", "ranged", "defense"], # Need to make a list/dict that has all the skills, and then have this check to only add the bonus to skills another character has 1+ points
                    scale_fn=lambda c: c.ability_levels.get("Fight the Battles", 0),
                    condition=IN_PARTY,
                    ),
                ],
            ),
        ],
        "is_passive": False,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

])
