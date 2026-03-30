from domain.abilities.factory import make_ability
from domain.abilities.patterns import apply_state, buff, convert_damage, damage, debuff, on_event, skill_check
from domain.conditions import IS_ENEMY
from domain.effects.special.roll import RollModifierEffect

# Passive — Power From Pain

def power_from_pain_effects(character):
    return [
        on_event(
            event_name="hp_lost",
            effect=buff(
                scale_fn=lambda c: 1,
                stats={"strength": 1},
                duration="5 minutes",
            ),
            condition=lambda ctx: ctx.amount >= 10,
        )
    ]

# Buffs / Debuffs

def rage_execute(character):
    effects = []

    # Perception penalty
    effects.extend(
        debuff(
            scale_fn=lambda c: c.get_adventure_level_by_name("Berserker"),
            stats={
                "perception": -1,
            },
        )
    )
    # Roll bonus
    effects.append(
    RollModifierEffect(
        scale_fn=lambda c: c.get_adventure_level_by_name("Berserker"),
        source_tag="rage",
    )
)

    return effects


def furious_strike_execute(caster, targets):
    return [
        damage(
            scale_fn=lambda c: (
                c.skills.get("Furious Strike", 0)
                + c.get_adventure_level_by_name("Berserker")
            ),
            condition=IS_ENEMY,
        ),
    ]


def headbutt_execute(caster, targets):
    return [
        damage(
            scale_fn=lambda c: c.skills.get("Headbutt", 0),
            condition=IS_ENEMY,
        ),
            skill_check(
            skill="Headbutt",
            difficulty=lambda ctx, target: target.roll_willpower(),
            on_success=apply_state("stunned"),
            condition=IS_ENEMY,
        ),
    ]

def growl_execute(caster, targets):
    return [
        skill_check(
            skill="Growl",
            difficulty=lambda ctx, target: target.roll_willpower(),
            on_success=convert_damage(
                from_pool="hp",
                to_pool="moxie",
                condition=IS_ENEMY,
            ),
        ),
    ]

# Active Skills / Attacks

# Registration

def register():

    # Furious Attack

    make_ability(
        name="Furious Strike",
        unlock_condition=lambda c: (
            c.has_adventure_job("Berserker")
            and c.get_adventure_level_by_name("Berserker") >= 1
        ),
        execute=furious_strike_execute,
        duration="1 Attack",
        description="Your next attack inflicts addtional damage equal to your Berserker level plus the level of this skill. The damage does not apply to any attack if you miss.",
        is_passive=False,
        is_skill=True,
        target_type="enemy"
    )

    # Growl

    make_ability(
        name="Growl",
        unlock_condition=lambda c: (
            c.has_adventure_job("Berserker")
            and c.get_adventure_level_by_name("Berserker") >= 1
        ),
        execute=growl_execute,
        cost=10,
        cost_pool="moxie",
        duration="1 Attack",
        description="Growl at an enemy, inflicting moxie damage. This is a Charisma plus Growl skill roll against the target's Willpower.",
        is_passive=False,
        is_skill=True,
        target_type="enemy"
    )

    make_ability(
        name="Headbutt",
        unlock_condition=lambda c: (
            c.has_adventure_job("Berserker")
            and c.get_adventure_level_by_name("Berserker") >= 1
        ),
        execute=headbutt_execute,
        cost=10,
        cost_pool="HP",
        duration="1 Attack",
        description="Smash your head into the enemy's face to try to stun them. This is a brawling skill roll that also adds your level in this skill.\n     If hit, the enemy must roll Constitution to avoid being stunned for 1 round.",
        is_passive=False,
        is_skill=True,
        target_type="enemy"
    )

    make_ability(
        name="Power From Pain",
        unlock_condition=lambda c: (
            c.has_adventure_job("Berserker")
            and c.get_adventure_level_by_name("Berserker") >= 1
        ),
        effect_generator=power_from_pain_effects,
        duration="Passive Constant",
        description="Pain is your fuel that drives you to fight harder... until you drop. Whenever you lose 10 or more hit points, you gain a buff of +1\n     to all strength-based rolls for the next 5 minutes. This skill has no levels.",
        is_passive=True,
        is_skill=False,
        target_type = "self"
    )

    make_ability(
        name="Rage",
        unlock_condition=lambda c: (
            c.has_adventure_job("Berserker")
            and c.get_adventure_level_by_name("Berserker") >= 1
        ),
        execute=rage_execute,
        cost=5,
        cost_pool="moxie",
        duration="1 Turn/level",
        description="You would like to RAGE! While raging, you cannot use ranged attacks or spells, and you suffer a perception debuff equal to your Berserker level.\n     Additionally, you may add your Berserker level to all other rolls. \n     This is an increase, not a buff. You may not rage for more turns than you have levels in this skill",
        is_passive=False,
        is_skill=True,
    )
