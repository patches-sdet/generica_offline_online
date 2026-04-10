from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    scaled_derived_buff,
    scaled_stat_buff,
    hp_damage,
    modify_next_attack,
    on_event,
    skill_check,
)
from domain.conditions import IS_ENEMY
from domain.effects.conditional import CompositeEffect


build_job("Berserker", [

    # Furious Strike
    {
        "name": "Furious Strike",
        "cost": 10,
        "cost_pool": "hp",
        "description": "Your next attack inflicts additional damage equal to your Berserker level plus the level of this skill. The damage does not apply to any attack if you miss.",
        "duration": "1 Attack",
        "effects": modify_next_attack(
                lambda ctx, attack: attack.add_bonus(
                    "damage",
                    ctx.source.get_progression_level("adventure", "Berserker", 0)
                    + ctx.source.ability_levels.get("Furious Strike", 0),
                )
            ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    # Growl
    {"grant": "Growl", "required_level": 1},

    # Headbutt
    {
        "name": "Headbutt",
        "cost": 10,
        "cost_pool": "hp",
        "description": "Smash your head into the enemy's face to try to stun them. This is a Brawling skill plus Headbutt roll. If hit, the enemy must roll Constitution to avoid being stunned for 1 round.",
        "duration": "1 Attack",
        "effects": CompositeEffect([
            hp_damage(
                scale_fn=lambda c: c.ability_levels.get("Headbutt", 0),
                condition=IS_ENEMY,
            ),
            skill_check(
                ability="Headbutt",
                stat="strength",
                difficulty=lambda target: target.roll_constitution(),
                on_success=[
                    apply_state("stunned")
                ],
            ),
        ],
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    # Power From Pain
    {
        "name": "Power From Pain",
        "description": "Pain is your fuel that drives you to fight harder... until you drop. Whenever you lose 10 or more hit points, you gain a buff of +1 to all strength-based rolls for the next 5 minutes. This skill has no levels.",
        "duration": "Passive Constant",
        "effects": on_event(
                event_name="hp_lost",
                effect=scaled_stat_buff(
                    scale_fn=lambda c: 1,
                    stats={"strength": 1},
                ),
                condition=lambda event_ctx: event_ctx.amount >= 10,
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Rage
    {
        "name": "Rage",
        "cost": 5,
        "cost_pool": "moxie",
        "description": "You would like to RAGE! While raging, you cannot use ranged attacks or spells, and you suffer a perception debuff equal to your Berserker level. Additionally, you may add your Berserker level to all other rolls. This is an increase, not a buff. You may not rage for more turns than you have levels in this skill.",
        "duration": "1 Turn/level",
            "effects": CompositeEffect([
            apply_state("raging"),
            apply_state("cannot_use_ranged_attacks"),
            apply_state("cannot_cast_spells"),
            scaled_stat_buff(
                scale_fn=lambda c: c.get_progression_level("adventure", "Berserker", 0),
                stats={"perception": -1},
            ),
            scaled_derived_buff(
                scale_fn=lambda c: c.get_progression_level("adventure", "Berserker", 0),
                stat="all_rolls",
                condition=lambda c: "raging" in getattr(c.source, "states", {}),
                ),
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
],
source_type="adventure"
)