from domain.abilities import ability_level, progression_level
from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    modify_next_attack,
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

def _holy_smite_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "bonus_damage", ability_level(ctx.source, "Holy Smite"))
    _set_attack_attr(attack, "damage_type", "light")
    _set_attack_attr(attack, "holy_smite", True)

# Cleric

build_job(
    "Cleric",
    [
        # Level 1
        {
            "name": "Blessing",
            "type": "skill",
            "cost": 1,
            "cost_pool": "fortune",
            "target": "ally",
            "required_level": 1,
            "scales_with_level": False,
            "description": (
                "The Cleric spends fortune to increase a single chosen attribute of an ally by an equal amount. "
                "That fortune remains committed until the spell is cancelled. A being can only be under one Blessing "
                "at a time, and the Cleric can only maintain one Blessing at a time. This skill is a spell."
            ),
            "duration": "Until Cancelled or Dispelled",
            "is_spell": True,
            "effects": apply_state(
                "cleric_blessing_active",
                value_fn=lambda source: {
                    "active": True,
                    "chosen_stat": None,
                    "selection_required": True,
                    "invested_fortune": "from_spent_amount_min_1",
                    "duration": "until_cancelled_or_dispelled",
                    "one_active_blessing_from_source": True,
                    "target_limit_rule": "single_blessing_per_target",
                    "held_fortune_committed": True,
                    "applies_state_to_targets": "blessing_received",
                    "source_ability": "Blessing",
                },
            ),
        },
        {
            "name": "Faith",
            "type": "passive",
            "target": "self",
            "required_level": 1,
            "scales_with_level": False,
            "description": "Your Fate is increased by your Cleric level.",
            "duration": "Passive Constant",
            "effects": scaled_derived_buff(
                stat="fate",
                scale_fn=lambda source: progression_level(source, "adventure", "Cleric"),
            ),
        },
        {
            "name": "Godspell",
            "type": "skill",
            "target": "self",
            "required_level": 1,
            "scales_with_level": False,
            "description": (
                "The Cleric gains access to the unique Godspell of their chosen deity. "
                "This is a structured placeholder until deity selection and godspell binding are implemented."
            ),
            "duration": "Varies",
            "effects": apply_state(
                "godspell_access",
                value_fn=lambda source: {
                    "active": True,
                    "deity": getattr(source, "states", {}).get("godspell_access", {}).get("deity"),
                    "chosen_godspell": getattr(source, "states", {}).get("godspell_access", {}).get("chosen_godspell"),
                    "selection_required": True,
                    "source_ability": "Godspell",
                },
            ),
        },
        {
            "name": "Holy Smite",
            "type": "skill",
            "cost": 10,
            "cost_pool": "fortune",
            "target": "enemy",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "Holy Smite increases the Cleric's next melee attack damage by 1 per level of this skill. "
                "This skill is a spell."
            ),
            "duration": "1 Minute per Level",
            "is_spell": True,
            "effects": modify_next_attack(_holy_smite_modifier),
        },
        {
            "grant": "Lesser Healing",
            "required_level": 1,
        },
        {
            "name": "Shield of Divinity",
            "type": "skill",
            "cost": 10,
            "cost_pool": "sanity",
            "target": "ally",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "The Cleric buffs a single target's Armor by an amount equal to the level of this skill. "
                "The Cleric can only apply this buff to one target at a time. This skill is a spell."
            ),
            "duration": "5 Minutes",
            "is_spell": True,
            "effects": apply_state(
                "shield_of_divinity_active",
                value_fn=lambda source: {
                    "active": True,
                    "armor_bonus": ability_level(source, "Shield of Divinity"),
                    "duration_minutes": 5,
                    "one_active_target_only": True,
                    "applies_state_to_targets": "shield_of_divinity_received",
                    "source_ability": "Shield of Divinity",
                },
            ),
        },

        # Level 5
        {
            "name": "Curative",
            "type": "skill",
            "cost": 15,
            "cost_pool": "sanity",
            "target": "ally",
            "required_level": 5,
            "scales_with_level": False,
            "description": (
                "Instantly removes one of the following conditions from the target: "
                "Bleeding, Diseased, Drunk, Gassy, Hungover, Nauseated, Numb, or Poisoned. "
                "This skill has no levels. This skill is a spell."
            ),
            "duration": "Instant",
            "is_spell": True,
            "effects": apply_state(
                "curative_applied",
                value_fn=lambda source: {
                    "selection_required": True,
                    "removable_conditions": {
                        "bleeding",
                        "diseased",
                        "drunk",
                        "gassy",
                        "hungover",
                        "nauseated",
                        "numb",
                        "poisoned",
                    },
                    "removes_selected_condition_from_target": True,
                    "source_ability": "Curative",
                },
            ),
        },
        {
            "name": "Party Heal",
            "type": "skill",
            "cost": 20,
            "cost_pool": "sanity",
            "target": "party",
            "required_level": 5,
            "scales_with_level": True,
            "description": (
                "Instantly heals all living party members within one hundred feet of the Cleric. "
                "The amount healed is 10 plus Party Heal level divided by 10. Undead party members "
                "take light-based damage instead, bypassing defenses and automatically hitting. "
                "This skill is a spell."
            ),
            "duration": "Instant",
            "is_spell": True,
            "effects": apply_state(
                "party_heal_cast",
                value_fn=lambda source: {
                    "active": True,
                    "radius_feet": 100,
                    "heal_hp": 10 + (ability_level(source, "Party Heal") // 10),
                    "damage_undead_instead": True,
                    "damage_bypasses_defenses": True,
                    "auto_hits": True,
                    "source_ability": "Party Heal",
                },
            ),
        },
        {
            "name": "Pray to God",
            "type": "skill",
            "cost": 20,
            "cost_pool": "fortune",
            "target": "self",
            "required_level": 5,
            "scales_with_level": False,
            "description": (
                "The Cleric enters mental contact with their deity for up to ten minutes. "
                "The deity can usually answer with hints and riddles within their area of influence. "
                "This skill has no levels. This skill is a spell."
            ),
            "duration": "10 Minutes",
            "is_spell": True,
            "effects": apply_state(
                "pray_to_god_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_minutes": 10,
                    "topic": None,
                    "selection_required": True,
                    "communication_mode": "mental_contact",
                    "response_style": "hints_and_riddles",
                    "limited_by_deity_domain": True,
                    "source_ability": "Pray to God",
                },
            ),
        },

        # Level 10
        {
            "name": "Divine Transit",
            "type": "skill",
            "cost": 10,
            "cost_pool": "sanity",
            "target": "group",
            "required_level": 10,
            "scales_with_level": False,
            "description": (
                "The Cleric petitions their deity to extract affected people from a dungeon, building, "
                "or alien plane of existence. Wards and similar countermeasures can prevent this. "
                "This skill has no levels. This skill is a spell."
            ),
            "duration": "Instant",
            "is_spell": True,
            "effects": apply_state(
                "divine_transit_cast",
                value_fn=lambda source: {
                    "active": True,
                    "blocked_by_wards": True,
                    "destination_rule": "entry_point_or_deity_choice",
                    "source_ability": "Divine Transit",
                },
            ),
        },
        {
            "name": "Holy Bolt",
            "type": "skill",
            "cost": 20,
            "cost_pool": "sanity",
            "target": "enemy",
            "required_level": 10,
            "scales_with_level": False,
            "description": (
                "The Cleric calls down a holy bolt upon a foe, using Wisdom plus Holy Bolt "
                "against the target's Luck. It normally inflicts Fortune damage reduced by Fate, "
                "but against undead or dark foes it may instead inflict HP damage. This skill is a spell."
            ),
            "duration": "1 Attack",
            "is_spell": True,
            "effects": apply_state(
                "holy_bolt_ready",
                value_fn=lambda source: {
                    "active": True,
                    "attack_stat": "wisdom",
                    "skill_name": "Holy Bolt",
                    "target_stat": "luck",
                    "default_damage_pool": "fortune",
                    "reduced_by": "fate",
                    "can_convert_to_hp_against_undead_or_dark": True,
                    "damage_type": "light",
                    "source_ability": "Holy Bolt",
                },
            ),
        },

        # Level 15
        {
            "name": "Back You Fiend!",
            "type": "skill",
            "cost": 30,
            "cost_pool": "sanity",
            "target": "undead_or_dark",
            "required_level": 15,
            "scales_with_level": False,
            "description": (
                "The Cleric becomes a beacon of holy light. Any undead or dark-aligned entity "
                "that comes within fifty feet takes damage equal to the Cleric's level, bypassing "
                "all defenses and automatically hitting. This skill has no levels. This skill is a spell."
            ),
            "duration": "Until Cancelled",
            "is_spell": True,
            "effects": apply_state(
                "back_you_fiend_active",
                value_fn=lambda source: {
                    "active": True,
                    "radius_feet": 50,
                    "duration": "until_cancelled",
                    "targets": {"undead", "dark_aligned"},
                    "damage_pool": "hp",
                    "damage_amount": progression_level(source, "adventure", "Cleric"),
                    "damage_type": "light",
                    "bypasses_defenses": True,
                    "auto_hits": True,
                    "cost_sanity_per_minute": 30,
                    "source_ability": "Back You Fiend!",
                },
            ),
        },
        {
            "name": "Greater Healing",
            "type": "skill",
            "cost": 25,
            "cost_pool": "sanity",
            "target": "ally_or_enemy",
            "required_level": 15,
            "scales_with_level": True,
            "description": (
                "Instantly heals a living target within one hundred feet of the Cleric, restoring HP equal "
                "to the Cleric's Wisdom plus Greater Healing level. Against undead or negative-natured targets, "
                "it deals light-based damage instead, bypassing defenses and automatically hitting. This skill is a spell."
            ),
            "duration": "1 Action",
            "is_spell": True,
            "effects": apply_state(
                "greater_healing_cast",
                value_fn=lambda source: {
                    "active": True,
                    "range_feet": 100,
                    "heal_hp": getattr(getattr(source, "attributes", None), "wisdom", 0)
                    + ability_level(source, "Greater Healing"),
                    "damage_undead_or_negative_targets_instead": True,
                    "damage_bypasses_defenses": True,
                    "auto_hits": True,
                    "damage_type": "light",
                    "source_ability": "Greater Healing",
                },
            ),
        },

        # Level 20
        {
            "name": "Divine Destiny",
            "type": "skill",
            "cost": 5,
            "cost_pool": "fortune",
            "target": "ally",
            "required_level": 20,
            "scales_with_level": True,
            "description": (
                "The Cleric spends fortune, increasing all of a target's defenses by one for each five points "
                "of fortune invested. The invested fortune remains committed until the spell is cancelled. "
                "A being can only be under one Divine Destiny at a time, and the Cleric can only maintain one at a time. "
                "This skill is a spell."
            ),
            "duration": "1 Turn per Skill Level",
            "is_spell": True,
            "effects": apply_state(
                "divine_destiny_active",
                value_fn=lambda source: {
                    "active": True,
                    "invested_fortune": "from_spent_amount_min_5",
                    "defense_bonus_rule": "spent_fortune_div_5",
                    "duration_turns": ability_level(source, "Divine Destiny"),
                    "one_active_divine_destiny_from_source": True,
                    "single_divine_destiny_per_target": True,
                    "held_fortune_committed": True,
                    "applies_state_to_targets": "divine_destiny_received",
                    "source_ability": "Divine Destiny",
                },
            ),
        },
        {
            "name": "Remove Condition",
            "type": "skill",
            "cost": 40,
            "cost_pool": "sanity",
            "target": "ally",
            "required_level": 20,
            "scales_with_level": False,
            "description": (
                "Instantly removes any condition except Cowering, Dying, Hungry, Maddened, "
                "Outrageous Misfortune, Starving, Thirsty, or Unconscious. "
                "This skill has no levels. This skill is a spell."
            ),
            "duration": "1 Action",
            "is_spell": True,
            "effects": apply_state(
                "remove_condition_applied",
                value_fn=lambda source: {
                    "selection_required": True,
                    "forbidden_conditions": {
                        "cowering",
                        "dying",
                        "hungry",
                        "maddened",
                        "outrageous_misfortune",
                        "starving",
                        "thirsty",
                        "unconscious",
                    },
                    "removes_selected_condition_from_target": True,
                    "source_ability": "Remove Condition",
                },
            ),
        },

        # Level 25
        {
            "grant": "Dispel Magic",
            "required_level": 25,
        },
        {
            "name": "Divine Conduit",
            "type": "skill",
            "cost": 50,
            "cost_pool": "fortune",
            "target": "self",
            "required_level": 25,
            "scales_with_level": True,
            "description": (
                "The Cleric becomes a minor avatar of their god, gaining +75 to all rolls and +25 to all defenses "
                "while divine power pours off them. This skill is a spell."
            ),
            "duration": "1 Minute per Skill Level",
            "is_spell": True,
            "effects": apply_state(
                "divine_conduit_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_minutes": ability_level(source, "Divine Conduit"),
                    "all_rolls_bonus": 75,
                    "all_defenses_bonus": 25,
                    "divine_power_visible": True,
                    "cost_fortune_per_minute": 50,
                    "source_ability": "Divine Conduit",
                },
            ),
        },
    ],
    source_type="adventure",
)