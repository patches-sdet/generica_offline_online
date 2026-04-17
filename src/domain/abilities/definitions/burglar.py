from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    inspect,
    passive_modifier,
    scaled_derived_buff,
    skill_check,
)
from domain.effects.base import Effect, EffectContext
from domain.effects.special.roll import RollModifierEffect


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _burglar_level(character) -> int:
    return character.get_progression_level("adventure", "Burglar", 0)


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


def _find_trap_difficulty(ctx, target) -> int:
    return int(getattr(target, "trap_difficulty", ctx.get_option("trap_difficulty", 100)))


def _disable_trap_difficulty(ctx, target) -> int:
    return int(getattr(target, "trap_difficulty", ctx.get_option("trap_difficulty", 100)))


def _breakfall_difficulty(ctx, target) -> int:
    """
    Placeholder for falling damage severity as a difficulty source.
    """
    return int(getattr(target, "fall_damage", ctx.get_option("fall_damage", 50)))


def _set_attack_attr(attack, key: str, value) -> None:
    setattr(attack, key, value)


# Passive modifier helpers

def _locksmith_modifier(ctx) -> None:
    if hasattr(ctx, "modify_lockpicking_bonus"):
        ctx.modify_lockpicking_bonus(
            amount=_ability_level(ctx.source, "Locksmith")
        )
        return

    states = _ensure_states(ctx.source)
    states["locksmith_active"] = {
        "active": True,
        "auto_reveal_lock_difficulty": True,
        "lockpicking_bonus": _ability_level(ctx.source, "Locksmith"),
        "applies_to_magical_locks": True,
        "source_ability": "Locksmith",
    }


# Custom effects / placeholders

class LootbagEffect(Effect):
    """
    Stores the enchanted lootbag state and carrying rules.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["lootbag_active"] = {
            "active": True,
            "duration_hours": 1,
            "capacity_slots": _ability_level(context.source, "Lootbag"),
            "capacity_rule": "one_item_or_identical_stack_per_slot",
            "ignores_weight_and_size_if_item_fits_opening": True,
            "spill_contents_if_destroyed": True,
            "source_ability": "Lootbag",
        }


class DistractionEffect(Effect):
    """
    Runtime-facing placeholder for guard-luring sound projection.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["distraction_ready"] = {
            "active": True,
            "attack_stat": "charisma",
            "skill_name": "Distraction",
            "target_resist_stat": "perception",
            "sound_range_feet": _ability_level(context.source, "Distraction") * 5,
            "effect": "investigate_sound_or_look_away",
            "source_ability": "Distraction",
        }


class JustTheWindEffect(Effect):
    """
    Placeholder for stealth-check reroll trigger.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["just_the_wind_ready"] = {
            "active": True,
            "trigger": "failed_stealth_check",
            "rerolls_allowed": 1,
            "must_accept_reroll": True,
            "source_ability": "Just the Wind",
        }


class BreakfallEffect(Effect):
    """
    Placeholder for fall-damage reduction roll.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["breakfall_ready"] = {
            "active": True,
            "trigger": "falling",
            "attack_stat": "agility",
            "skill_name": "Breakfall",
            "reduces_fall_damage_by_roll_result": True,
            "source_ability": "Breakfall",
        }


class InvisiblePicksEffect(Effect):
    """
    Placeholder for hidden-tool concealment state.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["invisible_picks_active"] = {
            "active": True,
            "duration_hours": _burglar_level(context.source),
            "conceals_lockpicks_and_trap_tools": True,
            "undetectable_except_true_sight": True,
            "requires_active_search_even_with_true_sight": True,
            "discovery_check": {
                "searcher_stat": "perception",
                "resist_stat": "dexterity",
            },
            "source_ability": "Invisible Picks",
        }


class ThiefsMaskEffect(Effect):
    """
    Placeholder for identity-concealment aura.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["thiefs_mask_active"] = {
            "active": True,
            "duration_hours": 1,
            "requires_mask_worn": True,
            "conceal_identity": True,
            "conceal_race_memory": True,
            "observers_present_at_donning_are_immune": True,
            "true_sight_negates": True,
            "ends_if_mask_removed": True,
            "source_ability": "Thief's Mask",
        }


class QuenchLightEffect(Effect):
    """
    Placeholder for suppressing a non-celestial light source.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["quench_light_ready"] = {
            "active": True,
            "duration_turns": _ability_level(context.source, "Quench Light"),
            "target_type": "noncelestial_light_source",
            "deactivate_light_source": True,
            "source_ability": "Quench Light",
        }


class HideyholeEffect(Effect):
    """
    Placeholder for extradimensional hideyhole creation.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["hideyhole_active"] = {
            "active": True,
            "duration_minutes": _ability_level(context.source, "Hideyhole"),
            "entry_window_turns": 1,
            "portal_target": "doorway_or_hole",
            "space_size": "large_closet",
            "expel_contents_on_expiration": True,
            "expel_contents_to_original_entry_point": True,
            "persists_if_burglar_enters": True,
            "source_ability": "Hideyhole",
        }


# Burglar

build_job("Burglar", [

    # Level 1

    {
        "name": "Case the Joint",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "The Burglar examines a structure or dwelling to learn its rough security level "
            "and the general theme and difficulty of guards, traps, and locks. "
            "This is a perception plus Case the Joint roll. Typical difficulties range from "
            "80 for a simple hut to 400 for a legendary labyrinth."
        ),
        "duration": "1 Inspection",
        "effects": skill_check(
            ability="Case the Joint",
            stat="perception",
            difficulty=_case_the_joint_difficulty,
            on_success=inspect(
                reveal_fn=_case_the_joint_reveal,
            ),
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "location",
        "type": "skill",
    },

    {
        "name": "Find Trap",
        "cost": 5,
        "cost_pool": "fortune",
        "description": (
            "While active, the Burglar adds the level of this skill to perception rolls "
            "made to detect traps."
        ),
        "duration": "1 Minute per Burglar Level",
        "effects": apply_state(
            "find_trap_active",
            value_fn=lambda source: {
                "duration_minutes": _burglar_level(source),
                "trap_detection_bonus": _ability_level(source, "Find Trap"),
                "source_ability": "Find Trap",
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Locksmith",
        "description": (
            "The Burglar automatically knows the difficulty to pick any lock they examine, "
            "including magical ones, and adds Locksmith level to all lockpicking attempts. "
            "This is an increase, not a buff."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_locksmith_modifier),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Lootbag",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "The Burglar enchants a bag or sack into a lootbag. It can carry one item or set "
            "of identical items per skill level regardless of weight or size, so long as the "
            "items fit through the opening. If the bag is destroyed, all contents spill out."
        ),
        "duration": "1 Hour",
        "effects": LootbagEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "bag",
        "type": "skill",
    },

    {
        "name": "Stealthy Step",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "While active, the Burglar adds Stealthy Step level to all stealth checks. "
            "This is an increase, not a buff."
        ),
        "duration": "1 Minute per Burglar Level",
        "effects": apply_state(
            "stealthy_step_active",
            value_fn=lambda source: {
                "duration_minutes": _burglar_level(source),
                "stealth_bonus": _ability_level(source, "Stealthy Step"),
                "source_ability": "Stealthy Step",
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Disable Trap",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "The Burglar adds Disable Trap level to attempts made to disable a trap."
        ),
        "duration": "1 Attempt",
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
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": True,
        "target": "trap",
        "type": "skill",
    },

    {
        "name": "Distraction",
        "cost": 20,
        "cost_pool": "moxie",
        "description": (
            "The Burglar creates a misleading sound to distract a guard or sentry. "
            "This is a charisma plus Distraction roll resisted by perception. The sound "
            "may originate up to five feet per skill level away from the Burglar."
        ),
        "duration": "1 Action",
        "effects": DistractionEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Just the Wind",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "When the Burglar fails a stealth check, they may reroll it, but must accept "
            "the new result even if it is worse. This skill has no levels."
        ),
        "duration": "Instant",
        "effects": JustTheWindEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Breakfall",
        "cost": 20,
        "cost_pool": "stamina",
        "description": (
            "When the Burglar falls, they may roll agility plus Breakfall. "
            "The damage dealt by the fall is reduced by the roll result."
        ),
        "duration": "Instant",
        "effects": BreakfallEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 10,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Wallwalker",
        "cost": 20,
        "cost_pool": "stamina",
        "description": (
            "While active, the Burglar ignores all negative situational climbing modifiers "
            "while scaling vertical surfaces."
        ),
        "duration": "1 Turn per Level",
        "effects": apply_state(
            "wallwalker_active",
            value_fn=lambda source: {
                "duration_turns": _ability_level(source, "Wallwalker"),
                "ignore_negative_climbing_modifiers": True,
                "applies_to": "vertical_surfaces",
                "source_ability": "Wallwalker",
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 10,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Invisible Picks",
        "cost": 25,
        "cost_pool": "fortune",
        "description": (
            "The Burglar renders their lockpicks and trap-disarming tools invisible and "
            "undetectable except to true sight. Even then, they must still be actively searched, "
            "and the searcher must succeed at a perception check against the Burglar's dexterity. "
            "This skill has no levels."
        ),
        "duration": "1 Hour per Burglar Level",
        "effects": InvisiblePicksEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 15,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Thief's Mask",
        "cost": 30,
        "cost_pool": "fortune",
        "description": (
            "While wearing a mask, the Burglar conceals their identity so thoroughly that even "
            "their race becomes hard to remember after they leave. Observers who saw the mask "
            "being donned are immune. True sight or mask removal ends the effect. "
            "This skill has no levels."
        ),
        "duration": "1 Hour",
        "effects": ThiefsMaskEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 15,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Acrobat's Muscles",
        "description": (
            "Through constant exercise and training, the Burglar gains a bonus to Endurance "
            "equal to Burglar level. This skill has no levels."
        ),
        "duration": "Passive Constant",
        "effects": scaled_derived_buff(
            scale_fn=lambda c: c.get_progression_level("adventure", "Burglar", 0),
            stat="endurance",
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Quench Light",
        "cost": 40,
        "cost_pool": "fortune",
        "description": (
            "The Burglar deactivates one non-celestial light source for a number of turns "
            "equal to this skill's level."
        ),
        "duration": "1 Turn per Level",
        "effects": QuenchLightEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 20,
        "scales_with_level": True,
        "target": "light_source",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Ceilingwalker",
        "cost": 50,
        "cost_pool": "stamina",
        "description": (
            "While active, the Burglar can climb across ceilings and horizontal surfaces "
            "with no roll required."
        ),
        "duration": "1 Turn per Level",
        "effects": apply_state(
            "ceilingwalker_active",
            value_fn=lambda source: {
                "duration_turns": _ability_level(source, "Ceilingwalker"),
                "can_traverse_ceilings": True,
                "no_roll_required": True,
                "source_ability": "Ceilingwalker",
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Hideyhole",
        "cost": 100,
        "cost_pool": "fortune",
        "description": (
            "The Burglar turns a doorway or hole into a temporary extradimensional hideyhole "
            "about the size of a large closet. The portal stays open briefly unless the Burglar enters. "
            "If the skill expires, everyone inside is expelled back to the original point of entry."
        ),
        "duration": "1 Minute per Level",
        "effects": HideyholeEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": True,
        "target": "doorway_or_hole",
        "type": "skill",
    },

], source_type="adventure")