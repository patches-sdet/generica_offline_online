from domain.abilities.builders._job_builder import build_job
from domain.abilities import ability_level, ctx_ability_level, progression_level, ctx_progression_level
from domain.abilities.patterns import (
    apply_state,
    inspect,
    passive_modifier,
)


# Local helpers

def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


# Passive helpers

def _noblesse_oblige_modifier(source) -> None:
    states = _ensure_states(source)
    states["noblesse_oblige"] = {
        "active": True,
        "applies_to": ("sworn_subjects", "party_members"),
        "buff_stat": "highest_attribute",
        "buff_amount": progression_level(source, "adventure", "Ruler"),
        "source_ability": "Noblesse Oblige",
    }


def _its_good_to_be_king_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["its_good_to_be_king"] = {
        "active": True,
        "gain_experience_from_subjects": True,
        "higher_level_subject_significant_quest_grants_ruler_level_point": True,
        "lower_level_subject_rewards_feed_kings_quest_tokens": True,
        "token_table": {
            "1-100": 1,
            "101-1000": 2,
            "1001-5000": 4,
            "5001-25000": 8,
            "25001-100000": 16,
            "100001+": 32,
        },
        "source_ability": "It's Good to be King",
    }


build_job("Ruler", [

    # Level 1

    {
        "name": "Emboldening Speech",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "Buff all allies within earshot, increasing Moxie and Sanity by Charisma divided by five "
            "plus Emboldening Speech level. Requires a full turn to activate."
        ),
        "duration": "1 Minute per Ruler Level",
        "effects": apply_state(
            "emboldening_speech_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Ruler"),
                "requires_full_turn": True,
                "cannot_do_anything_else_while_activating": True,
                "affects_allies_within_earshot": True,
                "moxie_bonus": (source.get_stat("charisma", 0) // 5) + ability_level(source, "Emboldening Speech"),
                "sanity_bonus": (source.get_stat("charisma", 0) // 5) + ability_level(source, "Emboldening Speech"),
                "source_ability": "Emboldening Speech",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Identify Subject",
        "cost": 5,
        "cost_pool": "moxie",
        "description": (
            "Examine a sworn subject's status screen, or inspect a party member with greater detail."
        ),
        "duration": "5 Minutes",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "identify_subject",
                "valid_targets": ("sworn_subject", "party_member"),
                "reveals": (
                    "subject_status_screen",
                    "expanded_party_status_information",
                ),
                "hidden_check_for_concealed_status": {
                    "stat": "wisdom",
                    "skill": "Identify Subject",
                    "gm_secret_roll": True,
                },
                "source_ability": "Identify Subject",
            },
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Noblesse Oblige",
        "description": (
            "Buff all sworn subjects and party members, increasing your highest attribute by your Ruler level."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_noblesse_oblige_modifier),
        "required_level": 1,
        "scales_with_level": False,
        "target": "party",
        "type": "passive",
    },

    {
        "name": "Royal Audience",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "Buff your Charisma by this skill's level, but only when dealing with sworn subjects."
        ),
        "duration": "1 Minute per Ruler Level",
        "effects": apply_state(
            "royal_audience_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Ruler"),
                "charisma_bonus": ability_level(source, "Royal Audience"),
                "only_applies_with_sworn_subjects": True,
                "source_ability": "Royal Audience",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Simple Decree",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "Declare a simple command in twelve words or less. Violators among your subjects take moxie damage."
        ),
        "duration": "Permanent until Changed",
        "effects": apply_state(
            "simple_decree_active",
            value_fn=lambda source: {
                "active": True,
                "max_words": 12,
                "all_subjects_notified": True,
                "violation_moxie_damage": (
                    (source.get_stat("charisma", 0) + source.get_stat("wisdom", 0)) // 2
                ),
                "damage_reduced_by_target_cool": True,
                "only_one_simple_decree": True,
                "cannot_require_suicide_or_self_harm": True,
                "self_harmful_decrees_may_be_ignored": True,
                "source_ability": "Simple Decree",
            },
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Appoint Official",
        "cost": 25,
        "cost_pool": "moxie",
        "description": (
            "Appoint one official per Ruler level. Officials may accept oaths of fealty on your behalf."
        ),
        "duration": "Permanent until Changed",
        "effects": apply_state(
            "appoint_official_active",
            value_fn=lambda source: {
                "active": True,
                "official_limit": progression_level(source, "adventure", "Ruler"),
                "official_must_be_subject": True,
                "officials_may_accept_fealty": True,
                "accepted_subjects_join_your_subject_pool": True,
                "source_ability": "Appoint Official",
            },
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Organize Minions",
        "cost": 15,
        "cost_pool": "moxie",
        "description": (
            "Assign one shared quest. While working toward it, your party members or subjects gain "
            "a bonus to all attributes equal to your Ruler level."
        ),
        "duration": "Permanent until Changed",
        "effects": apply_state(
            "organize_minions_active",
            value_fn=lambda source: {
                "active": True,
                "choose_one_shared_quest": True,
                "applies_while_working_toward_quest": True,
                "affects": ("party_members", "subjects"),
                "all_attribute_bonus": progression_level(source, "adventure", "Ruler"),
                "only_one_organized_task": True,
                "source_ability": "Organize Minions",
            },
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    {
        "name": "Swear Fealty",
        "cost": 0,
        "cost_pool": None,
        "description": (
            "Allow an individual to become your subject by spending five Moxie in your presence "
            "or the presence of an appointed official."
        ),
        "duration": "Permanent until Changed",
        "effects": apply_state(
            "swear_fealty_active",
            value_fn=lambda source: {
                "active": True,
                "subject_spends_moxie": 5,
                "requires_presence_of_ruler_or_official": True,
                "joins_subject_pool_on_success": True,
                "enables_other_ruler_effects": True,
                "source_ability": "Swear Fealty",
            },
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    # Level 10

    {
        "name": "It's Good to be King",
        "description": (
            "Gain indirect experience from your subjects and accumulate free level-point tokens for King's Quest rewards."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_its_good_to_be_king_modifier),
        "required_level": 10,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "King's Quest",
        "cost": 20,
        "cost_pool": "moxie",
        "description": (
            "Declare a public quest. Subjects within earshot may accept it. Only one King's Quest may be active at a time."
        ),
        "duration": "Permanent until Canceled or Fulfilled",
        "effects": apply_state(
            "kings_quest_active",
            value_fn=lambda source: {
                "active": True,
                "public_quest_declared": True,
                "subjects_within_earshot_may_accept": True,
                "rewards_granted_immediately_on_completion": True,
                "does_not_count_toward_normal_quest_limit": True,
                "only_one_active_kings_quest": True,
                "may_only_be_announced_once_per_month": True,
                "source_ability": "King's Quest",
            },
        ),
        "required_level": 10,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Kingsguard",
        "cost": 50,
        "cost_pool": "fortune",
        "description": (
            "Promote party members to Kingsguard, granting weapon skill and pool bonuses."
        ),
        "duration": "Until you Rest",
        "effects": apply_state(
            "kingsguard_active",
            value_fn=lambda source: {
                "active": True,
                "promote_one_or_more_party_members": True,
                "weapon_skill_bonus": progression_level(source, "adventure", "Ruler"),
                "pool_bonus": source.get_stat("charisma", 0),
                "source_ability": "Kingsguard",
            },
        ),
        "required_level": 15,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Proclaim Treaty",
        "cost": 200,
        "cost_pool": "moxie",
        "description": (
            "Declare a treaty with a nation or organization. Subjects gain social bonuses with them "
            "and penalties when attacking them."
        ),
        "duration": "Permanent until Dismissed",
        "effects": apply_state(
            "proclaim_treaty_active",
            value_fn=lambda source: {
                "active": True,
                "choose_nation_or_organization": True,
                "all_subjects_notified": True,
                "attack_roll_penalty_against_treaty_group": progression_level(source, "adventure", "Ruler"),
                "charisma_bonus_with_treaty_group": progression_level(source, "adventure", "Ruler"),
                "perception_bonus_with_treaty_group": progression_level(source, "adventure", "Ruler"),
                "source_ability": "Proclaim Treaty",
            },
        ),
        "required_level": 15,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Complex Decree",
        "cost": 100,
        "cost_pool": "moxie",
        "description": (
            "Declare a command of 100 words or less. Violators among your subjects take moxie damage."
        ),
        "duration": "Permanent until Changed",
        "effects": apply_state(
            "complex_decree_active",
            value_fn=lambda source: {
                "active": True,
                "max_words": 100,
                "all_subjects_notified": True,
                "violation_moxie_damage": (
                    source.get_stat("charisma", 0) + source.get_stat("wisdom", 0)
                ),
                "damage_reduced_by_target_cool": True,
                "only_one_complex_decree": True,
                "cannot_require_suicide_or_self_harm": True,
                "self_harmful_decrees_may_be_ignored": True,
                "source_ability": "Complex Decree",
            },
        ),
        "required_level": 20,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    {
        "name": "Royal Quest",
        "cost": 80,
        "cost_pool": "moxie",
        "description": (
            "As King's Quest, but instantly notifies all subjects and party members."
        ),
        "duration": "Permanent until Canceled or Fulfilled",
        "effects": apply_state(
            "royal_quest_active",
            value_fn=lambda source: {
                "active": True,
                "quest_behaves_like_kings_quest": True,
                "all_subjects_notified_instantly": True,
                "all_party_members_notified_instantly": True,
                "does_not_count_toward_normal_quest_limit": True,
                "can_be_fueled_by_kings_quest_level_tokens": True,
                "source_ability": "Royal Quest",
            },
        ),
        "required_level": 20,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Claim Domain",
        "cost": 250,
        "cost_pool": "moxie",
        "description": (
            "Claim unruled land by planting and maintaining a flag for a full week."
        ),
        "duration": "Permanent until Conquered",
        "effects": apply_state(
            "claim_domain_active",
            value_fn=lambda source: {
                "active": True,
                "requires_unruled_land": True,
                "requires_flag_in_public_central_location": True,
                "flag_must_stand_for_days": 7,
                "land_becomes_claimed_on_success": True,
                "non_enemies_in_domain_become_subjects": True,
                "self_attribute_bonus_in_domain": progression_level(source, "adventure", "Ruler"),
                "self_defense_bonus_in_domain": progression_level(source, "adventure", "Ruler"),
                "source_ability": "Claim Domain",
            },
        ),
        "required_level": 25,
        "scales_with_level": False,
        "target": "area",
        "type": "skill",
    },

    {
        "name": "Declaration of War",
        "cost": 200,
        "cost_pool": "moxie",
        "description": (
            "Declare war on a species or organization. Your subjects and party gain combat bonuses against them."
        ),
        "duration": "Permanent until Changed",
        "effects": apply_state(
            "declaration_of_war_active",
            value_fn=lambda source: {
                "active": True,
                "choose_enemy_species_or_organization": True,
                "affects": ("subjects", "party_members"),
                "attack_roll_bonus_against_declared_enemy": progression_level(source, "adventure", "Ruler"),
                "defense_bonus_against_declared_enemy": progression_level(source, "adventure", "Ruler"),
                "source_ability": "Declaration of War",
            },
        ),
        "required_level": 25,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

], source_type="adventure")