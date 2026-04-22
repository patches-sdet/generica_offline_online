from domain.abilities import ability_level, progression_level
from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    inspect,
    passive_modifier,
    scaled_derived_buff,
    skill_check,
)

def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states

def _case_the_joint_difficulty(ctx, target) -> int:
    if hasattr(target, "difficulty"):
        return int(target.difficulty)

    security_level = getattr(target, "security_level", None)
    default_map = {
        "simple": 80,
        "merchant": 120,
        "castle": 180,
        "dungeon": 250,
        "legendary": 400,
    }
    if security_level in default_map:
        return default_map[security_level]

    return int(ctx.get_option("site_difficulty", 120))

def _case_the_joint_reveal(ctx, target) -> dict:
    return {
        "security_level": getattr(target, "security_level", "unknown"),
        "guard_theme": getattr(target, "guard_theme", "unknown"),
        "lock_difficulty": getattr(target, "lock_difficulty", "unknown"),
        "trap_difficulty": getattr(target, "trap_difficulty", "unknown"),
    }

def _disable_trap_difficulty(ctx, target) -> int:
    return int(getattr(target, "trap_difficulty", ctx.get_option("trap_difficulty", 100)))

# Passive runtime helpers

def _locksmith_modifier(ctx) -> None:
    if hasattr(ctx, "modify_lockpicking_bonus"):
        ctx.modify_lockpicking_bonus(
            amount=ability_level(ctx.source, "Locksmith")
        )
        return

    states = _ensure_states(ctx.source)
    states["locksmith_active"] = {
        "active": True,
        "auto_reveal_lock_difficulty": True,
        "lockpicking_bonus": ability_level(ctx.source, "Locksmith"),
        "applies_to_magical_locks": True,
        "source_ability": "Locksmith",
    }

# Burglar

build_job(
    "Burglar",
    [
        # Level 1
        {
            "name": "Case the Joint",
            "type": "skill",
            "cost": 10,
            "cost_pool": "fortune",
            "duration": "1 Inspection",
            "target": "location",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "The Burglar examines a structure or dwelling to learn its rough security level "
                "and the general theme and difficulty of guards, traps, and locks. "
                "This is a Perception + Case the Joint roll. Typical difficulties range from "
                "80 for a simple hut to 400 for a legendary labyrinth."
            ),
            "effects": skill_check(
                ability="Case the Joint",
                stat="perception",
                difficulty=_case_the_joint_difficulty,
                on_success=inspect(
                    reveal_fn=_case_the_joint_reveal,
                ),
            ),
        },
        {
            "name": "Find Trap",
            "type": "skill",
            "cost": 5,
            "cost_pool": "fortune",
            "duration": "1 Minute per Burglar Level",
            "target": "self",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "While active, the Burglar adds the level of this skill to perception rolls "
                "made to detect traps."
            ),
            "effects": apply_state(
                "find_trap_active",
                value_fn=lambda source: {
                    "duration_minutes": progression_level(source, "adventure", "Burglar"),
                    "trap_detection_bonus": ability_level(source, "Find Trap"),
                    "source_ability": "Find Trap",
                },
            ),
        },
        {
            "name": "Locksmith",
            "type": "passive",
            "target": "self",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "The Burglar automatically knows the difficulty to pick any lock they examine, "
                "including magical ones, and adds Locksmith level to all lockpicking attempts. "
                "This is an increase, not a buff."
            ),
            "duration": "Passive Constant",
            "effects": passive_modifier(_locksmith_modifier),
        },
        {
            "name": "Lootbag",
            "type": "skill",
            "cost": 10,
            "cost_pool": "fortune",
            "duration": "1 Hour",
            "target": "bag",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "The Burglar enchants a bag or sack into a lootbag. It can carry one item or set "
                "of identical items per skill level regardless of weight or size, so long as the "
                "items fit through the opening. If the bag is destroyed, all contents spill out."
            ),
            "effects": apply_state(
                "lootbag_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_hours": 1,
                    "capacity_slots": ability_level(source, "Lootbag"),
                    "capacity_rule": "one_item_or_identical_stack_per_slot",
                    "ignores_weight_and_size_if_item_fits_opening": True,
                    "spill_contents_if_destroyed": True,
                    "source_ability": "Lootbag",
                },
            ),
        },
        {
            "name": "Stealthy Step",
            "type": "skill",
            "cost": 10,
            "cost_pool": "stamina",
            "duration": "1 Minute per Burglar Level",
            "target": "self",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "While active, the Burglar adds Stealthy Step level to all stealth checks. "
                "This is an increase, not a buff."
            ),
            "effects": apply_state(
                "stealthy_step_active",
                value_fn=lambda source: {
                    "duration_minutes": progression_level(source, "adventure", "Burglar"),
                    "stealth_bonus": ability_level(source, "Stealthy Step"),
                    "source_ability": "Stealthy Step",
                },
            ),
        },

        # Level 5
        {
            "name": "Disable Trap",
            "type": "skill",
            "cost": 10,
            "cost_pool": "fortune",
            "duration": "1 Attempt",
            "target": "trap",
            "required_level": 5,
            "scales_with_level": True,
            "description": (
                "The Burglar adds Disable Trap level to attempts made to disable a trap."
            ),
            "effects": skill_check(
                ability="Disable Trap",
                stat="dexterity",
                difficulty=_disable_trap_difficulty,
                on_success=apply_state(
                    "trap_disabled",
                    value_fn=lambda source: {
                        "disabled": True,
                        "source_ability": "Disable Trap",
                    },
                ),
            ),
        },
        {
            "name": "Distraction",
            "type": "skill",
            "cost": 20,
            "cost_pool": "moxie",
            "duration": "1 Action",
            "target": "enemy",
            "required_level": 5,
            "scales_with_level": True,
            "description": (
                "The Burglar creates a misleading sound to distract a guard or sentry. "
                "This is a Charisma + Distraction roll resisted by Perception. The sound "
                "may originate up to five feet per skill level away from the Burglar."
            ),
            "effects": apply_state(
                "distraction_ready",
                value_fn=lambda source: {
                    "active": True,
                    "attack_stat": "charisma",
                    "skill_name": "Distraction",
                    "target_resist_stat": "perception",
                    "sound_range_feet": ability_level(source, "Distraction") * 5,
                    "effect": "investigate_sound_or_look_away",
                    "source_ability": "Distraction",
                },
            ),
        },
        {
            "name": "Just the Wind",
            "type": "skill",
            "cost": 10,
            "cost_pool": "fortune",
            "duration": "Instant",
            "target": "self",
            "required_level": 5,
            "scales_with_level": False,
            "description": (
                "When the Burglar fails a stealth check, they may reroll it, but must accept "
                "the new result even if it is worse. This skill has no levels."
            ),
            "effects": apply_state(
                "just_the_wind_ready",
                value_fn=lambda source: {
                    "active": True,
                    "trigger": "failed_stealth_check",
                    "rerolls_allowed": 1,
                    "must_accept_reroll": True,
                    "source_ability": "Just the Wind",
                },
            ),
        },

        # Level 10
        {
            "name": "Breakfall",
            "type": "skill",
            "cost": 20,
            "cost_pool": "stamina",
            "duration": "Instant",
            "target": "self",
            "required_level": 10,
            "scales_with_level": True,
            "description": (
                "When the Burglar falls, they may roll Agility + Breakfall. "
                "The damage dealt by the fall is reduced by the roll result."
            ),
            "effects": apply_state(
                "breakfall_ready",
                value_fn=lambda source: {
                    "active": True,
                    "trigger": "falling",
                    "attack_stat": "agility",
                    "skill_name": "Breakfall",
                    "reduces_fall_damage_by_roll_result": True,
                    "source_ability": "Breakfall",
                },
            ),
        },
        {
            "name": "Wallwalker",
            "type": "skill",
            "cost": 20,
            "cost_pool": "stamina",
            "duration": "1 Turn per Level",
            "target": "self",
            "required_level": 10,
            "scales_with_level": True,
            "description": (
                "While active, the Burglar ignores all negative situational climbing modifiers "
                "while scaling vertical surfaces."
            ),
            "effects": apply_state(
                "wallwalker_active",
                value_fn=lambda source: {
                    "duration_turns": ability_level(source, "Wallwalker"),
                    "ignore_negative_climbing_modifiers": True,
                    "applies_to": "vertical_surfaces",
                    "source_ability": "Wallwalker",
                },
            ),
        },

        # Level 15
        {
            "name": "Invisible Picks",
            "type": "skill",
            "cost": 25,
            "cost_pool": "fortune",
            "duration": "1 Hour per Burglar Level",
            "target": "self",
            "required_level": 15,
            "scales_with_level": False,
            "description": (
                "The Burglar renders their lockpicks and trap-disarming tools invisible and "
                "undetectable except to true sight. Even then, they must still be actively searched, "
                "and the searcher must succeed at a Perception check against the Burglar's Dexterity. "
                "This skill has no levels."
            ),
            "effects": apply_state(
                "invisible_picks_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_hours": progression_level(source, "adventure", "Burglar"),
                    "conceals_lockpicks_and_trap_tools": True,
                    "undetectable_except_true_sight": True,
                    "requires_active_search_even_with_true_sight": True,
                    "discovery_check": {
                        "searcher_stat": "perception",
                        "resist_stat": "dexterity",
                    },
                    "source_ability": "Invisible Picks",
                },
            ),
        },
        {
            "name": "Thief's Mask",
            "type": "skill",
            "cost": 30,
            "cost_pool": "fortune",
            "duration": "1 Hour",
            "target": "self",
            "required_level": 15,
            "scales_with_level": False,
            "description": (
                "While wearing a mask, the Burglar conceals their identity so thoroughly that even "
                "their race becomes hard to remember after they leave. Observers who saw the mask "
                "being donned are immune. True sight or mask removal ends the effect. "
                "This skill has no levels."
            ),
            "effects": apply_state(
                "thiefs_mask_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_hours": 1,
                    "requires_mask_worn": True,
                    "conceal_identity": True,
                    "conceal_race_memory": True,
                    "observers_present_at_donning_are_immune": True,
                    "true_sight_negates": True,
                    "ends_if_mask_removed": True,
                    "source_ability": "Thief's Mask",
                },
            ),
        },

        # Level 20
        {
            "name": "Acrobat's Muscles",
            "type": "passive",
            "target": "self",
            "required_level": 20,
            "scales_with_level": False,
            "description": (
                "Through constant exercise and training, the Burglar gains a bonus to Endurance "
                "equal to Burglar level. This skill has no levels."
            ),
            "duration": "Passive Constant",
            "effects": scaled_derived_buff(
                scale_fn=lambda source: progression_level(source, "adventure", "Burglar"),
                stat="endurance",
            ),
        },
        {
            "name": "Quench Light",
            "type": "skill",
            "cost": 40,
            "cost_pool": "fortune",
            "duration": "1 Turn per Level",
            "target": "light_source",
            "required_level": 20,
            "scales_with_level": True,
            "description": (
                "The Burglar deactivates one non-celestial light source for a number of turns "
                "equal to this skill's level."
            ),
            "effects": apply_state(
                "quench_light_ready",
                value_fn=lambda source: {
                    "active": True,
                    "duration_turns": ability_level(source, "Quench Light"),
                    "target_type": "noncelestial_light_source",
                    "deactivate_light_source": True,
                    "source_ability": "Quench Light",
                },
            ),
        },

        # Level 25
        {
            "name": "Ceilingwalker",
            "type": "skill",
            "cost": 50,
            "cost_pool": "stamina",
            "duration": "1 Turn per Level",
            "target": "self",
            "required_level": 25,
            "scales_with_level": True,
            "description": (
                "While active, the Burglar can climb across ceilings and horizontal surfaces "
                "with no roll required."
            ),
            "effects": apply_state(
                "ceilingwalker_active",
                value_fn=lambda source: {
                    "duration_turns": ability_level(source, "Ceilingwalker"),
                    "can_traverse_ceilings": True,
                    "no_roll_required": True,
                    "source_ability": "Ceilingwalker",
                },
            ),
        },
        {
            "name": "Hideyhole",
            "type": "skill",
            "cost": 100,
            "cost_pool": "fortune",
            "duration": "1 Minute per Level",
            "target": "doorway_or_hole",
            "required_level": 25,
            "scales_with_level": True,
            "description": (
                "The Burglar turns a doorway or hole into a temporary extradimensional hideyhole "
                "about the size of a large closet. The portal stays open briefly unless the Burglar enters. "
                "If the skill expires, everyone inside is expelled back to the original point of entry."
            ),
            "effects": apply_state(
                "hideyhole_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_minutes": ability_level(source, "Hideyhole"),
                    "entry_window_turns": 1,
                    "portal_target": "doorway_or_hole",
                    "space_size": "large_closet",
                    "expel_contents_on_expiration": True,
                    "expel_contents_to_original_entry_point": True,
                    "persists_if_burglar_enters": True,
                    "source_ability": "Hideyhole",
                },
            ),
        },
    ],
    source_type="adventure",
)