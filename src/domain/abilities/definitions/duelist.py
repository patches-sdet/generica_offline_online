from domain.abilities import ability_level, progression_level
from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    aura,
    modify_next_attack,
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


# ---------------------------------------------------------------------------
# Passive / runtime helpers
# ---------------------------------------------------------------------------

def _weapon_specialist_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["weapon_specialist"] = {
        "active": True,
        "bonus": ability_level(ctx.source, "Weapon Specialist"),
        "applies_to": "highest_weapon_skill",
        "choose_if_tied": True,
        "source_ability": "Weapon Specialist",
    }


def _parry_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["parry_active"] = {
        "active": True,
        "agility_bonus": ability_level(ctx.source, "Parry"),
        "condition": "aware_of_melee_attack_and_specialized_weapon_drawn",
        "source_ability": "Parry",
    }


def _riposte_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["riposte_active"] = {
        "active": True,
        "trigger": "enemy_roll_1_to_10_on_melee_attack_against_you",
        "free_attack": True,
        "once_per_turn": True,
        "requires_parry_context": True,
        "source_ability": "Riposte",
    }


# ---------------------------------------------------------------------------
# Attack helpers
# ---------------------------------------------------------------------------

def _fancy_flourish_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "attack_stat_options", ("dexterity", "charisma"))
    _set_attack_attr(attack, "target_stat", "willpower")
    _set_attack_attr(attack, "damage_pool", "moxie")
    _set_attack_attr(attack, "damage_bonus", ability_level(ctx.source, "Fancy Flourish"))
    _set_attack_attr(attack, "damage_reduced_by", "cool")
    _set_attack_attr(attack, "nonlethal", True)
    _set_attack_attr(attack, "fancy_flourish", True)


def _disarm_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "attack_stat_options", ("dexterity", "strength"))
    _set_attack_attr(attack, "requires_melee_range", True)
    _set_attack_attr(attack, "target_damage_pool", "stamina")
    _set_attack_attr(attack, "damage_reduced_by", "endurance")
    _set_attack_attr(attack, "forces_drop_weapon_check", True)
    _set_attack_attr(attack, "drop_weapon_resist_stat", "dexterity")
    _set_attack_attr(attack, "drop_weapon_dc_bonus", ability_level(ctx.source, "Disarm"))
    _set_attack_attr(attack, "disarm", True)


build_job(
    "Duelist",
    [
        # Level 1
        {
            "name": "Challenge",
            "type": "skill",
            "cost": 5,
            "cost_pool": "moxie",
            "target": "enemy",
            "required_level": 1,
            "scales_with_level": False,
            "is_spell": False,
            "description": (
                "Calls out a target to fight you. On success, they become Challenged, taking a penalty "
                "to all rolls equal to your Duelist level unless the roll involves maneuvering against you, "
                "attacking you, or defending against you. Challenging a new target removes the prior one."
            ),
            "duration": "5 Minutes",
            "effects": apply_state(
                "challenged",
                value_fn=lambda source: {
                    "challenger": source,
                    "penalty": progression_level(source, "adventure", "Duelist"),
                    "duration_minutes": 5,
                    "ignore_penalty_when": {
                        "maneuvering_against_challenger": True,
                        "attacking_challenger": True,
                        "defending_against_challenger": True,
                    },
                    "single_target_per_duelist": True,
                    "source_ability": "Challenge",
                },
            ),
        },
        {
            "name": "Dazzling Entrance",
            "type": "skill",
            "cost": 10,
            "cost_pool": "moxie",
            "target": "self",
            "required_level": 1,
            "scales_with_level": True,
            "is_spell": False,
            "description": (
                "Before revealing yourself, make a dramatic appearance. Buffs your Charisma and Cool "
                "by your Duelist level for a number of turns equal to this skill's level."
            ),
            "duration": "1 Turn per Level",
            "effects": apply_state(
                "dazzling_entrance_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_turns": ability_level(source, "Dazzling Entrance"),
                    "charisma_bonus": progression_level(source, "adventure", "Duelist"),
                    "cool_bonus": progression_level(source, "adventure", "Duelist"),
                    "source_ability": "Dazzling Entrance",
                },
            ),
        },
        {
            "name": "Fancy Flourish",
            "type": "skill",
            "cost": 5,
            "cost_pool": "stamina",
            "target": "enemy",
            "required_level": 1,
            "scales_with_level": True,
            "is_spell": False,
            "description": (
                "Unleash a flashy set of moves that will not physically injure your foe. "
                "Roll Dexterity or Charisma plus Fancy Flourish against the target's Willpower, "
                "inflicting Moxie damage reduced by Cool."
            ),
            "duration": "1 Attack",
            "effects": modify_next_attack(_fancy_flourish_modifier),
        },
        {
            "name": "Guard Stance",
            "type": "skill",
            "cost": 10,
            "cost_pool": "stamina",
            "target": "self",
            "required_level": 1,
            "scales_with_level": True,
            "is_spell": False,
            "description": (
                "Enter a defensive stance. Gain a bonus to Agility, dodge skill, and Armor by a chosen value "
                "up to Guard Stance level, while Strength and Dexterity are lowered by the same value. "
                "This does not change pools. Only one stance may be active at a time."
            ),
            "duration": "Until Dropped or End of Fight",
            "effects": aura(
                apply_state(
                    "guard_stance_active",
                    value_fn=lambda source: {
                        "active": True,
                        "chosen_value_max": ability_level(source, "Guard Stance"),
                        "buffs": {
                            "agility": "chosen_value",
                            "dodge": "chosen_value",
                            "armor": "chosen_value",
                        },
                        "penalties": {
                            "strength": "chosen_value",
                            "dexterity": "chosen_value",
                        },
                        "does_not_modify_pools": True,
                        "source_ability": "Guard Stance",
                    },
                ),
                aura_id="duelist_stance",
            ),
        },
        {
            "name": "Weapon Specialist",
            "type": "passive",
            "target": "self",
            "required_level": 1,
            "scales_with_level": True,
            "is_spell": False,
            "description": (
                "Enhances your highest weapon skill. If two or more weapon skills are tied for highest, "
                "you may choose which one to specialize in. The bonus equals Weapon Specialist level."
            ),
            "duration": "Passive Constant",
            "effects": passive_modifier(_weapon_specialist_modifier),
        },

        # Level 5
        {
            "name": "Parry",
            "type": "passive",
            "target": "self",
            "required_level": 5,
            "scales_with_level": True,
            "is_spell": False,
            "description": (
                "While you have your specialized weapon drawn, you may parry melee attacks you are aware of. "
                "Parry increases your Agility, but only against melee attacks."
            ),
            "duration": "Passive Constant",
            "effects": passive_modifier(_parry_modifier),
        },
        {
            "name": "Swashbuckler's Spirit",
            "type": "passive",
            "target": "self",
            "required_level": 5,
            "scales_with_level": False,
            "is_spell": False,
            "description": (
                "Your Cool is increased by your Duelist level."
            ),
            "duration": "Passive Constant",
            "effects": scaled_derived_buff(
                scale_fn=lambda source: progression_level(source, "adventure", "Duelist"),
                stat="cool",
            ),
        },
        {
            "name": "Swinger",
            "type": "skill",
            "cost": 10,
            "cost_pool": "stamina",
            "target": "self",
            "required_level": 5,
            "scales_with_level": True,
            "is_spell": False,
            "description": (
                "Adds this skill's level to Agility rolls when swinging from ropes, chandeliers, "
                "and similar feats, and to Strength rolls when climbing."
            ),
            "duration": "1 Minute per Level",
            "effects": apply_state(
                "swinger_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_minutes": ability_level(source, "Swinger"),
                    "agility_bonus_for_swinging": ability_level(source, "Swinger"),
                    "strength_bonus_for_climbing": ability_level(source, "Swinger"),
                    "source_ability": "Swinger",
                },
            ),
        },

        # Level 10
        {
            "name": "Disarm",
            "type": "skill",
            "cost": 20,
            "cost_pool": "stamina",
            "target": "enemy",
            "required_level": 10,
            "scales_with_level": True,
            "is_spell": False,
            "description": (
                "A sweeping melee attack that can disarm a foe. If it connects, the target uses Endurance "
                "for defense, takes Stamina instead of HP damage, and must roll Dexterity against your "
                "margin of success plus Disarm level or drop their weapon."
            ),
            "duration": "1 Attack",
            "effects": modify_next_attack(_disarm_modifier),
        },
        {
            "name": "Riposte",
            "type": "passive",
            "target": "self",
            "required_level": 10,
            "scales_with_level": False,
            "is_spell": False,
            "description": (
                "Whenever you successfully parry an attack, you may have a chance to immediately counterattack. "
                "This may only happen once per turn."
            ),
            "duration": "Passive Constant",
            "effects": passive_modifier(_riposte_modifier),
        },

        # Level 15
        {
            "name": "Offensive Stance",
            "type": "skill",
            "cost": 30,
            "cost_pool": "stamina",
            "target": "self",
            "required_level": 15,
            "scales_with_level": True,
            "is_spell": False,
            "description": (
                "Enter an offensive stance that boosts Strength and Dexterity by a chosen value up to "
                "Offensive Stance level, while lowering Agility and dodge skill by the same amount. "
                "This does not change pools. Only one stance may be active at a time."
            ),
            "duration": "Until Dropped or End of Fight",
            "effects": aura(
                apply_state(
                    "offensive_stance_active",
                    value_fn=lambda source: {
                        "active": True,
                        "chosen_value_max": ability_level(source, "Offensive Stance"),
                        "buffs": {
                            "strength": "chosen_value",
                            "dexterity": "chosen_value",
                        },
                        "penalties": {
                            "agility": "chosen_value",
                            "dodge": "chosen_value",
                        },
                        "does_not_modify_pools": True,
                        "source_ability": "Offensive Stance",
                    },
                ),
                aura_id="duelist_stance",
            ),
        },
        {
            "grant": "Pommel Strike",
            "required_level": 15,
        },

        # Level 20
        {
            "name": "Mobility Stance",
            "type": "skill",
            "cost": 40,
            "cost_pool": "stamina",
            "target": "self",
            "required_level": 20,
            "scales_with_level": True,
            "is_spell": False,
            "description": (
                "Enter a mobility stance. Gain a bonus to Agility and initiative equal to up to three times "
                "Mobility Stance level, while lowering Dexterity, Strength, and dodge skill by the chosen value. "
                "Only one stance may be active at a time."
            ),
            "duration": "Until Dropped or End of Fight",
            "effects": aura(
                apply_state(
                    "mobility_stance_active",
                    value_fn=lambda source: {
                        "active": True,
                        "chosen_value_max": ability_level(source, "Mobility Stance") * 3,
                        "buffs": {
                            "agility": "chosen_value",
                            "initiative": "chosen_value",
                        },
                        "penalties": {
                            "dexterity": "chosen_value",
                            "strength": "chosen_value",
                            "dodge": "chosen_value",
                        },
                        "does_not_modify_pools": True,
                        "source_ability": "Mobility Stance",
                    },
                ),
                aura_id="duelist_stance",
            ),
        },
        {
            "grant": "Staredown",
            "required_level": 20,
        },

        # Level 25
        {
            "name": "A Leaf on the Wind",
            "type": "skill",
            "cost": 50,
            "cost_pool": "stamina",
            "target": "self",
            "required_level": 25,
            "scales_with_level": False,
            "is_spell": False,
            "description": (
                "When struck, you may instantly reduce the opponent's margin of success by your Duelist level. "
                "This does not trigger Parry or Riposte, even if it turns the attack into a miss. "
                "This skill has no levels."
            ),
            "duration": "Instant",
            "effects": apply_state(
                "leaf_on_the_wind_ready",
                value_fn=lambda source: {
                    "active": True,
                    "trigger": "when_hit",
                    "reduce_margin_of_success": progression_level(source, "adventure", "Duelist"),
                    "does_not_trigger_parry": True,
                    "does_not_trigger_riposte": True,
                    "source_ability": "A Leaf on the Wind",
                },
            ),
        },
        {
            "name": "You're Mine!",
            "type": "skill",
            "cost": 50,
            "cost_pool": "moxie",
            "target": "enemy",
            "required_level": 25,
            "scales_with_level": False,
            "is_spell": False,
            "description": (
                "You focus everything on one foe. Against that target, you gain an increase equal to double "
                "your Duelist level on all rolls. All other foes gain an increase equal to your Duelist level "
                "on their rolls against you. This skill has no levels."
            ),
            "duration": "Until Dropped or End of Fight",
            "effects": apply_state(
                "youre_mine_active",
                value_fn=lambda source: {
                    "active": True,
                    "focus_target_required": True,
                    "bonus_against_focus_target": progression_level(source, "adventure", "Duelist") * 2,
                    "bonus_to_other_foes_against_you": progression_level(source, "adventure", "Duelist"),
                    "source_ability": "You're Mine!",
                },
            ),
        },
    ],
    source_type="adventure",
)