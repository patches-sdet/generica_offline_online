from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    modify_next_attack,
    on_event,
    passive_modifier,
    scaled_derived_buff,
    scaled_stat_buff,
)
from domain.effects.base import Effect, EffectContext
from domain.effects.stat_effects import DerivedStatBonus


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _berserker_level(character) -> int:
    return character.get_progression_level("adventure", "Berserker", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


def _set_attack_attr(attack, key: str, value) -> None:
    setattr(attack, key, value)


# Attack modifier helpers

def _furious_strike_modifier(ctx, attack) -> None:
    _set_attack_attr(
        attack,
        "bonus_damage",
        _berserker_level(ctx.source) + _ability_level(ctx.source, "Furious Strike"),
    )
    _set_attack_attr(attack, "furious_strike", True)


def _reckless_charge_modifier(ctx, attack) -> None:
    _set_attack_attr(
        attack,
        "attack_bonus",
        _ability_level(ctx.source, "Reckless Charge"),
    )
    _set_attack_attr(attack, "requires_movement", True)
    _set_attack_attr(attack, "granted_after_charge", True)


def _wide_swing_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "targets_all_adjacent_enemies", True)
    _set_attack_attr(attack, "single_roll_for_all_targets", True)
    _set_attack_attr(attack, "bonus_damage", 1)
    _set_attack_attr(
        attack,
        "cost_hp_per_adjacent_foe",
        10,
    )
    _set_attack_attr(
        attack,
        "experience_difficulty_source",
        "highest_agility_among_successfully_struck_foes",
    )


def _bigger_they_are_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "ignore_armor", _berserker_level(ctx.source) * 2)
    _set_attack_attr(attack, "minimum_target_size", "self_or_larger")
    _set_attack_attr(attack, "the_bigger_they_are", True)


# Passive / event helpers

def _power_from_pain_buff(ctx: EffectContext) -> list[Effect]:
    return [
        apply_state(
            "power_from_pain_active",
            value_fn=lambda source: {
                "duration_minutes": 5,
                "strength_roll_bonus": 1,
                "source_ability": "Power From Pain",
            },
        )
    ]


def _two_handed_specialist_modifier(ctx) -> None:
    """
    Runtime-facing passive hook for two-handed weapon attacks.
    """
    if hasattr(ctx, "modify_two_handed_attack_bonus"):
        ctx.modify_two_handed_attack_bonus(
            amount=_ability_level(ctx.source, "Two-Handed Specialist")
        )
        return

    states = _ensure_states(ctx.source)
    states["two_handed_specialist"] = {
        "active": True,
        "attack_bonus_per_skill_level": _ability_level(ctx.source, "Two-Handed Specialist"),
        "requires_two_handed_weapon": True,
        "source_ability": "Two-Handed Specialist",
    }

class HeadbuttEffect(Effect):
    """
    Runtime-facing placeholder for the Berserker's headbutt attack.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["headbutt_ready"] = {
            "active": True,
            "attack_stat": "strength",
            "attack_skill": "brawling",
            "bonus_from_skill": _ability_level(context.source, "Headbutt"),
            "on_hit_save": {
                "target_stat": "constitution",
                "dc_source_ability": "Headbutt",
                "on_fail_state": "stunned",
                "duration_rounds": 1,
            },
            "source_ability": "Headbutt",
        }

class BuildUpEffect(Effect):
    """
    Stores the charge-up state for the next attack.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["build_up_active"] = {
            "active": True,
            "max_actions": _ability_level(context.source, "Build Up"),
            "attack_bonus_per_action_spent": 10,
            "expires_on_attack": True,
            "duration_minutes": 1,
            "source_ability": "Build Up",
        }

class AllYouNeedIsKillEffect(Effect):
    """
    Event-facing placeholder for kill-triggered self-healing.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["all_you_need_is_kill"] = {
            "active": True,
            "trigger": "target_defeated_by_source",
            "cost_moxie": 25,
            "heal_hp_amount": _ability_level(context.source, "All You Need is Kill"),
            "source_ability": "All You Need is Kill",
        }


class TwoHandedTitanEffect(Effect):
    """
    Passive weapon-handling override placeholder.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["two_handed_titan"] = {
            "active": True,
            "can_wield_two_handed_as_one_handed": True,
            "stamina_multiplier_reduction": 2,
            "minimum_stamina_multiplier": 1,
            "source_ability": "Two-Handed Titan",
        }


# Berserker

build_job("Berserker", [

    # Level 1

    {
        "name": "Furious Strike",
        "cost": 10,
        "cost_pool": "hp",
        "description": (
            "Your next attack inflicts additional damage equal to your Berserker level "
            "plus the level of this skill. The bonus damage is wasted if the attack misses."
        ),
        "duration": "1 Attack",
        "effects": modify_next_attack(_furious_strike_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    {"grant": "Growl", "required_level": 1},

    {
        "name": "Headbutt",
        "cost": 10,
        "cost_pool": "hp",
        "description": (
            "The Berserker smashes their head into the enemy. This is a strength + brawling "
            "+ Headbutt attack. If it hits, the target must roll Constitution against the "
            "Berserker's Headbutt or be stunned for 1 round."
        ),
        "duration": "1 Attack",
        "effects": HeadbuttEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Power From Pain",
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
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {"grant": "Rage", "required_level": 1},

    # Level 5

        {
        "name": "Reckless Charge",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "The Berserker doubles their running speed for the turn, ignores situational terrain "
            "modifiers for the next action, and may immediately make a melee attack after moving. "
            "That attack gains an increase equal to Reckless Charge level. The Berserker must move "
            "in order to use this skill."
        ),
        "duration": "1 Attack",
        "effects": apply_state(
            "reckless_charge_active",
            value_fn=lambda source: {
                "duration_turns": 1,
                "double_running_speed": True,
                "ignore_situational_terrain_modifiers": True,
                "requires_movement": True,
                "immediate_melee_attack_after_moving": True,
                "attack_bonus": _ability_level(source, "Reckless Charge"),
                "source_ability": "Reckless Charge",
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {"grant": "Toughness", "required_level": 5},

    {
        "name": "Wide Swing",
        "cost": 10,
        "cost_pool": "hp",
        "description": (
            "The Berserker's next melee attack targets all adjacent enemies. Roll once and apply "
            "the result to all foes struck. The Berserker loses 10 HP per adjacent foe when using "
            "this skill. Wide Swing adds +1 damage and has no levels."
        ),
        "duration": "1 Attack",
        "effects": modify_next_attack(_wide_swing_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": False,
        "target": "adjacent_enemies",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Build Up",
        "cost": 20,
        "cost_pool": "moxie",
        "description": (
            "For each action spent building up, the Berserker's next attack gains +10. "
            "The Berserker may spend a number of actions equal to this skill's level. "
            "The effect lasts 1 minute or until used."
        ),
        "duration": "1 Minute or Until Used",
        "effects": BuildUpEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 10,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Tough as Leather",
        "description": (
            "The Berserker's body hardens with conditioning. Increase Endurance by "
            "their Berserker level."
        ),
        "duration": "Passive Constant",
        "effects": scaled_derived_buff(
            scale_fn=lambda c: c.get_progression_level("adventure", "Berserker", 0),
            stat="endurance",
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 10,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Level 15

    {"grant": "Fast as Death", "required_level": 15},

    {
        "name": "Two-Handed Specialist",
        "description": (
            "While using a two-handed weapon, the Berserker gains +1 to attack rolls "
            "for every level of this skill."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_two_handed_specialist_modifier),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 15,
        "scales_with_level": True,
        "target": "self",
        "type": "passive",
    },

    # Level 20

    {
        "name": "Iron Skin",
        "cost": 50,
        "cost_pool": "stamina",
        "description": (
            "The Berserker hardens their muscles like armor, gaining a buff to Armor "
            "equal to the level of this skill."
        ),
        "duration": "1 Minute",
        "effects": apply_state(
            "iron_skin_active",
            value_fn=lambda source: {
                "duration_minutes": 1,
                "armor_bonus": _ability_level(source, "Iron Skin"),
                "source_ability": "Iron Skin",
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 20,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "The Bigger They Are...",
        "cost": 25,
        "cost_pool": "moxie",
        "description": (
            "The Berserker's next attack ignores armor equal to twice their Berserker level. "
            "This skill may only be used against a foe of equal or larger size. This skill has no levels."
        ),
        "duration": "1 Attack",
        "effects": modify_next_attack(_bigger_they_are_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 20,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    # Level 25

    {
        "name": "All You Need is Kill",
        "cost": 25,
        "cost_pool": "moxie",
        "description": (
            "Whenever the Berserker knocks a foe unconscious or dead, they may pay this skill's cost "
            "to instantly regain hit points equal to the level of this skill."
        ),
        "duration": "Instant",
        "effects": AllYouNeedIsKillEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Two-Handed Titan",
        "description": (
            "The Berserker may wield a two-handed weapon as though it were one-handed. "
            "They also reduce the stamina damage multiplier of any weapon they wield by 2 multiples, "
            "to a minimum of ×1. This skill has no levels."
        ),
        "duration": "Passive Constant",
        "effects": TwoHandedTitanEffect(),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

], source_type="adventure")