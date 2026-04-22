from domain.abilities import ability_level, progression_level
from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    composite,
    conditional_damage,
    inspect,
    modify_next_attack,
    passive_modifier,
    scaled_derived_buff,
    scaled_stat_buff,
    skill_check,
)
from domain.conditions.state import IS_HELPLESS, IS_SURPRISED
from domain.effects.special.roll import RollModifierEffect


def _progression_total(entity) -> int:
    progressions = getattr(entity, "progressions", None)
    if isinstance(progressions, dict):
        return sum(p.level for p in progressions.values())
    return 0

def _compare_total_levels(source, target) -> str:
    """
    Lightweight inspection helper for Cold Read.
    """
    source_total = _progression_total(source)
    target_total = _progression_total(target)

    if target_total <= 0:
        return "unknown"

    if source_total >= target_total + 10:
        return "far weaker than you"
    if source_total > target_total:
        return "weaker than you"
    if source_total == target_total:
        return "about equal to you"
    if target_total >= source_total + 10:
        return "far stronger than you"
    return "stronger than you"

def _get_vulnerabilities(target) -> list[str]:
    """
    Lightweight inspection helper for Cold Read.
    Uses visible states/tags only; deeper combat vulnerability logic can evolve later.
    """
    results: list[str] = []

    states = getattr(target, "states", {}) or {}
    tags = getattr(target, "tags", set()) or set()

    if "surprised" in states:
        results.append("surprised")
    if "helpless" in states:
        results.append("helpless")
    if "hobbled" in states:
        results.append("hobbled")
    if "numbed" in states:
        results.append("numbed")
    if "paralyzed" in states:
        results.append("paralyzed")

    if "construct" in tags:
        results.append("construct")
    if "undead" in tags:
        results.append("undead")

    return results

def _set_attack_attr(attack, key: str, value) -> None:
    setattr(attack, key, value)

def _append_attack_list_attr(attack, key: str, value) -> None:
    current = getattr(attack, key, None)
    if current is None:
        current = []
        setattr(attack, key, current)
    current.append(value)

# Attack modifiers

def _hindering_strike_modifier(ctx, attack) -> None:
    _append_attack_list_attr(
        attack,
        "on_hit_conditions",
        {
            "condition": "numbed",
            "duration_rounds": ability_level(ctx.source, "Hindering Strike"),
        },
    )

def _hobbling_strike_modifier(ctx, attack) -> None:
    _append_attack_list_attr(
        attack,
        "on_hit_conditions",
        {
            "condition": "hobbled",
            "duration_rounds": ability_level(ctx.source, "Hobbling Strike"),
        },
    )

def _armor_piercer_modifier(ctx, attack) -> None:
    _set_attack_attr(
        attack,
        "ignore_armor",
        ability_level(ctx.source, "Armor Piercer"),
    )

def _paralyzing_strike_modifier(ctx, attack) -> None:
    _append_attack_list_attr(
        attack,
        "on_hit_saving_effects",
        {
            "check_stat": "constitution",
            "condition": "paralyzed",
            "remove_dc": 250,
            "duration_rounds": ability_level(ctx.source, "Paralyzing Strike"),
        },
    )

# Passive / runtime helpers

def _silent_killer_roll_bonus(source) -> int:
    return ability_level(source, "Silent Killer")


def _unobtrusive_passive(ctx):
    return composite(
        scaled_stat_buff(
            scale_fn=lambda source: ability_level(source, "Unobtrusive"),
            stats={"charisma": 1},
        ),
        apply_state(
            "low_profile",
            value_fn=lambda source: ability_level(source, "Unobtrusive") > 0,
        ),
    )

# Assassin

build_job(
    "Assassin",
    [
        # Level 1
        {
            "name": "Backstab",
            "type": "skill",
            "cost": 10,
            "cost_pool": "stamina",
            "duration": "5 minutes",
            "target": "enemy",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "The Assassin prepares to target weak spots. For the next five minutes, "
                "they add one point of damage per Backstab level to attacks made on "
                "surprised or helpless targets. At GM discretion, this may also apply "
                "when striking a target's back."
            ),
            "effects": conditional_damage(
                scale_fn=lambda source: ability_level(source, "Backstab"),
                condition=lambda ctx, target: (
                    IS_SURPRISED(ctx, target) or IS_HELPLESS(ctx, target)
                ),
            ),
        },

        {
            "name": "Cold Read",
            "type": "skill",
            "cost": 5,
            "cost_pool": "moxie",
            "duration": "1 turn",
            "target": "enemy",
            "required_level": 1,
            "scales_with_level": False,
            "description": (
                "The Assassin looks over a target, assessing their challenge and weak "
                "points. This is a Perception + Cold Read roll resisted by the target's "
                "Charisma roll."
            ),
            "effects": skill_check(
                ability="Cold Read",
                stat="perception",
                difficulty=lambda ctx, target: target.roll_charisma(),
                on_success=inspect(
                    reveal_fn=lambda ctx, target: {
                        "relative_power": _compare_total_levels(ctx.source, target),
                        "vulnerabilities": _get_vulnerabilities(target),
                    }
                ),
            ),
        },

        {"grant": "Fast as Death", "required_level": 1},

        {"grant": "Quickdraw", "required_level": 1},

        {
            "name": "Unobtrusive",
            "type": "passive",
            "target": "self",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "Assassins are good at hiding in plain sight. This adds Unobtrusive to "
                "Charisma when blending in, moving without suspicion, or otherwise "
                "avoiding notice through demeanor."
            ),
            "effects": composite(
                scaled_stat_buff(
                    scale_fn=lambda source: ability_level(source, "Unobtrusive"),
                    stats={"charisma": 1},
                ),
                apply_state(
                    "low_profile",
                    value_fn=lambda source: ability_level(source, "Unobtrusive") > 0,
                ),
            ),
        },

        # Level 5
        {
            "name": "Hindering Strike",
            "type": "skill",
            "cost": 10,
            "cost_pool": "stamina",
            "duration": "1 attack",
            "target": "self",
            "required_level": 5,
            "scales_with_level": True,
            "description": (
                "Strategic cuts to the right muscle groups make hard targets easier to "
                "deal with. A successful attack inflicts the Numbed condition for rounds "
                "equal to this skill's level."
            ),
            "effects": modify_next_attack(_hindering_strike_modifier),
        },

        {
            "name": "Poison Blade",
            "type": "skill",
            "cost": 10,
            "cost_pool": "fortune",
            "duration": "Instant",
            "target": "self",
            "required_level": 5,
            "scales_with_level": False,
            "description": (
                "Instantly takes any poison on the Assassin's person or within reach and "
                "applies it to the weapon they are holding. This skill has no levels."
            ),
            "effects": apply_state(
                "poison_blade_ready",
                value_fn=lambda source: {
                    "active": True,
                    "consume_nearest_poison": True,
                },
            ),
        },

        {
            "name": "Silent Killer",
            "type": "skill",
            "cost": 15,
            "cost_pool": "moxie",
            "duration": "10 minutes",
            "target": "self",
            "required_level": 5,
            "scales_with_level": True,
            "description": (
                "The Assassin controls their body and movement to the point where they "
                "make no noise. While active, they make no sound and gain +1 per level "
                "to stealth rolls where sound matters."
            ),
            "effects": apply_state(
                "silent_killer",
                value_fn=lambda source: {
                "silent": True,
                "duration_minutes": 10,
                "stealth_sound_bonus": ability_level(source, "Silent Killer"),
                },
            ),
        },

        # Level 10
        {
            "name": "Cold as Death",
            "type": "passive",
            "target": "self",
            "required_level": 10,
            "scales_with_level": False,
            "description": (
                "A professional killer learns not to let emotion show. This adds the "
                "Assassin's level to Cool. This skill has no levels."
            ),
            "effects": scaled_derived_buff(
                scale_fn=lambda source: progression_level(source, "adventure", "Assassin"),
                stat="cool",
            ),
        },

        {
            "name": "Lost in Crowds",
            "type": "skill",
            "cost": 20,
            "cost_pool": "moxie",
            "duration": "Instant",
            "target": "self",
            "required_level": 10,
            "scales_with_level": False,
            "description": (
                "In a populated area, the Assassin may escape pursuit by blending into "
                "bystanders. This substitutes an Agility + Unobtrusive roll for chase "
                "checks. This skill has no levels."
            ),
            "effects": apply_state(
                "lost_in_crowds",
                value_fn=lambda source: {
                    "active": True,
                    "use_unobtrusive_for_chase": True,
                },
            ),
        },

        # Level 15
        {
            "name": "Fade Out",
            "type": "skill",
            "cost": 20,
            "cost_pool": "moxie",
            "duration": "Instant",
            "target": "self",
            "required_level": 15,
            "scales_with_level": False,
            "description": (
                "When the Assassin fails a stealth check, they may immediately reroll "
                "once. They must accept the reroll. This skill may only be used once "
                "per turn."
            ),
            "effects": apply_state(
                "faded",
                value_fn=lambda source: {
                    "allow_stealth_reroll": True,
                    "uses_remaining_this_turn": 1,
                },
            ),
        },

        {
            "name": "Hobbling Strike",
            "type": "skill",
            "cost": 25,
            "cost_pool": "stamina",
            "duration": "1 attack",
            "target": "self",
            "required_level": 15,
            "scales_with_level": True,
            "description": (
                "A precise strike to key tendons leaves the target hobbled. A successful "
                "attack inflicts the Hobbled condition for rounds equal to this skill's "
                "level."
            ),
            "effects": modify_next_attack(_hobbling_strike_modifier),
        },

        # Level 20
        {
            "name": "Armor Piercer",
            "type": "skill",
            "cost": 40,
            "cost_pool": "stamina",
            "duration": "1 attack",
            "target": "self",
            "required_level": 20,
            "scales_with_level": True,
            "description": (
                "When attacking heavily armored foes, the Assassin strikes where the "
                "armor isn't. A successful attack ignores 1 point of armor per level "
                "of this skill."
            ),
            "effects": modify_next_attack(_armor_piercer_modifier),
        },

        {
            "name": "Undetectable",
            "type": "skill",
            "cost": 50,
            "cost_pool": "moxie",
            "duration": "1 minute",
            "target": "self",
            "required_level": 20,
            "scales_with_level": True,
            "description": (
                "Detection spells, magical effects, or perception-boosting magic that "
                "would normally notice the Assassin are reduced by 1 level per "
                "Undetectable level."
            ),
            "effects": apply_state(
                "undetectable",
                value_fn=lambda source: {
                    "magic_detection_reduction": ability_level(source, "Undetectable"),
                    "duration_minutes": 1,
                },
            ),
        },

        # Level 25
        {
            "name": "Getaway/Pursuit",
            "type": "skill",
            "cost": 50,
            "cost_pool": "stamina",
            "duration": "1 chase stage",
            "target": "self",
            "required_level": 25,
            "scales_with_level": False,
            "description": (
                "The Assassin may automatically succeed at a chase stage, regardless of "
                "difficulty. This skill has no levels."
            ),
            "effects": apply_state(
                "getaway_pursuit",
                value_fn=lambda source: {
                    "auto_pass_chase_stage": True,
                },
            ),
        },

        {
            "name": "Paralyzing Strike",
            "type": "skill",
            "cost": 50,
            "cost_pool": "fortune",
            "duration": "1 attack",
            "target": "self",
            "required_level": 25,
            "scales_with_level": True,
            "description": (
                "The Assassin strikes a nerve cluster that can paralyze the target "
                "temporarily. On hit, the target must make a Constitution check using "
                "the Assassin's total attack roll as the difficulty. On failure, the "
                "target gains Paralyzed with removal difficulty 250."
            ),
            "effects": modify_next_attack(_paralyzing_strike_modifier),
        },
    ],
    source_type="adventure",
)