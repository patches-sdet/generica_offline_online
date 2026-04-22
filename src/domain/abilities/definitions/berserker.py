from domain.abilities import ability_level, progression_level
from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    modify_next_attack,
    on_event,
    passive_modifier,
    scaled_derived_buff,
)

def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


def _set_attack_attr(attack, key: str, value) -> None:
    setattr(attack, key, value)

# Attack modifiers

def _furious_strike_modifier(ctx, attack) -> None:
    _set_attack_attr(
        attack,
        "bonus_damage",
        progression_level(ctx, "adventure", "Berserker") + ability_level(ctx.source, "Furious Strike"),
    )
    _set_attack_attr(attack, "furious_strike", True)

def _wide_swing_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "targets_all_adjacent_enemies", True)
    _set_attack_attr(attack, "single_roll_for_all_targets", True)
    _set_attack_attr(attack, "bonus_damage", 1)
    _set_attack_attr(attack, "cost_hp_per_adjacent_foe", 10)
    _set_attack_attr(
        attack,
        "experience_difficulty_source",
        "highest_agility_among_successfully_struck_foes",
    )


def _bigger_they_are_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "ignore_armor", progression_level(ctx, "adventure", "Berserker") * 2)
    _set_attack_attr(attack, "minimum_target_size", "self_or_larger")
    _set_attack_attr(attack, "the_bigger_they_are", True)

# Passive / runtime helpers

def _two_handed_specialist_modifier(ctx) -> None:
    """
    Runtime-facing passive hook for two-handed weapon attacks.
    """
    if hasattr(ctx, "modify_two_handed_attack_bonus"):
        ctx.modify_two_handed_attack_bonus(
            amount=ability_level(ctx.source, "Two-Handed Specialist")
        )
        return

    states = _ensure_states(ctx.source)
    states["two_handed_specialist"] = {
        "active": True,
        "attack_bonus_per_skill_level": ability_level(
            ctx.source,
            "Two-Handed Specialist",
        ),
        "requires_two_handed_weapon": True,
        "source_ability": "Two-Handed Specialist",
    }

# Berserker

build_job(
    "Berserker",
    [
        # Level 1
        {
            "name": "Furious Strike",
            "type": "skill",
            "cost": 10,
            "cost_pool": "hp",
            "duration": "1 Attack",
            "target": "enemy",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "Your next attack inflicts additional damage equal to your Berserker level "
                "plus the level of this skill. The bonus damage is wasted if the attack misses."
            ),
            "effects": modify_next_attack(_furious_strike_modifier),
        },
        {
            "grant": "Growl",
            "required_level": 1,
        },
        {
            "name": "Headbutt",
            "type": "skill",
            "cost": 10,
            "cost_pool": "hp",
            "duration": "1 Attack",
            "target": "enemy",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "The Berserker smashes their head into the enemy. This is a Strength + "
                "Brawling + Headbutt attack. If it hits, the target must roll Constitution "
                "against the Berserker's Headbutt or be stunned for 1 round."
            ),
            "effects": apply_state(
                "headbutt_ready",
                value_fn=lambda source: {
                    "active": True,
                    "attack_stat": "strength",
                    "attack_skill": "brawling",
                    "bonus_from_skill": ability_level(source, "Headbutt"),
                    "on_hit_save": {
                        "target_stat": "constitution",
                        "dc_source_ability": "Headbutt",
                        "on_fail_state": "stunned",
                        "duration_rounds": 1,
                    },
                    "source_ability": "Headbutt",
                },
            ),
        },
        {
            "name": "Power From Pain",
            "type": "passive",
            "target": "self",
            "required_level": 1,
            "scales_with_level": False,
            "description": (
                "Whenever the Berserker loses 10 or more hit points, they gain +1 to all "
                "strength-based rolls for the next 5 minutes. This skill has no levels."
            ),
            "duration": "Passive Constant",
            "effects": on_event(
                event_name="hp_lost",
                effect=apply_state(
                    "power_from_pain_active",
                    value_fn=lambda source: {
                        "duration_minutes": 5,
                        "strength_roll_bonus": 1,
                        "source_ability": "Power From Pain",
                    },
                ),
                condition=lambda event_ctx: getattr(event_ctx, "amount", 0) >= 10,
            ),
        },
        {
            "grant": "Rage",
            "required_level": 1,
        },

        # Level 5
        {
            "name": "Reckless Charge",
            "type": "skill",
            "cost": 10,
            "cost_pool": "stamina",
            "duration": "1 Attack",
            "target": "self",
            "required_level": 5,
            "scales_with_level": True,
            "description": (
                "The Berserker doubles their running speed for the turn, ignores situational terrain "
                "modifiers for the next action, and may immediately make a melee attack after moving. "
                "That attack gains an increase equal to Reckless Charge level. The Berserker must move "
                "in order to use this skill."
            ),
            "effects": apply_state(
                "reckless_charge_active",
                value_fn=lambda source: {
                    "duration_turns": 1,
                    "double_running_speed": True,
                    "ignore_situational_terrain_modifiers": True,
                    "requires_movement": True,
                    "immediate_melee_attack_after_moving": True,
                    "attack_bonus": ability_level(source, "Reckless Charge"),
                    "source_ability": "Reckless Charge",
                },
            ),
        },
        {
            "grant": "Toughness",
            "required_level": 5,
        },
        {
            "name": "Wide Swing",
            "type": "skill",
            "cost": 10,
            "cost_pool": "hp",
            "duration": "1 Attack",
            "target": "adjacent_enemies",
            "required_level": 5,
            "scales_with_level": False,
            "description": (
                "The Berserker's next melee attack targets all adjacent enemies. Roll once and apply "
                "the result to all foes struck. The Berserker loses 10 HP per adjacent foe when using "
                "this skill. Wide Swing adds +1 damage and has no levels."
            ),
            "effects": modify_next_attack(_wide_swing_modifier),
        },

        # Level 10
        {
            "name": "Build Up",
            "type": "skill",
            "cost": 20,
            "cost_pool": "moxie",
            "duration": "1 Minute or Until Used",
            "target": "self",
            "required_level": 10,
            "scales_with_level": True,
            "description": (
                "For each action spent building up, the Berserker's next attack gains +10. "
                "The Berserker may spend a number of actions equal to this skill's level. "
                "The effect lasts 1 minute or until used."
            ),
            "effects": apply_state(
                "build_up_active",
                value_fn=lambda source: {
                    "active": True,
                    "max_actions": ability_level(source, "Build Up"),
                    "attack_bonus_per_action_spent": 10,
                    "expires_on_attack": True,
                    "duration_minutes": 1,
                    "source_ability": "Build Up",
                },
            ),
        },
        {
            "name": "Tough as Leather",
            "type": "passive",
            "target": "self",
            "required_level": 10,
            "scales_with_level": False,
            "description": (
                "The Berserker's body hardens with conditioning. Increase Endurance by "
                "their Berserker level."
            ),
            "duration": "Passive Constant",
            "effects": scaled_derived_buff(
                scale_fn=lambda source: progression_level(source, "adventure", "Berserker"),
                stat="endurance",
            ),
        },

        # Level 15
        {
            "grant": "Fast as Death",
            "required_level": 15,
        },
        {
            "name": "Two-Handed Specialist",
            "type": "passive",
            "target": "self",
            "required_level": 15,
            "scales_with_level": True,
            "description": (
                "While using a two-handed weapon, the Berserker gains +1 to attack rolls "
                "for every level of this skill."
            ),
            "duration": "Passive Constant",
            "effects": passive_modifier(_two_handed_specialist_modifier),
        },

        # Level 20
        {
            "name": "Iron Skin",
            "type": "skill",
            "cost": 50,
            "cost_pool": "stamina",
            "duration": "1 Minute",
            "target": "self",
            "required_level": 20,
            "scales_with_level": True,
            "description": (
                "The Berserker hardens their muscles like armor, gaining a buff to Armor "
                "equal to the level of this skill."
            ),
            "effects": apply_state(
                "iron_skin_active",
                value_fn=lambda source: {
                    "duration_minutes": 1,
                    "armor_bonus": ability_level(source, "Iron Skin"),
                    "source_ability": "Iron Skin",
                },
            ),
        },
        {
            "name": "The Bigger They Are...",
            "type": "skill",
            "cost": 25,
            "cost_pool": "moxie",
            "duration": "1 Attack",
            "target": "enemy",
            "required_level": 20,
            "scales_with_level": False,
            "description": (
                "The Berserker's next attack ignores armor equal to twice their Berserker level. "
                "This skill may only be used against a foe of equal or larger size. This skill has no levels."
            ),
            "effects": modify_next_attack(_bigger_they_are_modifier),
        },

        # Level 25
        {
            "name": "All You Need is Kill",
            "type": "skill",
            "cost": 25,
            "cost_pool": "moxie",
            "duration": "Instant",
            "target": "self",
            "required_level": 25,
            "scales_with_level": True,
            "description": (
                "Whenever the Berserker knocks a foe unconscious or dead, they may pay this skill's cost "
                "to instantly regain hit points equal to the level of this skill."
            ),
            "effects": apply_state(
                "all_you_need_is_kill",
                value_fn=lambda source: {
                    "active": True,
                    "trigger": "target_defeated_by_source",
                    "cost_moxie": 25,
                    "heal_hp_amount": ability_level(source, "All You Need is Kill"),
                    "source_ability": "All You Need is Kill",
                },
            ),
        },
        {
            "name": "Two-Handed Titan",
            "type": "passive",
            "target": "self",
            "required_level": 25,
            "scales_with_level": False,
            "description": (
                "The Berserker may wield a two-handed weapon as though it were one-handed. "
                "They also reduce the stamina damage multiplier of any weapon they wield by 2 multiples, "
                "to a minimum of ×1. This skill has no levels."
            ),
            "duration": "Passive Constant",
            "effects": apply_state(
                "two_handed_titan",
                value_fn=lambda source: {
                    "active": True,
                    "can_wield_two_handed_as_one_handed": True,
                    "stamina_multiplier_reduction": 2,
                    "minimum_stamina_multiplier": 1,
                    "source_ability": "Two-Handed Titan",
                },
            ),
        },
    ],
    source_type="adventure",
)