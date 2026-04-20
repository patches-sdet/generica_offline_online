from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    create_item,
    inspect,
    passive_modifier,
)


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _enchanter_level(character) -> int:
    return character.get_progression_level("adventure", "Enchanter", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


def _quality_roll_metadata(source, skill_name: str) -> dict:
    return {
        "quality_roll": {
            "stat": "intelligence",
            "skill": skill_name,
            "special_outcomes": {
                "1_to_10": "inferior_or_cursed",
                "90_to_100": "superior",
            },
        }
    }


def _spellstore_payload(source, max_level: int, reagent_color: str, reagent_doses: int) -> dict:
    payload = {
        "active": True,
        "store_spell_or_skill": True,
        "max_storable_level": max_level,
        "consumes_on_use": True,
        "requires_item_target": True,
        "can_store_ally_ability": True,
        "reagents_required": {
            reagent_color: reagent_doses,
        },
        "source_ability": f"Spellstore {max_level if max_level != 1 else 'I'}",
    }
    payload.update(_quality_roll_metadata(source, f"Spellstore {max_level if max_level != 1 else 'I'}"))
    return payload


def _make_glowgleam_item(source):
    return {
        "name": "Glowgleam Enchantment",
        "description": "A simple light enchantment bound into an object.",
        "created_by": "Glowgleam",
        "duration_hours": _enchanter_level(source),
        "light_strength_stat": "intelligence",
        "extinguish_difficulty": {
            "stat": "willpower",
            "skill": "Glowgleam",
        },
        "temporary": True,
    }


def _enchantment_experimentation_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["enchantment_experimentation"] = {
        "active": True,
        "experimental_skill_capacity": _enchanter_level(ctx.source) // 10,
        "unequipped_experimental_skills_stored_in_spellbooks": True,
        "source_ability": "Enchantment Experimentation",
    }


build_job("Enchanter", [

    # Level 1

    {
        "name": "Appraise",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Determine the properties of an examined item. Cursed or illusionary properties may require "
            "a hidden check. This skill levels when used on a new item for the first time."
        ),
        "duration": "5 Minutes",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "appraise_item",
                "reveals": "all_item_properties",
                "hidden_check_for_cursed_or_illusionary_properties": {
                    "stat": "intelligence",
                    "skill": "Appraise",
                    "gm_secret_roll": True,
                },
                "levels_on_new_item_examined": True,
                "source_ability": "Appraise",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Glowgleam",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Infuses an object with light. Luminescence scales with Intelligence, and magical extinguishing "
            "must overcome your Willpower plus Glowgleam level."
        ),
        "duration": "1 Hour per Enchanter Level",
        "effects": create_item(_make_glowgleam_item),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Harden",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Buff an object's armor value or a weapon's weapon level by this skill divided by five."
        ),
        "duration": "10 Minutes",
        "effects": apply_state(
            "harden_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": 10,
                "requires_object_or_construct_target": True,
                "bonus_amount": _ability_level(source, "Harden") // 5,
                "applies_to": ("armor", "weapon_level"),
                "source_ability": "Harden",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Soften",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Debuff an object's armor value or a weapon's weapon level by this skill divided by five. "
            "This skill levels whenever it is cast."
        ),
        "duration": "10 Minutes",
        "effects": apply_state(
            "soften_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": 10,
                "requires_object_or_construct_target": True,
                "penalty_amount": _ability_level(source, "Soften") // 5,
                "applies_to": ("armor", "weapon_level"),
                "levels_on_cast": True,
                "source_ability": "Soften",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Spellstore I",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Prepare an object that stores a level 1 spell or skill. Anyone may use the object "
            "appropriately to activate the stored effect, after which the item becomes nonmagical."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "spellstore_i_active",
            value_fn=lambda source: _spellstore_payload(source, 1, "red", 1),
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Boost +5",
        "cost": 25,
        "cost_pool": "sanity",
        "description": (
            "Enchant a magic item to boost an attribute, defense, or magical effect by +5. "
            "Not cumulative."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "boost_plus_5_active",
            value_fn=lambda source: {
                "active": True,
                "requires_magic_item_target": True,
                "boost_amount": 5,
                "valid_targets": ("attribute", "defense", "magical_effect"),
                "not_cumulative": True,
                "reagents_required": {
                    "red": 3,
                },
                "crystals_required": {
                    "level_1": 1,
                },
                "levels_when_successful_non_cursed_item_created": True,
                "source_ability": "Boost +5",
                **_quality_roll_metadata(source, "Boost +5"),
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Elemental Protection",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "Imbue a worn or wielded item with protection against a chosen elemental type."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "elemental_protection_active",
            value_fn=lambda source: {
                "active": True,
                "requires_item_target": True,
                "requires_dedicated_boost": True,
                "choose_element_type": True,
                "effect": "elemental_dispersion_or_absorption_field",
                "reagents_required": {
                    "orange": 1,
                },
                "source_ability": "Elemental Protection",
                **_quality_roll_metadata(source, "Elemental Protection"),
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Spellstore V",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "As Spellstore I, but stores level 5 skills or spells."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "spellstore_v_active",
            value_fn=lambda source: _spellstore_payload(source, 5, "red", 3),
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Wards",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "Create wards in an area against a chosen creature type, penalizing them and damaging them each turn."
        ),
        "duration": "Permanent until Destroyed or Dispelled",
        "effects": apply_state(
            "wards_active",
            value_fn=lambda source: {
                "active": True,
                "choose_creature_type": True,
                "area_effect": True,
                "affected_creature_roll_penalty": _enchanter_level(source),
                "damage_over_time_per_turn": _ability_level(source, "Wards"),
                "spell_penalty_for_affected_creatures": _enchanter_level(source),
                "affected_spell_damage_halved": True,
                "can_be_dispelled": True,
                "reagents_required": {
                    "green": 1,
                },
                "source_ability": "Wards",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "area",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Boost +10",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "As Boost +5, but grants +10 instead."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "boost_plus_10_active",
            value_fn=lambda source: {
                "active": True,
                "requires_magic_item_target": True,
                "boost_amount": 10,
                "valid_targets": ("attribute", "defense", "magical_effect"),
                "not_cumulative": True,
                "reagents_required": {
                    "yellow": 3,
                },
                "crystals_required": {
                    "level_2": 1,
                },
                "levels_when_successful_non_cursed_item_created": True,
                "source_ability": "Boost +10",
                **_quality_roll_metadata(source, "Boost +10"),
            },
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Disenchant",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "Attempt to disenchant a magical item you created or control, recovering half the reagents and crystals used."
        ),
        "duration": "1 Action",
        "effects": apply_state(
            "disenchant_active",
            value_fn=lambda source: {
                "active": True,
                "requires_owned_controlled_or_created_item": True,
                "contest": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Disenchant",
                    "defender_stat": "intelligence",
                    "defender_skill": "appropriate_enchanter_skill_or_equivalent",
                    "holder_may_add_willpower": True,
                },
                "on_success": {
                    "recover_half_creation_materials": True,
                },
                "source_ability": "Disenchant",
            },
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Spellstore X",
        "cost": 40,
        "cost_pool": "sanity",
        "description": (
            "As Spellstore I, but stores level 10 skills or spells."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "spellstore_x_active",
            value_fn=lambda source: _spellstore_payload(source, 10, "orange", 1),
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Spell Protection",
        "cost": 150,
        "cost_pool": "sanity",
        "description": (
            "Protect a magical item against hostile magic, time, and most physical damage."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "spell_protection_active",
            value_fn=lambda source: {
                "active": True,
                "requires_magic_item_target": True,
                "immune_to_time": True,
                "resists_hostile_magic": True,
                "resists_most_physical_damage": True,
                "cannot_be_disenchanted_or_destroyed_without_long_breakdown": True,
                "required_breakdown_days_per_creator_level": _enchanter_level(source),
                "reagents_required": {
                    "green": 3,
                },
                "crystals_required": {
                    "level_2": 1,
                },
                "source_ability": "Spell Protection",
            },
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Spellstore XV",
        "cost": 60,
        "cost_pool": "sanity",
        "description": (
            "As Spellstore I, but stores level 15 skills or spells."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "spellstore_xv_active",
            value_fn=lambda source: _spellstore_payload(source, 15, "orange", 3),
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Boost +20",
        "cost": 100,
        "cost_pool": "sanity",
        "description": (
            "As Boost +5, but grants +20 instead."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "boost_plus_20_active",
            value_fn=lambda source: {
                "active": True,
                "requires_magic_item_target": True,
                "boost_amount": 20,
                "valid_targets": ("attribute", "defense", "magical_effect"),
                "not_cumulative": True,
                "reagents_required": {
                    "blue": 3,
                },
                "crystals_required": {
                    "level_3": 1,
                },
                "levels_when_successful_non_cursed_item_created": True,
                "source_ability": "Boost +20",
                **_quality_roll_metadata(source, "Boost +20"),
            },
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Enhance Skill",
        "cost": 100,
        "cost_pool": "sanity",
        "description": (
            "When tied to a boost, allows that boost to increase a chosen skill by an amount equal to the boost."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "enhance_skill_active",
            value_fn=lambda source: {
                "active": True,
                "requires_linked_boost": True,
                "converts_boost_into_skill_levels": True,
                "reagents_required": {
                    "green": 1,
                },
                "source_ability": "Enhance Skill",
            },
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Spellstore XX",
        "cost": 80,
        "cost_pool": "sanity",
        "description": (
            "As Spellstore I, but stores level 20 skills or spells."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "spellstore_xx_active",
            value_fn=lambda source: _spellstore_payload(source, 20, "yellow", 1),
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Charged Spell",
        "cost": 200,
        "cost_pool": "sanity",
        "description": (
            "Charge an item with multiple castings of the same spell. It cannot be recharged once made."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "charged_spell_active",
            value_fn=lambda source: {
                "active": True,
                "requires_item_target": True,
                "stores_multiple_castings_of_same_spell": True,
                "charge_count_based_on_original_caster_capacity": True,
                "cannot_be_recharged": True,
                "max_storable_spell_level": 10,
                "reagent_cost_by_spell_level": {
                    "1": {"red": 1},
                    "5": {"orange": 1},
                    "10": {"yellow": 1},
                },
                "source_ability": "Charged Spell",
            },
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Embed Spell I",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "Enchant a spellstored item so it may be used once per day instead of becoming nonmagical after use."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "embed_spell_i_active",
            value_fn=lambda source: {
                "active": True,
                "requires_spellstored_item": True,
                "reusable_once_per_day": True,
                "recharge_hours": 24,
                "crystals_required": {
                    "level_4": 1,
                },
                "source_ability": "Embed Spell I",
            },
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Enchantment Experimentation",
        "description": (
            "Research and produce new Enchanter skills. You may learn and use experimental enchanting skills "
            "equal to your level divided by ten."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_enchantment_experimentation_modifier),
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Spellstore XXV",
        "cost": 100,
        "cost_pool": "sanity",
        "description": (
            "As Spellstore I, but stores level 25 skills or spells."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "spellstore_xxv_active",
            value_fn=lambda source: _spellstore_payload(source, 25, "yellow", 3),
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

], source_type="adventure")