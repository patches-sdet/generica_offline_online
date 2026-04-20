from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    composite,
    conditional_damage,
    heal_hp,
    inspect,
    passive_modifier,
    scaled_skill_buff,
    scaled_stat_buff,
)
from domain.conditions import IS_ENEMY


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _mercenary_level(character) -> int:
    return character.get_progression_level("adventure", "Mercenary", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


# Passive / runtime helpers

def _named_and_feared_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["named_and_feared"] = {
        "active": True,
        "battlefield_only": True,
        "immune_to_fear_bypasses": True,
        "fails_if_only_target_available": True,
        "attack_redirect_check": {
            "attacker_stat": "willpower",
            "defender_stat": "luck",
        },
        "source_ability": "Named and Feared",
    }


build_job("Mercenary", [

    # Level 1

    {
        "name": "Blood is Gold",
        "cost": 0,
        "cost_pool": None,
        "description": (
            "Spend coin to restore HP. Each 5 copper worth of coinage restores 1 HP, up to "
            "three times Blood is Gold level per use."
        ),
        "duration": "1 Action",
        "effects": composite(
            heal_hp(
                scale_fn=lambda c: _ability_level(c, "Blood is Gold") * 3,
            ),
            apply_state(
                "blood_is_gold_active",
                value_fn=lambda source: {
                    "active": True,
                    "coin_heal_rate_copper_per_hp": 5,
                    "max_heal_per_use": _ability_level(source, "Blood is Gold") * 3,
                    "requires_spendable_coin": True,
                    "consumed_coin_is_destroyed": True,
                    "source_ability": "Blood is Gold",
                },
            ),
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Do the Job",
        "cost": 5,
        "cost_pool": "fortune",
        "description": (
            "While actively pursuing a quest with a material reward, gain a bonus to all rolls "
            "equal to Do the Job level."
        ),
        "duration": "1 Minute per Skill Level",
        "effects": apply_state(
            "do_the_job_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _ability_level(source, "Do the Job"),
                "requires_rewarded_quest": True,
                "requires_actively_pursuing_quest": True,
                "all_roll_bonus": _ability_level(source, "Do the Job"),
                "source_ability": "Do the Job",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Fight the Battles",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "Buff the Mercenary and all party members, increasing Constitution, Strength, Armor, "
            "and all weapon skills by Mercenary level."
        ),
        "duration": "1 Turn per Skill Level",
        "effects": composite(
            scaled_stat_buff(
                scale_fn=_mercenary_level,
                stats={
                    "constitution": 1,
                    "strength": 1,
                    "armor": 1,
                },
            ),
            scaled_skill_buff(
                scale_fn=_mercenary_level,
                skills={
                    "all_weapon_skills": 1,
                },
            ),
            apply_state(
                "fight_the_battles_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_turns": _ability_level(source, "Fight the Battles"),
                    "weapon_skill_scope": "all_weapon_skills",
                    "bonus_amount": _mercenary_level(source),
                    "source_ability": "Fight the Battles",
                },
            ),
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "party",
        "type": "skill",
    },

    {
        "name": "Get Paid",
        "cost": 20,
        "cost_pool": "fortune",
        "description": (
            "If a quest-giver tries to cheat you out of your reward, they permanently lose luck "
            "equal to Get Paid level until they pay what they owe. This skill levels when used."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "get_paid_active",
            value_fn=lambda source: {
                "active": True,
                "trigger": "quest_giver_refuses_payment",
                "luck_penalty": _ability_level(source, "Get Paid"),
                "restored_if_paid": True,
                "levels_on_use": True,
                "source_ability": "Get Paid",
            },
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Take the Hits",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "Buffs your HP by an amount equal to Take the Hits level."
        ),
        "duration": "1 Turn per Skill Level",
        "effects": apply_state(
            "take_the_hits_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": _ability_level(source, "Take the Hits"),
                "hp_bonus": _ability_level(source, "Take the Hits"),
                "source_ability": "Take the Hits",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Follow the Dotted Line",
        "cost": 20,
        "cost_pool": "fortune",
        "description": (
            "Attempt to reveal a magical trail leading to the next thing required to complete the quest."
        ),
        "duration": "10 Minutes",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "dotted_line",
                "duration_minutes": 10,
                "check": {
                    "stat": "perception",
                    "skill": "Follow the Dotted Line",
                    "difficulty_from_metadata": "tier",
                },
                "reveals": "next_quest_objective",
                "source_ability": "Follow the Dotted Line",
            },
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Forced March",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "You and chosen party members gain a bonus to walking and running totals equal to "
            "Forced March level."
        ),
        "duration": "1 Hour",
        "effects": apply_state(
            "forced_march_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": 1,
                "walking_bonus": _ability_level(source, "Forced March"),
                "running_bonus": _ability_level(source, "Forced March"),
                "per_person_cost": 10,
                "cost_pool": "stamina",
                "source_ability": "Forced March",
            },
        ),
        "required_level": 5,
        "scales_with_level": True,
        "target": "party",
        "type": "skill",
    },

    {
        "name": "Secure the Perimeter",
        "cost": 20,
        "cost_pool": "fortune",
        "description": (
            "Checks a valid campsite for hidden creatures or dangers within the chosen perimeter."
        ),
        "duration": "1 Action",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "camp_perimeter_scan",
                "requires_valid_campsite": True,
                "check": {
                    "stat": "perception",
                    "skill": "Secure the Perimeter",
                    "gm_roll": True,
                },
                "reveals": ("hidden_creatures", "hidden_dangers"),
                "source_ability": "Secure the Perimeter",
            },
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Set Spears",
        "cost": 25,
        "cost_pool": "stamina",
        "description": (
            "The Mercenary and all party members may make a free attack when an enemy moves next "
            "to them. If the attack hits, add Set Spears level to the damage inflicted."
        ),
        "duration": "1 Turn",
        "effects": apply_state(
            "set_spears_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": 1,
                "trigger": "enemy_moves_adjacent",
                "grants_free_attack": True,
                "damage_bonus_on_hit": _ability_level(source, "Set Spears"),
                "applies_to_party": True,
                "counts_charge_as_trigger": True,
                "source_ability": "Set Spears",
            },
        ),
        "required_level": 10,
        "scales_with_level": True,
        "target": "party",
        "type": "skill",
    },

    {
        "name": "Switch Ranks",
        "cost": 25,
        "cost_pool": "fortune",
        "description": (
            "Trade places with a party member within a number of feet equal to Switch Ranks level."
        ),
        "duration": "1 Action",
        "effects": apply_state(
            "switch_ranks_active",
            value_fn=lambda source: {
                "active": True,
                "swap_positions": True,
                "max_range_feet": _ability_level(source, "Switch Ranks"),
                "requires_party_target": True,
                "source_ability": "Switch Ranks",
            },
        ),
        "required_level": 10,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    # Level 15

    {"grant": "Bodyguard", "required_level": 15},

    {"grant": "Pillage", "required_level": 15},

    # Level 20

    {"grant": "Get That Guy!", "required_level": 20},

    {
        "name": "Vengeance",
        "cost": 50,
        "cost_pool": "stamina",
        "description": (
            "After any pool except Fortune is reduced to zero, you may take one action before being taken out. "
            "This skill has no levels."
        ),
        "duration": "Instant",
        "effects": apply_state(
            "vengeance_ready",
            value_fn=lambda source: {
                "active": True,
                "trigger": "non_fortune_pool_reduced_to_zero",
                "grant_final_action": True,
                "source_ability": "Vengeance",
            },
        ),
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Long-Term Contract",
        "cost": 100,
        "cost_pool": "fortune",
        "description": (
            "A written contract binds its signers. Anyone trying to violate it must roll Wisdom "
            "against your Perception plus Long-Term Contract skill or lose 100 Fortune permanently."
        ),
        "duration": "Until Canceled",
        "effects": apply_state(
            "long_term_contract_active",
            value_fn=lambda source: {
                "active": True,
                "requires_signed_contract": True,
                "violation_check": {
                    "challenger_stat": "wisdom",
                    "defender_stat": "perception",
                    "defender_skill": "Long-Term Contract",
                },
                "failure_penalty": {
                    "fortune_loss": 100,
                    "permanent": True,
                },
                "source_ability": "Long-Term Contract",
            },
        ),
        "required_level": 25,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Named and Feared",
        "description": (
            "On the battlefield, enemies who wish to attack you must roll Willpower against your Luck. "
            "Failure forces them to choose another target if one is available. Fearless foes are immune."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_named_and_feared_modifier),
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

], source_type="adventure")