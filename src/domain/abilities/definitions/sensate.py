from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    passive_modifier,
)


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _sensate_level(character) -> int:
    return character.get_progression_level("adventure", "Sensate", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


# Passive helpers

def _arts_and_crafts_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["arts_and_crafts"] = {
        "active": True,
        "bonus": _sensate_level(ctx.source),
        "applies_to": "level_1_crafting_skill_rolls",
        "source_ability": "Arts and Crafts",
    }


build_job("Sensate", [

    # Level 1

    {
        "name": "Arts and Crafts",
        "description": (
            "Add your Sensate level to all level 1 crafting skill rolls."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_arts_and_crafts_modifier),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Dull Sense",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Reduce a target's Perception by this skill's level. If resisted, the target notices the attempt."
        ),
        "duration": "1 Minute per Sensate Level",
        "effects": apply_state(
            "dull_sense_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _sensate_level(source),
                "contest": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Dull Sense",
                    "target_stat": "wisdom",
                },
                "on_success": {
                    "perception_penalty": _ability_level(source, "Dull Sense"),
                    "target_unaware_of_effect": True,
                    "target_unaware_of_caster": True,
                },
                "on_failure": {
                    "attempt_is_noticed": True,
                    "no_dullness_applied": True,
                },
                "source_ability": "Dull Sense",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Heighten Sense",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Increase a single target's Perception by this skill's level."
        ),
        "duration": "1 Minute per Sensate Level",
        "effects": apply_state(
            "heighten_sense_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _sensate_level(source),
                "perception_bonus": _ability_level(source, "Heighten Sense"),
                "source_ability": "Heighten Sense",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "ally or self",
        "type": "skill",
    },

    {
        "name": "Phantasmal Picture",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Create a minor unmoving visual illusion over a small area."
        ),
        "duration": "1 Minute per Sensate Level",
        "effects": apply_state(
            "phantasmal_picture_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _sensate_level(source),
                "illusion_type": "visual",
                "illusion_moves": False,
                "area_square_meters": 3,
                "pierce_check": {
                    "observer_stat": "perception",
                    "caster_stat": "charisma",
                    "caster_skill": "Phantasmal Picture",
                },
                "recognized_illusion_still_obscures_vision": True,
                "translucent_illusion_may_not_block_vision": True,
                "source_ability": "Phantasmal Picture",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "area",
        "type": "skill",
    },

    {
        "name": "That Je Ne Seis Quois",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "Add one additional non-visual sense to one of your illusions."
        ),
        "duration": "Until the Illusion Fades",
        "effects": apply_state(
            "that_je_ne_seis_quois_active",
            value_fn=lambda source: {
                "active": True,
                "applies_to_existing_illusion": True,
                "choose_one_nonvisual_sense": True,
                "valid_choices": (
                    "tactile",
                    "taste",
                    "auditory",
                    "olfactory",
                ),
                "may_be_applied_up_to_four_times": True,
                "source_ability": "That Je Ne Seis Quois",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "area",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Deafen",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Inflict the Deafened condition on a single target."
        ),
        "duration": "1 Minute per Sensate Level",
        "effects": apply_state(
            "deafen_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _sensate_level(source),
                "contest": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Deafen",
                    "target_stat": "constitution",
                },
                "on_success_condition": "Deafened",
                "source_ability": "Deafen",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {"grant": "Magic Mouth", "required_level": 5},

    {
        "name": "Sleep",
        "cost": 15,
        "cost_pool": "sanity",
        "description": (
            "Attack a target's Stamina, dealing margin damage reduced by Endurance."
        ),
        "duration": "1 Action",
        "effects": apply_state(
            "sleep_active",
            value_fn=lambda source: {
                "active": True,
                "attack_stat": "intelligence",
                "attack_skill": "Sleep",
                "target_stat": "agility",
                "damage_pool": "stamina",
                "damage_amount": "margin_of_success",
                "reduced_by": "endurance",
                "source_ability": "Sleep",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Bad Gas",
        "cost": 15,
        "cost_pool": "sanity",
        "description": (
            "Inflict the Gassy condition on a target."
        ),
        "duration": "1 Minute per Sensate Level",
        "effects": apply_state(
            "bad_gas_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _sensate_level(source),
                "contest": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Bad Gas",
                    "target_stat": "constitution",
                },
                "on_success_condition": "Gassy",
                "source_ability": "Bad Gas",
            },
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Phantasm",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "Create a mobile visual illusion that can be puppeted or programmed."
        ),
        "duration": "1 Minute per Sensate Level",
        "effects": apply_state(
            "phantasm_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _sensate_level(source),
                "illusion_type": "visual",
                "illusion_moves": True,
                "movement_radius_meters": 100,
                "area_square_meters": 6,
                "may_be_puppeted": True,
                "programmable_behavior_limit": "five_reasonably_sized_sentences",
                "pierce_check": {
                    "observer_stat": "perception",
                    "caster_stat": "charisma",
                    "caster_skill": "Phantasm",
                },
                "recognized_illusion_still_obscures_vision": True,
                "translucent_illusion_may_not_block_vision": True,
                "source_ability": "Phantasm",
            },
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": False,
        "target": "area",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Numbness",
        "cost": 25,
        "cost_pool": "sanity",
        "description": (
            "Inflict the Numb condition on a target."
        ),
        "duration": "1 Minute per Sensate Level",
        "effects": apply_state(
            "numbness_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _sensate_level(source),
                "contest": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Numbness",
                    "target_stat": "constitution",
                },
                "on_success_condition": "Numb",
                "source_ability": "Numbness",
            },
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Permanent Phantasm",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "Make one of your phantasms permanent."
        ),
        "duration": "Until Canceled, Dispelled, or Deceased",
        "effects": apply_state(
            "permanent_phantasm_active",
            value_fn=lambda source: {
                "active": True,
                "requires_existing_phantasm": True,
                "makes_phantasm_permanent": True,
                "only_one_permanent_phantasm": True,
                "ends_if_caster_dies": True,
                "freely_cancelable_by_caster": True,
                "source_ability": "Permanent Phantasm",
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
        "name": "Masterpiece",
        "cost": 40,
        "cost_pool": "fortune",
        "description": (
            "Before one crafting roll, roll twice and keep your preferred result."
        ),
        "duration": "One Crafting",
        "effects": apply_state(
            "masterpiece_active",
            value_fn=lambda source: {
                "active": True,
                "applies_to_next_crafting_roll": True,
                "roll_twice_keep_choice": True,
                "source_ability": "Masterpiece",
            },
        ),
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Vomit Comet",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "Inflict the Nauseated condition on a target that can vomit."
        ),
        "duration": "1 Turn per Sensate Level",
        "effects": apply_state(
            "vomit_comet_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": _sensate_level(source),
                "contest": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Vomit Comet",
                    "target_stat": "constitution",
                },
                "on_success_condition": "Nauseated",
                "fails_if_target_lacks_required_anatomy_or_instincts": True,
                "source_ability": "Vomit Comet",
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
        "name": "Blind",
        "cost": 40,
        "cost_pool": "sanity",
        "description": (
            "Inflict the Blind condition on a target."
        ),
        "duration": "1 Turn per Sensate Level",
        "effects": apply_state(
            "blind_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": _sensate_level(source),
                "contest": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Blind",
                    "target_stat": "constitution",
                },
                "on_success_condition": "Blind",
                "source_ability": "Blind",
            },
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Vivid Hallucination",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "Apply this to a Phantasm so its apparent attacks deal real HP damage."
        ),
        "duration": "Until the Illusion Fades",
        "effects": apply_state(
            "vivid_hallucination_active",
            value_fn=lambda source: {
                "active": True,
                "requires_existing_phantasm": True,
                "phantasm_deals_real_damage": True,
                "damage_pool": "hp",
                "damage_amount": _sensate_level(source),
                "bypasses_defenses": True,
                "source_ability": "Vivid Hallucination",
            },
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "area",
        "type": "skill",
    },

], source_type="adventure")