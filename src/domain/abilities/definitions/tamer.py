from domain.abilities.builders._job_builder import build_job
from domain.abilities import ability_level, ctx_ability_level, progression_level, ctx_progression_level
from domain.abilities.patterns import (
    apply_state,
    heal_hp,
    inspect,
    passive_modifier,
)
from domain.effects.special.minions import GrantControlledGroupMembershipEffect


# Local helpers

def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


def _truce_modifier_factory(creature_type: str, ability_name: str):
    def modifier(ctx) -> None:
        states = _ensure_states(ctx.source)
        states[f"{ability_name.lower().replace(' ', '_')}_active"] = {
            "active": True,
            "truce_type": creature_type,
            "attacker_must_roll": {
                "attacker_stat": "willpower",
                "defender_stat": "charisma",
            },
            "one_attempt_per_turn": True,
            "success_allows_attacks_for_rest_of_day": True,
            "only_one_truce_active_at_a_time": True,
            "switching_truce_requires_full_turn_uninterrupted_concentration": True,
            "source_ability": ability_name,
        }
    return modifier


build_job("Tamer", [

    # Level 1

    {
        "name": "Analyze Monster",
        "cost": 5,
        "cost_pool": "fortune",
        "description": (
            "Examine a beast or monster's status screen."
        ),
        "duration": "1 Minute",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "analyze_monster",
                "contest": {
                    "caster_stat": "perception",
                    "caster_skill": "Analyze Monster",
                    "target_stat": "willpower",
                },
                "reveals": "monster_status_screen",
                "valid_targets": ("beast", "monster"),
                "source_ability": "Analyze Monster",
            },
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Bake Monster Treats",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "Bake treats for a chosen monster type. Each treat increases a tamed creature's loyalty by 10%."
        ),
        "duration": "1 Hour per Tamer Level",
        "effects": apply_state(
            "bake_monster_treats_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": progression_level(source, "adventure", "Tamer"),
                "choose_monster_type": True,
                "ingredient_cost_copper": 2,
                "baking_roll": {
                    "stat": "intelligence",
                    "skill": "Bake Monster Treats",
                    "bonus_skill_if_present": "Cooking",
                },
                "treats_created": "one_per_full_20_on_roll",
                "each_treat_increases_loyalty_percent": 10,
                "source_ability": "Bake Monster Treats",
            },
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Beast Truce",
        "description": (
            "Convince beasts that you are nonthreatening."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_truce_modifier_factory("beast", "Beast Truce")),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Tame Monster",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "Attempt to bond with a tameable creature and make it your companion."
        ),
        "duration": "Permanent",
        "effects": GrantControlledGroupMembershipEffect(
            tag="tamed_companion",
            condition=lambda ctx, target: True,
            controller_state_key="controller",
            extra_state={
                "tamed_by_skill": "Tame Monster",
                "requires_tameable_target": True,
                "fails_if_target_is_actively_fighting": True,
                "contest": {
                    "caster_stat": "charisma",
                    "caster_skill": "Tame Monster",
                    "target_stats": ("wisdom", "willpower"),
                },
                "bonus_to_tame_roll_per_10_percent_missing_hp": 10,
                "sets_loyalty_percent": 50,
                "delevels_target_to_tamer_level_if_higher": True,
                "may_shrink_if_level_gap_is_large": True,
                "loyalty_check_required_in_desperate_situations": True,
                "loyalty_failure_threshold": 100,
                "may_refuse_orders_or_break_bond_on_low_loyalty": True,
                "treatment_affects_loyalty": True,
                "companion_may_gain_levels_and_grind_points": True,
                "source_ability": "Tame Monster",
            },
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Track Monster",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "Track an identified creature or search for tracks of a chosen creature category."
        ),
        "duration": "1 Hour per Level",
        "effects": apply_state(
            "track_monster_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": ability_level(source, "Track Monster"),
                "modes": {
                    "follow_identified_tracks": {
                        "perception_bonus": ability_level(source, "Track Monster"),
                    },
                    "search_for_creature_category": {
                        "roll": {
                            "stat": "luck",
                            "skill": "Track Monster",
                        },
                        "finds_appropriate_creature_for_area": True,
                    },
                },
                "source_ability": "Track Monster",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Bug Truce",
        "description": (
            "Convince bugs and related creatures that you are neither hostile nor prey."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_truce_modifier_factory("bug", "Bug Truce")),
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {"grant": "Friendly Smile", "required_level": 5},

    {
        "name": "Heal Monster",
        "cost": 20,
        "cost_pool": "moxie",
        "description": (
            "Heal one of your tamed companions."
        ),
        "duration": "1 Action",
        "effects": heal_hp(
            scale_fn=lambda source: (progression_level(source, "adventure", "Tamer") * 2) + ability_level(source, "Heal Monster"),
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Beast Eye",
        "cost": 20,
        "cost_pool": "fortune",
        "description": (
            "See through the eyes of one of your tamed companions."
        ),
        "duration": "1 Minute",
        "effects": apply_state(
            "beast_eye_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": 1,
                "requires_tamed_companion_target": True,
                "share_companion_vision": True,
                "source_ability": "Beast Eye",
            },
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Force Feed",
        "cost": 20,
        "cost_pool": "stamina",
        "description": (
            "Force-feed monster treats to a target monster to improve your next taming attempt."
        ),
        "duration": "Instant",
        "effects": apply_state(
            "force_feed_active",
            value_fn=lambda source: {
                "active": True,
                "requires_monster_treats": True,
                "touch_delivery_check": {
                    "caster_stat": "dexterity",
                    "caster_skill": "Force Feed",
                },
                "each_correct_treat_grants_bonus_to_next_tame_roll": 10,
                "wrong_treat_has_no_effect_and_annoys_target": True,
                "source_ability": "Force Feed",
            },
        ),
        "required_level": 10,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Plant Truce",
        "description": (
            "Convince plants and related creatures that you are beneficial rather than hostile."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_truce_modifier_factory("plant", "Plant Truce")),
        "required_level": 10,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Level 15

    {
        "name": "Cheer On",
        "cost": 30,
        "cost_pool": "moxie",
        "description": (
            "Boost a tamed companion's next attack or skill roll if it can clearly hear you."
        ),
        "duration": "1 Turn",
        "effects": apply_state(
            "cheer_on_active",
            value_fn=lambda source: {
                "active": True,
                "requires_tamed_companion_target": True,
                "target_must_clearly_hear_you": True,
                "boost_next_attack_or_skill_roll_by": ability_level(source, "Cheer On"),
                "requires_clear_spoken_instruction": True,
                "source_ability": "Cheer On",
            },
        ),
        "required_level": 15,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Fey Truce",
        "description": (
            "Convince fey that you are not worth attacking immediately."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_truce_modifier_factory("fey", "Fey Truce")),
        "required_level": 15,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Spook Monster",
        "cost": 30,
        "cost_pool": "moxie",
        "description": (
            "Scare an unintelligent monster into fleeing."
        ),
        "duration": "1 Turn per Tamer Level",
        "effects": apply_state(
            "spook_monster_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": progression_level(source, "adventure", "Tamer"),
                "only_works_if_target_intelligence_below": 20,
                "contest": {
                    "caster_stat": "charisma",
                    "caster_skill": "Spook Monster",
                    "target_stats": ("intelligence", "willpower"),
                },
                "on_success_target_flees": True,
                "source_ability": "Spook Monster",
            },
        ),
        "required_level": 15,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Call Beast",
        "cost": 40,
        "cost_pool": "fortune",
        "description": (
            "Summon one of your tamed companions to your location."
        ),
        "duration": "1 Action",
        "effects": apply_state(
            "call_beast_active",
            value_fn=lambda source: {
                "active": True,
                "requires_tamed_companion_choice": True,
                "summons_companion_regardless_of_distance": True,
                "appears_instantly": True,
                "gm_may_call_for_luck_check_for_readiness": True,
                "source_ability": "Call Beast",
            },
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Slime Truce",
        "description": (
            "Convince slimes that you are not food."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_truce_modifier_factory("slime", "Slime Truce")),
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Level 25

    {
        "name": "Borrow Monster Skill",
        "cost": 50,
        "cost_pool": "fortune",
        "description": (
            "Duplicate a known monster skill of level 25 or lower."
        ),
        "duration": "1 Minute per Tamer Level",
        "effects": apply_state(
            "borrow_monster_skill_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Tamer"),
                "requires_previously_encountered_monster_skill": True,
                "max_borrowable_skill_level": 25,
                "uses_borrow_monster_skill_level_for_leveled_skills": ability_level(source, "Borrow Monster Skill"),
                "uses_tamer_level_in_place_of_monster_job_level": progression_level(source, "adventure", "Tamer"),
                "source_ability": "Borrow Monster Skill",
            },
        ),
        "required_level": 25,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Lesser Dragon Truce",
        "description": (
            "Confuse lesser dragons long enough to reduce their aggression toward you."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_truce_modifier_factory("lesser_dragon", "Lesser Dragon Truce")),
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

], source_type="adventure")