from domain.abilities.builders._job_builder import build_job
from domain.abilities import ability_level, ctx_ability_level, progression_level, ctx_progression_level
from domain.abilities.patterns import (
    apply_state,
    passive_modifier,
    aura,
)


# Local helpers

def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


# Passive helpers

def _dietary_restrictions_modifier(ctx) -> None:
    states = _ensure_states(ctx)
    states["dietary_restrictions"] = {
        "active": True,
        "requires_no_unhealthy_food_for_last_week": True,
        "small_buff_to_all_pools": True,
        "stack_limit": ability_level(ctx, "Dietary Restrictions") * 2,
        "remove_all_stacks_if_unhealthy_food_eaten": True,
        "levels_per_week_on_diet": True,
        "cannot_be_raised_by_grind_points": True,
        "backlogged_weeks_count": True,
        "source_ability": "Dietary Restrictions",
    }


def _work_it_baby_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["work_it_baby"] = {
        "active": True,
        "bonus_percent_per_level": 1,
        "affected_items": "worn_and_wielded_items_that_confer_bonuses",
        "source_ability": "Work It Baby",
    }


build_job("Model", [

    # Level 1

    {
        "name": "Dietary Restrictions",
        "description": (
            "While you have avoided UNHEALTHY food for the past week, gain stacking buffs to all pools. "
            "Eating UNHEALTHY food removes all stacks."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_dietary_restrictions_modifier),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Fascination",
        "description": (
            "After healing, aiding, or otherwise being nice to an enemy in combat, they may become "
            "temporarily fascinated with you if they fail to resist."
        ),
        "duration": "1 Turn per Skill Level",
        "effects": apply_state(
            "fascination_active",
            value_fn=lambda source: {
                "active": True,
                "trigger": "heal_aid_or_be_kind_to_enemy_in_combat",
                "contest": {
                    "target_stat": "willpower",
                    "caster_stat": "charisma",
                    "caster_bonus": progression_level(source, "adventure", "Model"),
                },
                "on_failure": "target_becomes_fascinated",
                "duration_turns": ability_level(source, "Fascination"),
                "source_ability": "Fascination",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Flex",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "Buff your Endurance and Armor by this skill's level."
        ),
        "duration": "1 Minute per Model Level",
        "effects": apply_state(
            "flex_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Model"),
                "endurance_bonus": ability_level(source, "Flex"),
                "armor_bonus": ability_level(source, "Flex"),
                "source_ability": "Flex",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Self-Esteem",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "Buff your Mental Fortitude and Cool by this skill's level."
        ),
        "duration": "1 Minute per Model Level",
        "effects": apply_state(
            "self_esteem_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Model"),
                "mental_fortitude_bonus": ability_level(source, "Self-Esteem"),
                "cool_bonus": ability_level(source, "Self-Esteem"),
                "source_ability": "Self-Esteem",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Work It Baby",
        "description": (
            "All worn and wielded items that confer bonuses have those bonuses increased by 1% per skill level."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_work_it_baby_modifier),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Level 5

    {
        "name": "Call Outfit",
        "cost": 20,
        "cost_pool": "moxie",
        "description": (
            "Instantly summon one of your regular equipment sets and clothe yourself in it."
        ),
        "duration": "Instant",
        "effects": apply_state(
            "call_outfit_active",
            value_fn=lambda source: {
                "active": True,
                "summon_regular_equipment_set": True,
                "equip_immediately": True,
                "set_must_be_kept_together": True,
                "primary_material_must_be_lighter_than_metal": True,
                "small_metal_accessories_allowed": True,
                "barrier_check": {
                    "caster_stat": "charisma",
                    "caster_skill": "Call Outfit",
                    "difficulty": "ward_strength_or_caster_willpower",
                },
                "source_ability": "Call Outfit",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Makeup",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "Apply makeup that buffs one chosen skill by this skill's level."
        ),
        "duration": "Until Smeared or Removed",
        "effects": apply_state(
            "makeup_active",
            value_fn=lambda source: {
                "active": True,
                "choose_one_skill": True,
                "chosen_skill_bonus": ability_level(source, "Makeup"),
                "makeup_must_match_job_theme": True,
                "source_ability": "Makeup",
            },
        ),
        "required_level": 5,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Strong Pose",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "Buff your Strength by this skill's level."
        ),
        "duration": "1 Minute per Model Level",
        "effects": aura(
            apply_state(
            "strong_pose_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Model"),
                "strength_bonus": ability_level(source, "Strong Pose"),
                "source_ability": "Strong Pose",
            },
        ),
        aura_id="model_pose",
        ),
        "required_level": 5,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Adjust Weight",
        "cost": 20,
        "cost_pool": "stamina",
        "description": (
            "Adjust your weight up or down by a percentage based on your Model level."
        ),
        "duration": "1 Minute per Skill Level",
        "effects": apply_state(
            "adjust_weight_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": ability_level(source, "Adjust Weight"),
                "weight_adjustment_percent_max": progression_level(source, "adventure", "Model"),
                "can_increase_or_decrease_weight": True,
                "body_shape_changes_with_weight": True,
                "situational_effects_gm_defined": True,
                "source_ability": "Adjust Weight",
            },
        ),
        "required_level": 10,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Sexy Pose",
        "cost": 20,
        "cost_pool": "stamina",
        "description": (
            "Buff your Charisma by this skill's level when dealing with those capable of sexual attraction to you."
        ),
        "duration": "1 Minute per Model Level",
        "effects": aura(
            apply_state(
            "sexy_pose_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Model"),
                "charisma_bonus": ability_level(source, "Sexy Pose"),
                "only_applies_to_targets_capable_of_sexual_attraction": True,
                "source_ability": "Sexy Pose",
            },
        ),
        aura_id="model_pose",
        ),
        "required_level": 10,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Flexible Pose",
        "cost": 30,
        "cost_pool": "stamina",
        "description": (
            "Buff your Agility and Dexterity by this skill's level."
        ),
        "duration": "1 Minute per Model Level",
        "effects": aura(
            apply_state(
            "flexible_pose_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Model"),
                "agility_bonus": ability_level(source, "Flexible Pose"),
                "dexterity_bonus": ability_level(source, "Flexible Pose"),
                "source_ability": "Flexible Pose",
            },
        ),
        aura_id="model_pose",
        ),
        "required_level": 15,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Scornful Laugh",
        "cost": 30,
        "cost_pool": "moxie",
        "description": (
            "A moxie-targeting attack against all enemies within a number of feet equal to your Model level."
        ),
        "duration": "Instant",
        "effects": apply_state(
            "scornful_laugh_active",
            value_fn=lambda source: {
                "active": True,
                "attack_stat": "charisma",
                "attack_skill": "Scornful Laugh",
                "target_stat": "willpower",
                "target_pool": "moxie",
                "radius_feet": progression_level(source, "adventure", "Model"),
                "multi_target_enemies_in_radius": True,
                "source_ability": "Scornful Laugh",
            },
        ),
        "required_level": 15,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Do You Even Lift?",
        "cost": 40,
        "cost_pool": "stamina",
        "description": (
            "Add this skill to Strength rolls for lifting heavy objects and other non-combat feats of strength."
        ),
        "duration": "1 Turn per Model Level",
        "effects": apply_state(
            "do_you_even_lift_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": progression_level(source, "adventure", "Model"),
                "strength_roll_bonus_for_lifting": ability_level(source, "Do You Even Lift?"),
                "strength_roll_bonus_for_noncombat_feats": ability_level(source, "Do You Even Lift?"),
                "combat_use_gm_discretion": True,
                "source_ability": "Do You Even Lift?",
            },
        ),
        "required_level": 20,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Stubborn Pose",
        "cost": 40,
        "cost_pool": "moxie",
        "description": (
            "Buff your Willpower and Wisdom by this skill's level."
        ),
        "duration": "1 Minute per Model Level",
        "effects": aura(
            apply_state(
            "stubborn_pose_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Model"),
                "willpower_bonus": ability_level(source, "Stubborn Pose"),
                "wisdom_bonus": ability_level(source, "Stubborn Pose"),
                "source_ability": "Stubborn Pose",
            },
        ),
        aura_id="model_pose",
        ),
        "required_level": 20,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Fitness Obsession",
        "cost": 50,
        "cost_pool": "stamina",
        "description": (
            "Buff all physical attributes by this skill's level."
        ),
        "duration": "1 Turn",
        "effects": apply_state(
            "fitness_obsession_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": 1,
                "physical_attribute_bonus": ability_level(source, "Fitness Obsession"),
                "applies_to": (
                    "strength",
                    "constitution",
                    "dexterity",
                    "agility",
                ),
                "source_ability": "Fitness Obsession",
            },
        ),
        "required_level": 25,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Love Me",
        "cost": 50,
        "cost_pool": "moxie",
        "description": (
            "Attempt to charm a target into treating you as their best friend or better."
        ),
        "duration": "1 Attempt",
        "effects": apply_state(
            "love_me_active",
            value_fn=lambda source: {
                "active": True,
                "contest": {
                    "caster_stat": "charisma",
                    "caster_skill": "Love Me",
                    "target_stat": "willpower",
                },
                "on_success": {
                    "target_charmed": True,
                    "target_treats_you_as_best_friend_or_better": True,
                    "target_cooperates_with_reasonable_suggestions": True,
                    "reasonableness_depends_on_target_nature": True,
                },
                "source_ability": "Love Me",
            },
        ),
        "required_level": 25,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

], source_type="adventure")