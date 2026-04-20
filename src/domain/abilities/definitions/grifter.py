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

def _grifter_level(character) -> int:
    return character.get_progression_level("adventure", "Grifter", 0)

def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states

# Passive helpers

def _mega_moxie_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["mega_moxie"] = {
        "active": True,
        "max_moxie_percent_bonus": _grifter_level(ctx.source),
        "source_ability": "Mega-Moxie",
    }

build_job("Grifter", [

    # Level 1

    {
        "name": "Fools Gold",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "Create one temporary false gold coin per Grifter level. The coins register as magical, "
            "then dissipate later. Observers may realize the deception by rolling Perception against your Charisma."
        ),
        "duration": "10 Minutes per Skill Level",
        "effects": apply_state(
            "fools_gold_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _ability_level(source, "Fools Gold") * 10,
                "temporary_gold_coins": _grifter_level(source),
                "coins_are_false": True,
                "detect_as_magical": True,
                "dissipates_after_duration": True,
                "pierce_check": {
                    "observer_stat": "perception",
                    "grifter_stat": "charisma",
                },
                "source_ability": "Fools Gold",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Master of Disguise",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "Assume a masterful disguise. Those trying to pierce it roll Perception against your "
            "Charisma plus Master of Disguise level."
        ),
        "duration": "10 Minutes per Skill Level",
        "effects": apply_state(
            "master_of_disguise_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _ability_level(source, "Master of Disguise") * 10,
                "pierce_check": {
                    "observer_stat": "perception",
                    "grifter_stat": "charisma",
                    "grifter_skill": "Master of Disguise",
                },
                "extraordinary_difference_may_increase_difficulty": True,
                "source_ability": "Master of Disguise",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Silent Activation",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "Silently activate another skill by taking an action and spending moxie first. "
            "Observers watching your face may notice the lip movement."
        ),
        "duration": "1 Skill Activation",
        "effects": apply_state(
            "silent_activation_ready",
            value_fn=lambda source: {
                "active": True,
                "applies_to_next_skill_activation": True,
                "requires_action": True,
                "lip_movement_detectable": True,
                "detection_check": {
                    "observer_watching_face_required": True,
                    "grifter_stat": "charisma",
                    "grifter_skill": "Silent Activation",
                },
                "source_ability": "Silent Activation",
            },
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Silver Tongue",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "Buff your Charisma by this skill's level, but only for lies."
        ),
        "duration": "10 Minutes per Skill Level",
        "effects": apply_state(
            "silver_tongue_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _ability_level(source, "Silver Tongue") * 10,
                "charisma_bonus_for_lies": _ability_level(source, "Silver Tongue"),
                "source_ability": "Silver Tongue",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Size Up",
        "cost": 5,
        "cost_pool": "fortune",
        "description": (
            "Roll Luck plus Size Up against the target's Willpower. On success, learn their Charisma, "
            "Perception, Willpower, Wisdom, and detection/observation skills relevant to deception."
        ),
        "duration": "1 Turn",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "size_up_target",
                "contest": {
                    "caster_stat": "luck",
                    "caster_skill": "Size Up",
                    "target_stat": "willpower",
                },
                "reveals": (
                    "charisma",
                    "perception",
                    "willpower",
                    "wisdom",
                    "detection_skills",
                    "observation_skills",
                ),
                "focus": "traits_that_interfere_with_lies_or_deceptions",
                "source_ability": "Size Up",
            },
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Forgery",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "Create a convincing false document such as a license, authorization, or permit. "
            "Appraise and similar item-reading skills see through it."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "forgery_active",
            value_fn=lambda source: {
                "active": True,
                "creates_false_document": True,
                "valid_document_types": (
                    "license",
                    "authorization",
                    "official_document",
                    "permit",
                ),
                "pierce_check": {
                    "observer_stat": "perception",
                    "grifter_stat": "dexterity",
                    "grifter_skill": "Forgery",
                },
                "item_reading_skills_bypass_deception": True,
                "source_ability": "Forgery",
            },
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Pickpocket",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "Gain a Dexterity bonus for sleight-of-hand or pickpocketing attempts."
        ),
        "duration": "1 Attempt",
        "effects": apply_state(
            "pickpocket_active",
            value_fn=lambda source: {
                "active": True,
                "applies_to_next_attempt": True,
                "dexterity_bonus_for_pickpocketing": _ability_level(source, "Pickpocket"),
                "dexterity_bonus_for_sleight_of_hand": _ability_level(source, "Pickpocket"),
                "pairs_well_with": "Silent Activation",
                "source_ability": "Pickpocket",
            },
        ),
        "required_level": 5,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Unflappable",
        "description": (
            "Gain a bonus to Cool equal to Grifter level."
        ),
        "duration": "Passive Constant",
        "effects": scaled_derived_buff(
            scale_fn=_grifter_level,
            stat="cool",
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Level 10

    {
        "name": "Feign Death",
        "cost": 20,
        "cost_pool": "moxie",
        "description": (
            "Appear dead until the effect ends. Anyone failing to pierce the bluff believes you are dead."
        ),
        "duration": "5 Minutes per Grifter Level",
        "effects": apply_state(
            "feign_death_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _grifter_level(source) * 5,
                "appear_dead": True,
                "pierce_check": {
                    "observer_stat": "perception",
                    "grifter_stat": "charisma",
                    "grifter_skill": "Feign Death",
                },
                "ends_if_you_move_or_speak": True,
                "source_ability": "Feign Death",
            },
        ),
        "required_level": 10,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Old Buddy",
        "cost": 25,
        "cost_pool": "moxie",
        "description": (
            "Convince a target that you are an old friend. Success makes them moderately friendly "
            "in most non-combat situations until the effect expires."
        ),
        "duration": "1 Minute per Grifter Level",
        "effects": apply_state(
            "old_buddy_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _grifter_level(source),
                "contest": {
                    "caster_stat": "charisma",
                    "caster_skill": "Old Buddy",
                    "target_stat": "intelligence",
                },
                "target_believes_old_friend": True,
                "moderately_friendly_in_noncombat": True,
                "weak_in_combat_or_high_tension_scenes": True,
                "target_realizes_truth_when_effect_ends": True,
                "source_ability": "Old Buddy",
            },
        ),
        "required_level": 10,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Bluster",
        "cost": 30,
        "cost_pool": "moxie",
        "description": (
            "Distract loudly, granting your party bonuses to Mental Fortitude, Cool, Perception, and Willpower "
            "equal to your Grifter level. While active, you cannot use speech-requiring skills."
        ),
        "duration": "Until Ceased",
        "effects": apply_state(
            "bluster_active",
            value_fn=lambda source: {
                "active": True,
                "party_buff_amount": _grifter_level(source),
                "buffs": {
                    "mental_fortitude": _grifter_level(source),
                    "cool": _grifter_level(source),
                    "perception": _grifter_level(source),
                    "willpower": _grifter_level(source),
                },
                "does_not_affect_self": True,
                "cannot_use_speech_required_skills": True,
                "source_ability": "Bluster",
            },
        ),
        "required_level": 15,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    {
        "name": "Mega-Moxie",
        "description": (
            "Gain a bonus to max moxie equal to your Grifter level as a percentage."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_mega_moxie_modifier),
        "required_level": 15,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Level 20

    {
        "name": "Fake it to Make it 10",
        "cost": 50,
        "cost_pool": "fortune",
        "description": (
            "Temporarily mimic another adventuring or crafting job's level 10 non-passive skill. "
            "Only one faked skill may be active at a time."
        ),
        "duration": "Varies",
        "effects": apply_state(
            "fake_it_to_make_it_10_active",
            value_fn=lambda source: {
                "active": True,
                "base_cost": 50,
                "plus_copied_skill_cost": True,
                "mimic_other_job_skill": True,
                "max_skill_level_to_copy": 10,
                "cannot_copy_passive_constant_skills": True,
                "copied_skill_uses_this_skill_level": _ability_level(source, "Fake it to Make it 10"),
                "duration": "copied_skill_duration_or_until_rest",
                "only_one_faked_skill_active": True,
                "source_ability": "Fake it to Make it 10",
            },
        ),
        "required_level": 20,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Shout Down",
        "cost": 50,
        "cost_pool": "moxie",
        "description": (
            "A vocal attack that damages both sanity and moxie if your Charisma plus Shout Down "
            "beats the target's Wisdom and Willpower."
        ),
        "duration": "1 Attack",
        "effects": apply_state(
            "shout_down_active",
            value_fn=lambda source: {
                "active": True,
                "attack_stat": "charisma",
                "attack_skill": "Shout Down",
                "target_defenses": ("wisdom", "willpower"),
                "damage_pools": ("sanity", "moxie"),
                "damage_amount": "margin_of_success",
                "reduced_by": ("mental_fortitude", "cool"),
                "source_ability": "Shout Down",
            },
        ),
        "required_level": 20,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Scoundrel's Luck",
        "cost": 100,
        "cost_pool": "fortune",
        "description": (
            "When you fail a roll, immediately reroll it and keep the second result. "
            "This may only be used once per roll."
        ),
        "duration": "Instant",
        "effects": apply_state(
            "scoundrels_luck_ready",
            value_fn=lambda source: {
                "active": True,
                "trigger": "failed_roll",
                "grant_immediate_reroll": True,
                "must_keep_second_result": True,
                "once_per_roll": True,
                "source_ability": "Scoundrel's Luck",
            },
        ),
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Shift Blame",
        "cost": 100,
        "cost_pool": "moxie",
        "description": (
            "Convince a target that someone else is to blame. If successful, they must direct their next turn's "
            "frustration at that blamed target. A target cannot be affected more than once per encounter."
        ),
        "duration": "1 Attack",
        "effects": apply_state(
            "shift_blame_active",
            value_fn=lambda source: {
                "active": True,
                "attack_stat": "charisma",
                "attack_skill": "Shift Blame",
                "target_defense": "perception",
                "choose_blame_target": True,
                "on_success": {
                    "target_blames_chosen_target": True,
                    "must_attack_or_act_against_blame_target_next_turn": True,
                    "behavior_still_must_fit_setting_and_disposition": True,
                },
                "blame_fades_after_first_attack": True,
                "once_per_target_per_encounter": True,
                "source_ability": "Shift Blame",
            },
        ),
        "required_level": 25,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

], source_type="adventure")