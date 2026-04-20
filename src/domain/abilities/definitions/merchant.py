from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    inspect,
    passive_modifier,
)


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _merchant_level(character) -> int:
    return character.get_progression_level("adventure", "Merchant", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


# Passive helpers

def _quality_work_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["quality_work"] = {
        "active": True,
        "bonus": _merchant_level(ctx.source),
        "applies_to": (
            "crafting_mundane_items",
            "crafting_job_services",
        ),
        "excludes": (
            "enchanting",
            "alchemy",
            "adventuring_job_creation",
        ),
        "source_ability": "Quality Work",
    }


build_job("Merchant", [

    # Level 1

    {
        "name": "Goldfinder",
        "cost": 5,
        "cost_pool": "fortune",
        "description": (
            "Search a slain foe for coin. Results scale by a Perception plus Goldfinder roll, "
            "with critical successes doubling the normal amount found."
        ),
        "duration": "1 Search",
        "effects": apply_state(
            "goldfinder_active",
            value_fn=lambda source: {
                "active": True,
                "requires_slain_foe_search": True,
                "search_roll": {
                    "stat": "perception",
                    "skill": "Goldfinder",
                },
                "result_table": {
                    "80": "1_copper",
                    "120": "1d10_copper",
                    "180": "1d10_silver",
                    "250": "1d10_gold",
                    "400": "1d100_gold",
                },
                "critical_success_doubles_result": True,
                "works_on_any_foe": True,
                "source_ability": "Goldfinder",
            },
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Haggle",
        "cost": 5,
        "cost_pool": "fortune",
        "description": (
            "Add this skill's level to negotiation rolls."
        ),
        "duration": "5 Minutes",
        "effects": apply_state(
            "haggle_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": 5,
                "negotiation_roll_bonus": _ability_level(source, "Haggle"),
                "source_ability": "Haggle",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Merchant's Eye",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Reveal the properties of an item or commodity. Concealed properties may require a roll."
        ),
        "duration": "1 Turn",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "merchants_eye",
                "reveals": "all_item_or_commodity_properties",
                "invalid_targets": (
                    "living_things",
                    "animated_constructs",
                    "undead",
                ),
                "hidden_property_check": {
                    "stat": "perception",
                    "skill": "Merchant's Eye",
                    "gm_secret_roll": True,
                },
                "source_ability": "Merchant's Eye",
            },
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Pack of Holding",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "Turn a carrying container into a portal to an extradimensional room. "
            "Only one pack may be active at a time."
        ),
        "duration": "1 Hour per Merchant Level",
        "effects": apply_state(
            "pack_of_holding_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": _merchant_level(source),
                "requires_container_target": True,
                "creates_extradimensional_room": True,
                "capacity_cubic_meters": _ability_level(source, "Pack of Holding"),
                "single_active_pack_only": True,
                "destroyed_container_ejects_contents": True,
                "source_ability": "Pack of Holding",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Quality Work",
        "description": (
            "Gain a bonus equal to Merchant level to mundane crafting and crafting-job service rolls."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_quality_work_modifier),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Level 5

    {"grant": "Friendly Smile", "required_level": 5},

    {"grant": "Knack for Languages", "required_level": 5},

    {
        "name": "Yah Mule",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "Increase the movement rate of pack animals you are actively driving or riding."
        ),
        "duration": "1 Hour per Merchant Level",
        "effects": apply_state(
            "yah_mule_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": _merchant_level(source),
                "applies_to_pack_animals_being_driven_or_ridden": True,
                "movement_rate_bonus": _ability_level(source, "Yah Mule"),
                "source_ability": "Yah Mule",
            },
        ),
        "required_level": 5,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    # Level 10

    {"grant": "Pillage", "required_level": 10},

    {
        "name": "Priceless Heirloom",
        "cost": 20,
        "cost_pool": "moxie",
        "description": (
            "Alter an item's appearance and apparent properties to make it seem more or less valuable."
        ),
        "duration": "1 Hour",
        "effects": apply_state(
            "priceless_heirloom_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": 1,
                "requires_item_target": True,
                "adjusts_apparent_value": True,
                "can_fake_or_mask_properties": True,
                "pierce_check": {
                    "observer_attribute_plus_skill": True,
                    "difficulty_stat": "charisma",
                    "difficulty_skill": "Priceless Heirloom",
                },
                "can_fool_item_reading_skills": True,
                "source_ability": "Priceless Heirloom",
            },
        ),
        "required_level": 10,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Not in the Face!",
        "cost": 30,
        "cost_pool": "moxie",
        "description": (
            "Discourage foes from attacking you, as long as you are not committing hostile or hindering acts."
        ),
        "duration": "1 Turn per Level",
        "effects": apply_state(
            "not_in_the_face_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": _ability_level(source, "Not in the Face!"),
                "requires_non_hostile_behavior": True,
                "requires_non_hindering_behavior": True,
                "attackers_must_roll": {
                    "attacker_stat": "willpower",
                    "defender_stat": "charisma",
                },
                "success_allows_normal_attacks_for_rest_of_fight": True,
                "failure_wastes_action": True,
                "source_ability": "Not in the Face!",
            },
        ),
        "required_level": 15,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Repair Item",
        "cost": 25,
        "cost_pool": "sanity",
        "description": (
            "Completely repair a mundane item, or attempt to repair a magical item."
        ),
        "duration": "1 Action",
        "effects": apply_state(
            "repair_item_active",
            value_fn=lambda source: {
                "active": True,
                "repairs_mundane_item_fully": True,
                "magical_item_repair_check": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Repair Item",
                    "difficulty": "creator_level * 10",
                },
                "failure_has_no_effect": True,
                "roll_1_to_9_destroys_item_permanently": True,
                "does_not_affect": (
                    "artifacts",
                    "specially_protected_items",
                    "constructs",
                ),
                "source_ability": "Repair Item",
            },
        ),
        "required_level": 15,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Apply/Remove Theftproof",
        "cost": 80,
        "cost_pool": "fortune",
        "description": (
            "Create or remove a theftproof guardian on an item."
        ),
        "duration": "Permanent until Spent",
        "effects": apply_state(
            "theftproof_active",
            value_fn=lambda source: {
                "active": True,
                "requires_item_target": True,
                "mode": "apply_or_remove",
                "creates_invisible_intangible_guardian": True,
                "guardian_dissolves_if_item_is_purchased_from_merchant": True,
                "stolen_item_guardian_whispers_stolen_to_handlers": True,
                "cannot_be_normally_dispelled": True,
                "removing_unowned_theftproof_is_socially_immoral": True,
                "source_ability": "Apply/Remove Theftproof",
            },
        ),
        "required_level": 20,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Lockbox of Loot",
        "cost": 50,
        "cost_pool": "fortune",
        "description": (
            "Enchant a lockbox into a stationary secure extradimensional vault only you can access."
        ),
        "duration": "1 Day per Merchant Level",
        "effects": apply_state(
            "lockbox_of_loot_active",
            value_fn=lambda source: {
                "active": True,
                "duration_days": _merchant_level(source),
                "requires_lockbox_target": True,
                "creates_stationary_pack_of_holding": True,
                "follows_pack_of_holding_rules": True,
                "only_merchant_can_open": True,
                "only_merchant_can_store_or_withdraw": True,
                "can_hold_corpses_but_not_living_creatures": True,
                "single_active_lockbox_only": True,
                "cannot_be_destroyed": True,
                "source_ability": "Lockbox of Loot",
            },
        ),
        "required_level": 20,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Claim Store",
        "cost": 100,
        "cost_pool": "fortune",
        "description": (
            "Claim a legally owned building as your store and gain strong benefits while within it."
        ),
        "duration": "1 Month per Merchant Level",
        "effects": apply_state(
            "claim_store_active",
            value_fn=lambda source: {
                "active": True,
                "duration_months": _merchant_level(source),
                "requires_legally_owned_building": True,
                "store_roll_bonus": _merchant_level(source),
                "self_cleaning": True,
                "comfortable_temperature_for_merchant": True,
                "stored_items_self_maintain": True,
                "everlit_lanterns": True,
                "counts_as_luxury_inn_for_rest": True,
                "source_ability": "Claim Store",
            },
        ),
        "required_level": 25,
        "scales_with_level": False,
        "target": "area",
        "type": "skill",
    },

    {
        "name": "Upgrade Item",
        "cost": 100,
        "cost_pool": "fortune",
        "description": (
            "Temporarily improve an item, boosting all rolls made while using it by Merchant level."
        ),
        "duration": "1 Turn per Skill Level",
        "effects": apply_state(
            "upgrade_item_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": _ability_level(source, "Upgrade Item"),
                "requires_item_target": True,
                "roll_bonus_while_using_item": _merchant_level(source),
                "artifact_behavior_may_be_unpredictable": True,
                "source_ability": "Upgrade Item",
            },
        ),
        "required_level": 25,
        "scales_with_level": True,
        "target": "item",
        "type": "skill",
    },

], source_type="adventure")