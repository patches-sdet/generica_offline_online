from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    buff,
    damage,
    debuff,
    modify_next_attack,
    on_event,
    skill_check,
    scaled_resource_effect,
)
from domain.conditions import IS_ENEMY
from domain.effects import Damage


def moxie_damage(scale_fn, condition=None):
    return scaled_resource_effect(
        effect_cls=Damage,
        scale_fn=scale_fn,
        pool="moxie",
        condition=condition,
    )


build_job("Berserker", [

    # Furious Strike
    {
        "name": "Furious Strike",
        "type": "skill",
        "duration": "1 Attack",
        "description": "Your next attack inflicts additional damage equal to your Berserker level plus the level of this skill. The damage does not apply to any attack if you miss.",
        "target": "enemy",
        "effects": lambda ctx: [
            modify_next_attack(
                lambda ctx, attack: attack.add_bonus(
                    "damage",
                    ctx.source.get_progression_level("adventure", "Berserker", 0)
                    + ctx.source.ability_levels.get("Furious Strike", 0),
                )
            )
        ],
    },

    # Growl
    {
        "name": "Growl",
        "type": "skill",
        "cost": 10,
        "cost_pool": "moxie",
        "duration": "1 Attack",
        "description": "Growl at an enemy, inflicting moxie damage. This is a Charisma plus Growl skill roll against the target's Willpower.",
        "target": "enemy",
        "effects": lambda ctx: [
            skill_check(
                ability="Growl",
                stat="charisma",
                difficulty=lambda check_ctx, target: target.roll_willpower(),
                on_success=[
                    moxie_damage(
                        scale_fn=lambda c: c.ability_levels.get("Growl", 0),
                        condition=IS_ENEMY,
                    )
                ],
            )
        ],
    },

    # Headbutt
    {
        "name": "Headbutt",
        "type": "skill",
        "cost": 10,
        "cost_pool": "hp",
        "duration": "1 Attack",
        "description": "Smash your head into the enemy's face to try to stun them. This is a brawling skill roll that also adds your level in this skill. If hit, the enemy must roll Constitution to avoid being stunned for 1 round.",
        "target": "enemy",
        "effects": lambda ctx: [
            damage(
                scale_fn=lambda c: c.ability_levels.get("Headbutt", 0),
                condition=IS_ENEMY,
            ),
            skill_check(
                ability="Headbutt",
                stat="strength",
                difficulty=lambda check_ctx, target: target.roll_constitution(),
                on_success=[
                    apply_state("stunned")
                ],
            ),
        ],
    },

    # Power From Pain
    {
        "name": "Power From Pain",
        "type": "passive",
        "duration": "Passive Constant",
        "description": "Pain is your fuel that drives you to fight harder... until you drop. Whenever you lose 10 or more hit points, you gain a buff of +1 to all strength-based rolls for the next 5 minutes. This skill has no levels.",
        "target": "self",
        "effects": lambda ctx: [
            on_event(
                event_name="hp_lost",
                effect=buff(
                    scale_fn=lambda c: 1,
                    stats={"strength": 1},
                    duration="5 minutes",
                ),
                condition=lambda event_ctx: event_ctx.amount >= 10,
            )
        ],
        "scales_with_level": False,
    },

    # Rage
    {
        "name": "Rage",
        "type": "skill",
        "cost": 5,
        "cost_pool": "moxie",
        "duration": "1 Turn/level",
        "description": "You would like to RAGE! While raging, you cannot use ranged attacks or spells, and you suffer a perception debuff equal to your Berserker level. Additionally, you may add your Berserker level to all other rolls. This is an increase, not a buff. You may not rage for more turns than you have levels in this skill.",
        "effects": lambda ctx: [
            apply_state("raging"),
            apply_state("cannot_use_ranged_attacks"),
            apply_state("cannot_cast_spells"),
            debuff(
                scale_fn=lambda c: c.get_progression_level("adventure", "Berserker", 0),
                stats={"perception": -1},
            ),
        ],
    },
])