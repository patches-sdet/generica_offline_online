from domain.abilities.builders._job_builder import build_job
from domain.abilities import ability_level, ctx_ability_level, progression_level, ctx_progression_level
from domain.abilities.patterns import (
    apply_state,
    inspect,
    passive_modifier,
    scaled_derived_buff,
)
from domain.effects.special.minions import GrantControlledGroupMembershipEffect


# Local helpers

def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


# Passive helpers

def _magical_experimentation_modifier(source) -> None:
    states = _ensure_states(source)
    states["magical_experimentation"] = {
        "active": True,
        "experimental_skill_capacity": progression_level(source, "adventure", "Wizard") // 10,
        "unequipped_experimental_skills_stored_in_spellbooks": True,
        "source_ability": "Magical Experimentation",
    }


def _mana_meditation_modifier(source) -> None:
    states = _ensure_states(source)
    states["mana_meditation"] = {
        "active": True,
        "extra_sanity_regen_per_ten_minutes": (progression_level(source, "adventure", "Wizard"), + 9) // 10,
        "source_ability": "Mana Meditation",
    }


build_job("Wizard", [

    # Level 1

    {
        "name": "Analyze Magic",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Examine the properties of a magical item or spell, or reveal all magical effects active on an individual."
        ),
        "duration": "1 Minute",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "analyze_magic",
                "reveals": (
                    "magical_item_properties",
                    "spell_properties",
                    "active_magical_effects_on_target",
                ),
                "check": {
                    "stat": "intelligence",
                    "skill": "Analyze Magic",
                    "difficulty": "creator_or_spellcaster_level_times_10",
                },
                "source_ability": "Analyze Magic",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "item or ally or enemy",
        "type": "skill",
    },

    {
        "name": "Empower Spell",
        "cost": 0,
        "cost_pool": None,
        "description": (
            "Add raw magical power to another spell by paying double that spell's pool cost."
        ),
        "duration": "1 Action",
        "effects": apply_state(
            "empower_spell_active",
            value_fn=lambda source: {
                "active": True,
                "applies_to_spell_cast_same_action": True,
                "extra_cost_multiplier": 2,
                "boost_amount": ability_level(source, "Empower Spell"),
                "does_nothing_for_nonleveled_spells": True,
                "source_ability": "Empower Spell",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Force Blast",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Blast one target with raw magical energy, dealing HP damage and bypassing non-magical armor."
        ),
        "duration": "1 Attack",
        "effects": apply_state(
            "force_blast_active",
            value_fn=lambda source: {
                "active": True,
                "attack_stat": "intelligence",
                "attack_skill": "Force Blast",
                "target_stat": "agility",
                "damage_pool": "hp",
                "damage_amount": "margin_of_success",
                "bypasses_nonmagical_armor": True,
                "source_ability": "Force Blast",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Force Shield",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Form a shield of force that increases Armor, counting double against HP-targeting spells."
        ),
        "duration": "1 Minute per Wizard Level",
        "effects": apply_state(
            "force_shield_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Wizard"),
                "armor_bonus": ability_level(source, "Force Shield"),
                "double_value_against_hp_targeting_spells": True,
                "source_ability": "Force Shield",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {"grant": "Mana Focus", "required_level": 1},

    # Level 5

    {
        "name": "Familiar",
        "cost": 25,
        "cost_pool": "sanity",
        "description": (
            "Imbue a common beast or bug with increased sentience and bind it as your familiar."
        ),
        "duration": "Permanent",
        "effects": GrantControlledGroupMembershipEffect(
            tag="wizard_familiar",
            condition=lambda ctx, target: True,
            controller_state_key="controller",
            extra_state={
                "requires_common_beast_or_bug": True,
                "single_familiar_only": True,
                "familiar_intelligence": "familiar_skill_level",
                "can_send_telepathic_messages": True,
                "can_loan_sanity_one_for_one": True,
                "is_independent_and_may_refuse_danger": True,
                "obedience_depends_on_treatment": True,
                "source_ability": "Familiar",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Magic Fingers",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Use telekinetic force to lift and move objects around."
        ),
        "duration": "1 Turn",
        "effects": apply_state(
            "magic_fingers_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": 1,
                "telekinetic_strength": ability_level(source, "Magic Fingers"),
                "can_lift_and_move_objects": True,
                "cannot_directly_attack_or_deal_real_damage": True,
                "can_shove_with_check": {
                    "caster_strength_proxy": "Magic Fingers",
                    "target_stat": "strength",
                },
                "may_throw_target_off_ledge_or_into_obstacle": True,
                "source_ability": "Magic Fingers",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "enemy or item",
        "type": "skill",
    },

    {
        "name": "Resilient Mind",
        "description": (
            "Gain a bonus to Mental Fortitude equal to Wizard level."
        ),
        "duration": "Passive Constant",
        "effects": scaled_derived_buff(
            scale_fn=lambda source: progression_level(source, "adventure", "Wizard"),
            stat="mental_fortitude",
        ),
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Level 10

    {"grant": "Dispel Magic", "required_level": 10},

    {
        "name": "Float",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "Float about a foot off the ground to bypass ground hazards."
        ),
        "duration": "1 Turn per Wizard Level",
        "effects": apply_state(
            "float_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": progression_level(source, "adventure", "Wizard"),
                "hover_height_feet": 1,
                "bypass_ground_traps": True,
                "move_over_lava_and_water": True,
                "source_ability": "Float",
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
        "name": "Conceal Magic",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "Conceal the magic and properties of an item, spell, or creature from magical scrutiny."
        ),
        "duration": "4 Hours per Wizard Level",
        "effects": apply_state(
            "conceal_magic_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": progression_level(source, "adventure", "Wizard") * 4,
                "valid_targets": ("magical_item", "spell", "creature"),
                "increase_analysis_difficulty_by": ability_level(source, "Conceal Magic"),
                "applies_to": ("Analyze Magic", "similar_skills"),
                "source_ability": "Conceal Magic",
            },
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": True,
        "target": "item or ally or self",
        "type": "skill",
    },

    {
        "name": "Counterspelling",
        "cost": 15,
        "cost_pool": "sanity",
        "description": (
            "Hinder enemy spellcasting through constant disruptive muttering."
        ),
        "duration": "Until Canceled",
        "effects": apply_state(
            "counterspelling_active",
            value_fn=lambda source: {
                "active": True,
                "cost_per_minute": 15,
                "cost_pool": "sanity",
                "spellcasting_penalty_to_nearby_foes": ability_level(source, "Counterspelling"),
                "requires_continuous_chanting": True,
                "source_ability": "Counterspelling",
            },
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": True,
        "target": "area",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Flying",
        "cost": 40,
        "cost_pool": "sanity",
        "description": (
            "Fly using magical force. Flying substitutes for Agility rolls and targets while active."
        ),
        "duration": "1 Minute per Wizard Level",
        "effects": apply_state(
            "flying_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Wizard"),
                "can_fly": True,
                "flight_skill_substitutes_for_agility_rolls": True,
                "flight_skill_substitutes_for_agility_target_numbers": True,
                "agility_buffs_apply_to_flight_skill": True,
                "source_ability": "Flight",
            },
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Force Blast Burst",
        "cost": 40,
        "cost_pool": "sanity",
        "description": (
            "Hurl a burst of raw magical force, damaging all targets in a chosen radius."
        ),
        "duration": "1 Attack",
        "effects": apply_state(
            "force_blast_burst_active",
            value_fn=lambda source: {
                "active": True,
                "attack_stat": "intelligence",
                "attack_skill": "Force Blast",
                "target_stat": "agility",
                "damage_pool": "hp",
                "damage_amount": "margin_of_success",
                "radius_feet": progression_level(source, "adventure", "Wizard"),
                "minimum_radius_feet": 1,
                "single_roll_applied_to_each_target": True,
                "bypasses_nonmagical_armor": True,
                "source_ability": "Force Blast Burst",
            },
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Magical Experimentation",
        "description": (
            "Research and produce new Wizard skills."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_magical_experimentation_modifier),
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Mana Meditation",
        "description": (
            "Regenerate extra Sanity every ten minutes."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_mana_meditation_modifier),
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

], source_type="adventure")