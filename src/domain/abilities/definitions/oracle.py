from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    inspect,
    passive_modifier,
    scaled_derived_buff,
)


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _oracle_level(character) -> int:
    return character.get_progression_level("adventure", "Oracle", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


# Passive helpers

def _omens_and_portents_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["omens_and_portents"] = {
        "active": True,
        "receives_divine_signs": True,
        "omens_may_arrive_as": (
            "dreams",
            "visions",
            "symbols",
            "patterns",
            "other_divine_signs",
        ),
        "omens_hint_at_future": True,
        "omens_require_interpretation": True,
        "source_ability": "Omens and Portents",
    }


build_job("Oracle", [

    # Level 1

    {
        "name": "Absorb Condition",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "Transfer a condition or debuff from a touched target to yourself. "
            "The absorbed affliction naturally fades after one day if not cured first."
        ),
        "duration": "1 Action",
        "effects": apply_state(
            "absorb_condition_active",
            value_fn=lambda source: {
                "active": True,
                "requires_touch": True,
                "transfer_condition_or_debuff_to_self": True,
                "does_not_restore_drained_pools": True,
                "absorbed_condition_auto_fades_after_hours": 24,
                "source_ability": "Absorb Condition",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "ally or self",
        "type": "skill",
    },

    {
        "name": "Diagnose",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Reveal all debuffs and conditions affecting a target."
        ),
        "duration": "1 Action",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "diagnose",
                "reveals": (
                    "all_debuffs",
                    "all_conditions",
                ),
                "never_fails": True,
                "source_ability": "Diagnose",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "ally or enemy",
        "type": "skill",
    },

    {
        "name": "Divine Pawn",
        "description": (
            "Gain a bonus to Fate equal to Oracle level."
        ),
        "duration": "Passive Constant",
        "effects": scaled_derived_buff(
            scale_fn=_oracle_level,
            stat="fate",
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Foresight",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "Add this skill's level to one roll on your next turn. "
            "If that roll fails, you cannot use Foresight again for the rest of the day."
        ),
        "duration": "1 Turn",
        "effects": apply_state(
            "foresight_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": 1,
                "bonus_to_next_roll": _ability_level(source, "Foresight"),
                "on_failed_buffed_roll": {
                    "lockout_duration": "rest_of_day",
                    "locked_ability": "Foresight",
                },
                "source_ability": "Foresight",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {"grant": "Lesser Healing", "required_level": 1},

    # Level 5

    {
        "name": "Afflict Self",
        "cost": 5,
        "cost_pool": "fortune",
        "description": (
            "Randomly inflict yourself with a condition for the duration, unless cured sooner."
        ),
        "duration": "1 Turn per Skill Level",
        "effects": apply_state(
            "afflict_self_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": _ability_level(source, "Afflict Self"),
                "random_condition_table": {
                    "1-9": "Bleeding",
                    "10-19": "Blinded",
                    "20-29": "Burning",
                    "30-39": "Deafened",
                    "40-49": "Drunk",
                    "50-59": "Gassy",
                    "60-69": "Hobbled",
                    "70-79": "Hungover",
                    "80-89": "Numb",
                    "90-99": "Slowed",
                    "00": "Choose any condition and roll again",
                },
                "condition_ends_if_cured_or_duration_expires": True,
                "source_ability": "Afflict Self",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Omens and Portents",
        "description": (
            "Receive symbolic divine signs that hint at the future."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_omens_and_portents_modifier),
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Transfer Condition",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Transfer one of your current conditions or debuffs to another target with a boosted brawling touch."
        ),
        "duration": "1 Turn",
        "effects": apply_state(
            "transfer_condition_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": 1,
                "choose_from_current_afflictions": True,
                "requires_touch_attack": True,
                "touch_attack_stat_options": ("strength", "dexterity"),
                "touch_attack_skill_bonus": _ability_level(source, "Transfer Condition"),
                "preserves_original_duration": True,
                "source_ability": "Transfer Condition",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "enemy or ally",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Influence Fate",
        "cost": 25,
        "cost_pool": "fortune",
        "description": (
            "Choose an ally you can communicate with. On their next turn, they may add this skill's level to one roll."
        ),
        "duration": "1 Turn",
        "effects": apply_state(
            "influence_fate_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": 1,
                "requires_communicable_ally": True,
                "ally_bonus_to_single_roll": _ability_level(source, "Influence Fate"),
                "source_ability": "Influence Fate",
            },
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Short Vision",
        "cost": 25,
        "cost_pool": "sanity",
        "description": (
            "Enter a trance to seek answers from your god, then remain unconscious for a random duration."
        ),
        "duration": "01-100 Minutes",
        "effects": apply_state(
            "short_vision_active",
            value_fn=lambda source: {
                "active": True,
                "question_guided_vision": True,
                "check": {
                    "stat": "wisdom",
                    "skill": "Short Vision",
                    "difficulty": "gm_defined_minimum_150",
                },
                "knocks_caster_unconscious": True,
                "unconscious_duration_minutes": "1d100",
                "cannot_wake_until_vision_ends": True,
                "source_ability": "Short Vision",
            },
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Grant Vision",
        "cost": 30,
        "cost_pool": "fortune",
        "description": (
            "Grant a vision to a willing target. Only one granted vision may be active at a time."
        ),
        "duration": "01-100 Minutes",
        "effects": apply_state(
            "grant_vision_active",
            value_fn=lambda source: {
                "active": True,
                "requires_touch": True,
                "requires_willing_target": True,
                "grants_short_vision_like_effect": True,
                "target_uses_wisdom_roll_for_answers": True,
                "only_one_granted_vision_at_a_time": True,
                "ties_up_ability_until_target_finishes": True,
                "unconscious_duration_minutes": "1d100",
                "source_ability": "Grant Vision",
            },
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Random Buff",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "Grant a random buff to yourself or a willing touched target."
        ),
        "duration": "1 Turn per Oracle Level",
        "effects": apply_state(
            "random_buff_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": _oracle_level(source),
                "requires_touch": True,
                "willing_target_or_self": True,
                "buff_amount": _ability_level(source, "Random Buff"),
                "random_table": {
                    "1-2": "All physical attributes",
                    "3-4": "All mental attributes",
                    "5-6": "Perception and luck",
                    "7-8": "All pools",
                    "9-10": "All defenses",
                },
                "source_ability": "Random Buff",
            },
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": True,
        "target": "ally or self",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Trance",
        "cost": 40,
        "cost_pool": "sanity",
        "description": (
            "Overwhelm a target with visions, inflicting Paralyzed, Blinded, and Deafened."
        ),
        "duration": "1 Turn per Oracle Level",
        "effects": apply_state(
            "trance_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": _oracle_level(source),
                "contest": {
                    "caster_stat": "charisma",
                    "caster_skill": "Trance",
                    "target_stat": "willpower",
                },
                "on_success_conditions": (
                    "Paralyzed",
                    "Blinded",
                    "Deafened",
                ),
                "damage_break_check": {
                    "target_stat": "willpower",
                    "difficulty": "caster_charisma_plus_trance_skill",
                },
                "source_ability": "Trance",
            },
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Unerring Strike",
        "cost": 40,
        "cost_pool": "fortune",
        "description": (
            "For the next turn, your attacks automatically strike, but would-be misses cost Fortune."
        ),
        "duration": "1 Turn",
        "effects": apply_state(
            "unerring_strike_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": 1,
                "attacks_auto_hit": True,
                "still_requires_attack_roll": True,
                "on_roll_that_would_miss": {
                    "take_fortune_damage_equal_to_margin_of_failure": True,
                    "until_minimum_hit_threshold_reached": True,
                },
                "source_ability": "Unerring Strike",
            },
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Rewind Time",
        "cost": 100,
        "cost_pool": "fortune",
        "description": (
            "Negate the results of a completed turn and allow the target to act again. May be used once per day."
        ),
        "duration": "Instant",
        "effects": apply_state(
            "rewind_time_ready",
            value_fn=lambda source: {
                "active": True,
                "trigger": "immediately_after_turn_resolves",
                "negate_turn_results": True,
                "target_may_retry_or_choose_new_actions": True,
                "once_per_day": True,
                "source_ability": "Rewind Time",
            },
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "ally or self",
        "type": "skill",
    },

    {
        "name": "Truesight",
        "cost": 100,
        "cost_pool": "sanity",
        "description": (
            "See through darkness, obscurity, illusions, and resist coercion of mind or senses."
        ),
        "duration": "1 Turn per Oracle Level",
        "effects": apply_state(
            "truesight_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": _oracle_level(source),
                "see_in_total_darkness": True,
                "ignore_obscurement": True,
                "cannot_be_fooled_by_illusions": True,
                "immune_to_mind_or_sense_coercion": True,
                "source_ability": "Truesight",
            },
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

], source_type="adventure")