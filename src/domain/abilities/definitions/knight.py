from domain.abilities.builders._job_builder import build_job
from domain.abilities import ability_level, ctx_ability_level, progression_level, ctx_progression_level
from domain.abilities.patterns import (
    apply_state,
    create_item,
    heal_moxie,
    modify_next_attack,
    passive_modifier,
    scaled_derived_buff,
)


# Local helpers

def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


def _set_attack_attr(attack, key: str, value) -> None:
    setattr(attack, key, value)


# Passive / runtime helpers

def _shield_saint_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["shield_saint_active"] = {
        "active": True,
        "duration_turns": ability_level(ctx, "Shield Saint"),
        "requires_shield": True,
        "agility_targeting_penalty": ability_level(ctx, "Shield Saint"),
        "shield_armor_bonus_suppressed": True,
        "source_ability": "Shield Saint",
    }


def _duty_is_no_burden_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["duty_is_no_burden"] = {
        "active": True,
        "ignore_armor_penalties": True,
        "ignore_cursed_armor_penalties": True,
        "source_ability": "Duty is no Burden",
    }


# Attack helpers

def _dolorous_strike_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "requires_melee_range", True)
    _set_attack_attr(attack, "damage_bonus", ability_level(ctx, "Dolorous Strike"))
    _set_attack_attr(attack, "dolorous_strike", True)


# Item factory

def _make_lance(source):
    return {
        "name": "Lance",
        "base_type": "spear",
        "weapon_level": progression_level(source, "adventure", "Knight"),
        "created_by": "Lancer",
        "temporary": True,
        "duration_minutes": 5,
    }


build_job("Knight", [

    # Level 1

    {
        "name": "Armor Mastery",
        "description": (
            "A Knight gains a bonus to armor equal to Knight level."
        ),
        "duration": "Passive Constant",
        "effects": scaled_derived_buff(
            scale_fn=lambda ctx: ctx_progression_level(ctx, "adventure", "Grifter"),
            stat="armor",
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Code of Chivalry",
        "description": (
            "While the Knight keeps their sworn code, they gain +1 armor per two levels of "
            "Code of Chivalry. This levels by oathkeeping rather than normal grind progression."
        ),
        "duration": "Passive Constant",
        "effects": scaled_derived_buff(
            scale_fn=lambda c: ability_level(c, "Code of Chivalry") // 2,
            stat="armor",
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Horsemanship",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "Boosts ride skill by Horsemanship level."
        ),
        "duration": "10 Minutes per Knight Level",
        "effects": apply_state(
            "horsemanship_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Grifter") * 10,
                "ride_bonus": ability_level(source, "Horsemanship"),
                "source_ability": "Horsemanship",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Rally Troops",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "All allies within earshot regain lost moxie equal to Rally Troops level."
        ),
        "duration": "1 Action",
        "effects": heal_moxie(
            scale_fn=lambda c: ability_level(c, "Rally Troops"),
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Shield Saint",
        "description": (
            "While active and using a shield, attacks against you that target Agility suffer a penalty "
            "equal to Shield Saint level, but the shield does not provide its normal armor benefit."
        ),
        "duration": "1 Turn per Knight Level",
        "effects": passive_modifier(_shield_saint_modifier),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "passive",
    },

    # Level 5

    {
        "name": "Always in Uniform",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "When not wearing armor, gain armor equal to Knight level."
        ),
        "duration": "10 Minutes",
        "effects": apply_state(
            "always_in_uniform_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": 10,
                "requires_no_armor": True,
                "armor_bonus": progression_level(source, "adventure", "Grifter"),
                "source_ability": "Always in Uniform",
            },
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Corps a Corps",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "Locks your weapon with a foe's weapon. Both combatants are prevented from attacking until "
            "the lock is broken or a weapon is dropped."
        ),
        "duration": "Until Canceled or Escaped",
        "effects": apply_state(
            "corps_a_corps_active",
            value_fn=lambda source: {
                "active": True,
                "locker": source,
                "initiate_check": {
                    "source_stat": "strength",
                    "source_skill": "Corps a Corps",
                    "target_stat": "strength",
                    "target_skill": "highest_weapon_skill",
                },
                "break_check": {
                    "challenger_stat": "strength",
                    "challenger_skill": "highest_weapon_skill",
                    "defender_stat": "strength",
                    "defender_skill": "Corps a Corps",
                    "costs_action": True,
                },
                "cannot_attack_while_locked": True,
                "movement_restricted": True,
                "dropping_weapon_ends_lock": True,
                "source_ability": "Corps a Corps",
            },
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Dolorous Strike",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "Your next melee attack gains bonus damage equal to Dolorous Strike level."
        ),
        "duration": "1 Attack",
        "effects": modify_next_attack(_dolorous_strike_modifier),
        "required_level": 5,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Lancer",
        "cost": 20,
        "cost_pool": "fortune",
        "description": (
            "Creates a temporary lance with weapon level equal to Knight level."
        ),
        "duration": "5 Minutes",
        "effects": create_item(_make_lance),
        "required_level": 10,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Shield Friend",
        "cost": 20,
        "cost_pool": "stamina",
        "description": (
            "Intercept attacks aimed at an adjacent ally, causing them to strike you instead. "
            "While active, your Agility is halved for defense."
        ),
        "duration": "1 Turn per Level",
        "effects": apply_state(
            "shield_friend_active",
            value_fn=lambda source: {
                "active": True,
                "guardian": source,
                "duration_turns": ability_level(source, "Shield Friend"),
                "redirect_attacks_to_guardian": True,
                "requires_adjacent_ally": True,
                "guardian_defense_penalty": {
                    "stat": "agility",
                    "mode": "halve_for_defense",
                },
                "source_ability": "Shield Friend",
            },
        ),
        "required_level": 10,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Favored Mount",
        "cost": 30,
        "cost_pool": "moxie",
        "description": (
            "Empowers your current steed, giving it a bonus to all attributes equal to Knight level. "
            "Only one favored mount may be active at a time."
        ),
        "duration": "Until Rechosen",
        "effects": apply_state(
            "favored_mount",
            value_fn=lambda source: {
                "active": True,
                "favored_by": source,
                "all_attribute_bonus": progression_level(source, "adventure", "Grifter"),
                "single_favored_mount_per_knight": True,
                "source_ability": "Favored Mount",
            },
        ),
        "required_level": 15,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    {"grant": "Pommel Strike", "required_level": 15},

    # Level 20

    {
        "name": "Charge!",
        "cost": 50,
        "cost_pool": "stamina",
        "description": (
            "Double running or mounted speed, ignore terrain modifiers, and gain a bonus to the melee "
            "attack made after movement equal to Charge! level. You must move to gain the benefits."
        ),
        "duration": "10 Minutes",
        "effects": apply_state(
            "charge_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": 10,
                "speed_multiplier": 2,
                "ignore_terrain_modifiers": True,
                "must_move_for_benefits": True,
                "post_movement_melee_attack_bonus": ability_level(source, "Charge!"),
                "works_for": ("running", "mounted"),
                "source_ability": "Charge!",
            },
        ),
        "required_level": 20,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "The Last Crusade",
        "cost": 50,
        "cost_pool": "moxie",
        "description": (
            "Party members may use your Charge! skill at your current level while this is active, "
            "paying the normal stamina cost themselves."
        ),
        "duration": "10 Minutes",
        "effects": apply_state(
            "last_crusade_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": 10,
                "shares_ability": "Charge!",
                "shared_charge_level": ability_level(source, "Charge!"),
                "allies_pay_own_costs": True,
                "source_ability": "The Last Crusade",
            },
        ),
        "required_level": 20,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Duty is no Burden",
        "description": (
            "Armor causes you no penalties at all, even if cursed."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_duty_is_no_burden_modifier),
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Unyielding",
        "cost": 75,
        "cost_pool": "stamina",
        "description": (
            "While active, critical attacks against you are treated as regular attacks with no added "
            "critical effects."
        ),
        "duration": "1 Turn per Skill Level",
        "effects": apply_state(
            "unyielding_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": ability_level(source, "Unyielding"),
                "downgrade_critical_hits_to_normal_hits": True,
                "source_ability": "Unyielding",
            },
        ),
        "required_level": 25,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

], source_type="adventure")