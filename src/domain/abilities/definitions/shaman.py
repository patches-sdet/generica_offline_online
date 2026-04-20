from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    heal_hp,
    passive_modifier,
    scaled_derived_buff,
)


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _shaman_level(character) -> int:
    return character.get_progression_level("adventure", "Shaman", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


# Passive helpers

def _secret_herbs_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["secret_herbs_and_spices"] = {
        "active": True,
        "duration_minutes": _shaman_level(ctx.source),
        "plant_roll_bonus": _ability_level(ctx.source, "Secret Herbs and Spices"),
        "identifies_unknown_plants_and_uses": True,
        "counts_as_skill": "Herbalism",
        "applies_to": (
            "finding_herbs",
            "finding_natural_components",
            "harvesting_plant_resources",
            "plant_identification",
        ),
        "source_ability": "Secret Herbs and Spices",
    }


build_job("Shaman", [

    # Level 1

    {
        "name": "Fated Preserver",
        "description": (
            "Gain a bonus to Fate equal to your Shaman level."
        ),
        "duration": "Passive Constant",
        "effects": scaled_derived_buff(
            scale_fn=_shaman_level,
            stat="fate",
        ),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {"grant": "Poison Resistance", "required_level": 1},

    {
        "name": "Secret Herbs and Spices",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Find herbs and natural components, identify unknown plants, and count as Herbalism "
            "for plant harvesting while active."
        ),
        "duration": "1 Minute per Shaman Level",
        "effects": passive_modifier(_secret_herbs_modifier),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Slow Regeneration",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Heal a target gradually over one minute. May be pre-cast on an uninjured target."
        ),
        "duration": "1 Minute per Shaman Level",
        "effects": apply_state(
            "slow_regeneration_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _shaman_level(source),
                "water_based_healing": True,
                "valid_targets_include_water_elementals": True,
                "total_healing": _ability_level(source, "Slow Regeneration"),
                "healing_per_turn": max(1, _ability_level(source, "Slow Regeneration") // 6),
                "may_be_cast_preemptively": True,
                "cannot_heal_past_max_hp": True,
                "source_ability": "Slow Regeneration",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "ally or self",
        "type": "skill",
    },

    {
        "name": "Speak with Nature",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Speak with beasts, plants, and other nature-aligned entities."
        ),
        "duration": "1 Conversation",
        "effects": apply_state(
            "speak_with_nature_active",
            value_fn=lambda source: {
                "active": True,
                "valid_targets": (
                    "beasts",
                    "plants",
                    "nature_entities",
                ),
                "enables_conversation": True,
                "source_ability": "Speak with Nature",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "ally or area",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Beastly Skill Borrow",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Name a beast and gain access to its level 1 skills."
        ),
        "duration": "1 Minute per Shaman Level",
        "effects": apply_state(
            "beastly_skill_borrow_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _shaman_level(source),
                "choose_beast_type": True,
                "gain_level_1_beast_skills": True,
                "borrowed_skill_rating": _ability_level(source, "Beastly Skill Borrow") // 2,
                "source_ability": "Beastly Skill Borrow",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Call Vines",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Cause magical mobile vines to spring from nearby vegetation."
        ),
        "duration": "1 Minute per Shaman Level",
        "effects": apply_state(
            "call_vines_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _shaman_level(source),
                "requires_nearby_plantlife": True,
                "creates_mobile_vines": True,
                "vine_strength": _ability_level(source, "Call Vines"),
                "vine_brawling": _ability_level(source, "Call Vines"),
                "vine_armor": _shaman_level(source),
                "vine_hp": _shaman_level(source) * 10,
                "source_ability": "Call Vines",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "area",
        "type": "skill",
    },

    {
        "name": "Dreamquest",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "Send a willing recipient into a deep slumber to contact deeper natural forces."
        ),
        "duration": "3-5 Hours",
        "effects": apply_state(
            "dreamquest_active",
            value_fn=lambda source: {
                "active": True,
                "requires_willing_recipient": True,
                "deep_slumber": True,
                "duration_hours": "3_to_5",
                "contacts_deeper_forces_of_nature": True,
                "visions_may_include": (
                    "past",
                    "present",
                    "future",
                ),
                "decipher_check": {
                    "stat": "wisdom",
                    "skill": "Dreamquest",
                    "difficulty": "gm_defined_minimum_150",
                },
                "metadata_placeholder_only": True,
                "source_ability": "Dreamquest",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "ally or self",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Call Thorns",
        "cost": 15,
        "cost_pool": "sanity",
        "description": (
            "Cause nearby plantlife to grow damaging thorns."
        ),
        "duration": "1 Minute per Shaman Level",
        "effects": apply_state(
            "call_thorns_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _shaman_level(source),
                "requires_nearby_plantlife": True,
                "thorn_damage_hp": _ability_level(source, "Call Thorns"),
                "damages_targets_moving_through_or_pushed_into_vegetation": True,
                "synergy_with_call_vines": {
                    "increases_vine_damage": True,
                    "critical_hits_may_grapple": True,
                    "critical_hits_inflict": "Hobbled",
                    "hobbled_ends_when_out_of_reach_of_vegetation": True,
                },
                "source_ability": "Call Thorns",
            },
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": True,
        "target": "area",
        "type": "skill",
    },

    {
        "name": "Fast Regeneration",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "Heal a target every turn for one minute."
        ),
        "duration": "1 Minute per Shaman Level",
        "effects": apply_state(
            "fast_regeneration_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _shaman_level(source),
                "water_based_healing": True,
                "valid_targets_include_water_elementals": True,
                "healing_per_turn": _ability_level(source, "Fast Regeneration"),
                "may_be_cast_preemptively": True,
                "cannot_heal_past_max_hp": True,
                "source_ability": "Fast Regeneration",
            },
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": True,
        "target": "ally or self",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Beast Shape I",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "Transform into any Tier 1 animal."
        ),
        "duration": "1 Minute per Shaman Level",
        "effects": apply_state(
            "beast_shape_i_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _shaman_level(source),
                "choose_tier_1_animal": True,
                "gain_animal_job_levels": 1,
                "gain_temporary_attribute_adjustments": True,
                "gain_full_access_to_animal_skills": True,
                "leveled_animal_skills_use": _ability_level(source, "Beast Shape I"),
                "source_ability": "Beast Shape I",
            },
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Sweat Lodge",
        "cost": 60,
        "cost_pool": "sanity",
        "description": (
            "Prepare a sweat lodge that can remove most conditions from participants."
        ),
        "duration": "2 Hours",
        "effects": apply_state(
            "sweat_lodge_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": 2,
                "requires_15_minute_preparation": True,
                "requires_suitable_bathing_area": True,
                "participants_must_spend_at_least_hours": 1,
                "removes_all_conditions_except_special_cases": True,
                "does_not_remove_curses_or_gm_protected_cases": True,
                "source_ability": "Sweat Lodge",
            },
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": False,
        "target": "area",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Call Winds",
        "cost": 40,
        "cost_pool": "sanity",
        "description": (
            "Exercise limited influence over weather and wind."
        ),
        "duration": "1 Hour",
        "effects": apply_state(
            "call_winds_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": 1,
                "weather_control": True,
                "check": {
                    "stat": "wisdom",
                    "skill": "Call Winds",
                    "difficulty_table": {
                        "minor_change": 100,
                        "moderate_change": 150,
                        "major_change": 200,
                        "hurricane_from_zero": 300,
                        "tornadoes": 400,
                    },
                },
                "source_ability": "Call Winds",
            },
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "area",
        "type": "skill",
    },

    {
        "name": "Group Dreamquest",
        "cost": 40,
        "cost_pool": "sanity",
        "description": (
            "As Dreamquest, but for a group of willing individuals sharing the same dreamquest."
        ),
        "duration": "2-5 Hours",
        "effects": apply_state(
            "group_dreamquest_active",
            value_fn=lambda source: {
                "active": True,
                "cost_per_target": 40,
                "requires_willing_targets": True,
                "shared_dreamquest": True,
                "duration_hours": "2_to_5",
                "often_easier_to_decipher_than_single_dreamquest": True,
                "common_themes_improve_clarity": True,
                "metadata_placeholder_only": True,
                "source_ability": "Group Dreamquest",
            },
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "party",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Beast Shape V",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "Transform into an animal as with Beast Shape I, but gain five levels in the chosen animal job."
        ),
        "duration": "1 Minute per Shaman Level",
        "effects": apply_state(
            "beast_shape_v_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _shaman_level(source),
                "choose_animal": True,
                "gain_animal_job_levels": 5,
                "gain_temporary_attribute_adjustments": True,
                "gain_full_access_to_animal_skills": True,
                "leveled_animal_skills_use": _ability_level(source, "Beast Shape V"),
                "source_ability": "Beast Shape V",
            },
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Totem Mask",
        "cost": 100,
        "cost_pool": "sanity",
        "description": (
            "Create a totem mask that stores charge for a single simple cause."
        ),
        "duration": "Permanent until Discharged",
        "effects": apply_state(
            "totem_mask_active",
            value_fn=lambda source: {
                "active": True,
                "create_totem_mask": True,
                "simple_limited_cause_required": True,
                "mask_starts_with_charge": 1,
                "charge_per_grind_point": 10,
                "spend_charge_one_for_one_on_relevant_rolls": True,
                "only_applies_while_pursuing_mask_cause": True,
                "mask_crumbles_at_zero_grind_points": True,
                "can_be_recharged_with_additional_grind_points": True,
                "source_ability": "Totem Mask",
            },
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

], source_type="adventure")