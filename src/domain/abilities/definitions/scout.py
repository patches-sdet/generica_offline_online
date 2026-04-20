from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    inspect,
    passive_modifier,
)


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _scout_level(character) -> int:
    return character.get_progression_level("adventure", "Scout", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


# Passive helpers

def _sturdy_back_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["sturdy_back"] = {
        "active": True,
        "non_equipped_item_weight_reduction_percent": min(
            _ability_level(ctx.source, "Sturdy Back"),
            90,
        ),
        "does_not_apply_to_equipped_weapons_or_armor": True,
        "source_ability": "Sturdy Back",
    }


def _alertness_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["alertness"] = {
        "active": True,
        "auto_activate_sensory_skills_when_ambushed_or_unseen_danger": True,
        "activation_chance_percent": _ability_level(ctx.source, "Alertness"),
        "free_activation_no_pool_cost": True,
        "source_ability": "Alertness",
    }


def _wild_child_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["wild_child"] = {
        "active": True,
        "all_roll_bonus_in_wilderness": _scout_level(ctx.source),
        "equivalent_environments_also_count": True,
        "source_ability": "Wild Child",
    }


build_job("Scout", [

    # Level 1

    {
        "name": "Camouflage",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Blend in with your surroundings, buffing Stealth. In the wilderness, every two "
            "Camouflage levels count as three."
        ),
        "duration": "Until Dismissed or Exhausted",
        "effects": apply_state(
            "camouflage_active",
            value_fn=lambda source: {
                "active": True,
                "cost_per_minute": 5,
                "cost_pool": "sanity",
                "stealth_bonus": _ability_level(source, "Camouflage"),
                "wilderness_scaling": {
                    "base_levels": 2,
                    "effective_levels": 3,
                },
                "source_ability": "Camouflage",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Firestarter",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Create fire whose intensity scales with Firestarter level. Can also be used offensively "
            "to ignite items on a target's person."
        ),
        "duration": "1 Action",
        "effects": apply_state(
            "firestarter_active",
            value_fn=lambda source: {
                "active": True,
                "creates_fire": True,
                "ignites_flammable_material": True,
                "intensity_table": {
                    "1": "candle",
                    "10": "torch",
                    "25": "bonfire",
                    "50+": "hot_enough_to_melt_soft_metals",
                },
                "offensive_use": {
                    "attack_stats": ("dexterity", "brawling", "Firestarter"),
                    "target_stat": "agility",
                },
                "source_ability": "Firestarter",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "item or enemy",
        "type": "skill",
    },

    {
        "name": "Keen Eye",
        "cost": 5,
        "cost_pool": "stamina",
        "description": (
            "Buff your Perception by your Keen Eye skill level."
        ),
        "duration": "1 Minute per Scout Level",
        "effects": apply_state(
            "keen_eye_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _scout_level(source),
                "perception_bonus": _ability_level(source, "Keen Eye"),
                "source_ability": "Keen Eye",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Sturdy Back",
        "description": (
            "Reduce the weight of each non-equipped carried item by 1% per skill level, up to 90%."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_sturdy_back_modifier),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Wind's Whisper",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Silently send a message on the wind to a named target within range."
        ),
        "duration": "1 Message",
        "effects": apply_state(
            "winds_whisper_active",
            value_fn=lambda source: {
                "active": True,
                "silent_activation": True,
                "named_target_required": True,
                "range_meters": _ability_level(source, "Wind's Whisper") * 50,
                "word_limit": (
                    _ability_level(source, "Wind's Whisper") // 2
                    + _scout_level(source)
                ),
                "source_ability": "Wind's Whisper",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Alertness",
        "description": (
            "May auto-activate your sensory-enhancing skills for free when ambushed or about to "
            "encounter unseen danger."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_alertness_modifier),
        "required_level": 5,
        "scales_with_level": True,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Best Route",
        "cost": 15,
        "cost_pool": "sanity",
        "description": (
            "Examine a visible terrain feature and mark the best route to your destination for the party."
        ),
        "duration": "1 Hour per Scout Level",
        "effects": apply_state(
            "best_route_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": _scout_level(source),
                "requires_visible_terrain_feature": True,
                "route_visible_to_party": True,
                "route_quality_table": {
                    "1-25": "basic_route",
                    "26-50": "decent_route_with_shortcuts_and_obvious_danger_avoidance",
                    "51-75": "good_route_avoids_most_monsters_and_hits_unconcealed_loot",
                    "76+": "best_route_avoids_99_percent_of_monsters_and_hits_concealed_treasures",
                },
                "source_ability": "Best Route",
            },
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    {"grant": "Forage", "required_level": 5},

    # Level 10

    {
        "name": "Scouter",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "View part or all of a visible target's status screen."
        ),
        "duration": "10 Seconds per Scout Level",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "scouter",
                "duration_seconds": _scout_level(source) * 10,
                "contest": {
                    "caster_stat": "perception",
                    "caster_skill": "Scouter",
                    "target_stat": "luck",
                },
                "reveals": "partial_or_full_status_screen",
                "requires_visible_target": True,
                "source_ability": "Scouter",
            },
        ),
        "required_level": 10,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {"grant": "Wakeful Wandering", "required_level": 10},

    # Level 15

    {
        "name": "Be Prepared",
        "cost": 25,
        "cost_pool": "fortune",
        "description": (
            "Pull a useful non-magical item from a backpack or other container."
        ),
        "duration": "1 Hour",
        "effects": apply_state(
            "be_prepared_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": 1,
                "create_useful_nonmagical_item": True,
                "must_fit_in_backpack_or_container": True,
                "max_value_gold": 10,
                "item_disappears_or_falls_apart_when_duration_ends": True,
                "source_ability": "Be Prepared",
            },
        ),
        "required_level": 15,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Short Rations",
        "cost": 5,
        "cost_pool": "stamina",
        "description": (
            "Ignore hunger for a limited duration. When it ends, gain Starving until you eat a full meal."
        ),
        "duration": "Maximum of 1 Day per Scout Level",
        "effects": apply_state(
            "short_rations_active",
            value_fn=lambda source: {
                "active": True,
                "cost_per_hour": 5,
                "cost_pool": "stamina",
                "max_duration_days": _scout_level(source),
                "ignore_hunger": True,
                "on_end_gain_condition": "Starving",
                "condition_removed_by": "full_meal",
                "source_ability": "Short Rations",
            },
        ),
        "required_level": 15,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Party Whisper",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "Allow all members of the Scout's party to whisper to each other without speaking over long distances."
        ),
        "duration": "1 Minute per Scout Level",
        "effects": apply_state(
            "party_whisper_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _scout_level(source),
                "all_party_members_can_whisper_silently": True,
                "range_meters": _ability_level(source, "Wind's Whisper") * 50,
                "word_limit": (
                    _ability_level(source, "Wind's Whisper") // 2
                    + _scout_level(source)
                ),
                "uses_winds_whisper_range_and_word_rules": True,
                "source_ability": "Party Whisper",
            },
        ),
        "required_level": 20,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    {
        "name": "Thirstbane",
        "cost": 5,
        "cost_pool": "stamina",
        "description": (
            "Ignore thirst for a limited duration. When it ends, gain Dehydrated until you get a full drink."
        ),
        "duration": "Maximum of 6 Hours per Scout Level",
        "effects": apply_state(
            "thirstbane_active",
            value_fn=lambda source: {
                "active": True,
                "cost_per_hour": 5,
                "cost_pool": "stamina",
                "max_duration_hours": _scout_level(source) * 6,
                "ignore_thirst": True,
                "on_end_gain_condition": "Dehydrated",
                "condition_removed_by": "full_drink",
                "source_ability": "Thirstbane",
            },
        ),
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Mass Camouflage",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "As Camouflage, but may be extended to party members."
        ),
        "duration": "Until Dismissed or Exhausted",
        "effects": apply_state(
            "mass_camouflage_active",
            value_fn=lambda source: {
                "active": True,
                "cost_per_subject_per_minute": 10,
                "cost_pool": "sanity",
                "extends_camouflage_to_party_members": True,
                "stealth_bonus": _ability_level(source, "Camouflage"),
                "wilderness_scaling": {
                    "base_levels": 2,
                    "effective_levels": 3,
                },
                "source_ability": "Mass Camouflage",
            },
        ),
        "required_level": 25,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    {
        "name": "Wild Child",
        "description": (
            "Add your Scout level to all rolls while in a wilderness area or equivalent."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_wild_child_modifier),
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

], source_type="adventure")