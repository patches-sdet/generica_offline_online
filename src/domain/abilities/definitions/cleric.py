from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    modify_next_attack,
    scaled_derived_buff,
)
from domain.conditions import IS_ALLY
from domain.effects.base import Effect, EffectContext


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _cleric_level(character) -> int:
    return character.get_progression_level("adventure", "Cleric", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


def _set_attack_attr(attack, key: str, value) -> None:
    setattr(attack, key, value)


# Attack modifier helpers

def _holy_smite_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "bonus_damage", _ability_level(ctx.source, "Holy Smite"))
    _set_attack_attr(attack, "damage_type", "light")
    _set_attack_attr(attack, "holy_smite", True)


# Custom effects / placeholders

class BlessingEffect(Effect):
    """
    Invested-resource blessing placeholder.
    One active blessing bestowed by the Cleric at a time; one blessing per target.
    """

    def apply(self, context: EffectContext) -> None:
        chosen_stat = context.metadata.get("blessing_stat")
        invested_fortune = max(1, int(context.spent_amount or 1))

        states = _ensure_states(context.source)
        states["cleric_blessing_active"] = {
            "active": True,
            "targets": list(context.targets),
            "chosen_stat": chosen_stat,
            "invested_fortune": invested_fortune,
            "duration": "until_cancelled_or_dispelled",
            "one_active_blessing_from_source": True,
            "target_limit_rule": "single_blessing_per_target",
            "held_fortune_committed": invested_fortune,
            "source_ability": "Blessing",
        }

        for target in context.targets:
            target_states = _ensure_states(target)
            target_states["blessing_received"] = {
                "source": context.source,
                "chosen_stat": chosen_stat,
                "bonus": invested_fortune,
                "duration": "until_cancelled_or_dispelled",
                "source_ability": "Blessing",
            }


class GodspellEffect(Effect):
    """
    Placeholder for deity-bound godspell access.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        current = states.get("godspell_access", {})
        states["godspell_access"] = {
            "active": True,
            "deity": current.get("deity"),
            "chosen_godspell": current.get("chosen_godspell"),
            "selection_required": True,
            "source_ability": "Godspell",
        }


class ShieldOfDivinityEffect(Effect):
    """
    One-target armor buff placeholder.
    """

    def apply(self, context: EffectContext) -> None:
        bonus = _ability_level(context.source, "Shield of Divinity")

        states = _ensure_states(context.source)
        states["shield_of_divinity_active"] = {
            "active": True,
            "targets": list(context.targets),
            "armor_bonus": bonus,
            "duration_minutes": 5,
            "one_active_target_only": True,
            "source_ability": "Shield of Divinity",
        }

        for target in context.targets:
            target_states = _ensure_states(target)
            target_states["shield_of_divinity_received"] = {
                "source": context.source,
                "armor_bonus": bonus,
                "duration_minutes": 5,
                "source_ability": "Shield of Divinity",
            }


class CurativeEffect(Effect):
    """
    Removes one minor condition from the target.
    """

    REMOVABLE = {
        "bleeding",
        "diseased",
        "drunk",
        "gassy",
        "hungover",
        "nauseated",
        "numb",
        "poisoned",
    }

    def apply(self, context: EffectContext) -> None:
        chosen_condition = context.metadata.get("condition_name")

        for target in context.targets:
            states = _ensure_states(target)
            if chosen_condition in self.REMOVABLE:
                states.pop(chosen_condition, None)

            states["curative_applied"] = {
                "removed_condition": chosen_condition,
                "source": context.source,
                "source_ability": "Curative",
            }


class PartyHealEffect(Effect):
    """
    Placeholder for party-wide light healing.
    """

    def apply(self, context: EffectContext) -> None:
        amount = 10 + (_ability_level(context.source, "Party Heal") // 10)

        states = _ensure_states(context.source)
        states["party_heal_cast"] = {
            "active": True,
            "radius_feet": 100,
            "heal_hp": amount,
            "damage_undead_instead": True,
            "damage_bypasses_defenses": True,
            "auto_hits": True,
            "source_ability": "Party Heal",
        }


class PrayToGodEffect(Effect):
    """
    Placeholder for deity contact / question-answer interaction.
    """

    def apply(self, context: EffectContext) -> None:
        topic = context.metadata.get("topic")

        states = _ensure_states(context.source)
        states["pray_to_god_active"] = {
            "active": True,
            "duration_minutes": 10,
            "topic": topic,
            "communication_mode": "mental_contact",
            "response_style": "hints_and_riddles",
            "limited_by_deity_domain": True,
            "source_ability": "Pray to God",
        }


class DivineTransitEffect(Effect):
    """
    Placeholder for deity-assisted escape / extraction.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["divine_transit_cast"] = {
            "active": True,
            "targets": list(context.targets),
            "blocked_by_wards": True,
            "destination_rule": "entry_point_or_deity_choice",
            "source_ability": "Divine Transit",
        }


class HolyBoltEffect(Effect):
    """
    Placeholder for a light-based ranged spell attack.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["holy_bolt_ready"] = {
            "active": True,
            "attack_stat": "wisdom",
            "skill_name": "Holy Bolt",
            "target_stat": "luck",
            "default_damage_pool": "fortune",
            "reduced_by": "fate",
            "can_convert_to_hp_against_undead_or_dark": True,
            "damage_type": "light",
            "source_ability": "Holy Bolt",
        }


class BackYouFiendEffect(Effect):
    """
    Anti-undead / anti-dark holy aura placeholder.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["back_you_fiend_active"] = {
            "active": True,
            "radius_feet": 50,
            "duration": "until_cancelled",
            "targets": {"undead", "dark_aligned"},
            "damage_pool": "hp",
            "damage_amount": _cleric_level(context.source),
            "damage_type": "light",
            "bypasses_defenses": True,
            "auto_hits": True,
            "cost_sanity_per_minute": 30,
            "source_ability": "Back You Fiend!",
        }


class GreaterHealingEffect(Effect):
    """
    Placeholder for strong single-target light healing / anti-undead damage.
    """

    def apply(self, context: EffectContext) -> None:
        amount = getattr(getattr(context.source, "attributes", None), "wisdom", 0) + _ability_level(context.source, "Greater Healing")

        states = _ensure_states(context.source)
        states["greater_healing_cast"] = {
            "active": True,
            "targets": list(context.targets),
            "range_feet": 100,
            "heal_hp": amount,
            "damage_undead_or_negative_targets_instead": True,
            "damage_bypasses_defenses": True,
            "auto_hits": True,
            "damage_type": "light",
            "source_ability": "Greater Healing",
        }


class DivineDestinyEffect(Effect):
    """
    Invested-resource defense blessing placeholder.
    """

    def apply(self, context: EffectContext) -> None:
        invested_fortune = max(5, int(context.spent_amount or 5))
        defense_bonus = invested_fortune // 5

        states = _ensure_states(context.source)
        states["divine_destiny_active"] = {
            "active": True,
            "targets": list(context.targets),
            "invested_fortune": invested_fortune,
            "defense_bonus": defense_bonus,
            "duration_turns": _ability_level(context.source, "Divine Destiny"),
            "one_active_divine_destiny_from_source": True,
            "single_divine_destiny_per_target": True,
            "held_fortune_committed": invested_fortune,
            "source_ability": "Divine Destiny",
        }

        for target in context.targets:
            target_states = _ensure_states(target)
            target_states["divine_destiny_received"] = {
                "source": context.source,
                "defense_bonus": defense_bonus,
                "duration_turns": _ability_level(context.source, "Divine Destiny"),
                "source_ability": "Divine Destiny",
            }


class RemoveConditionEffect(Effect):
    """
    Removes almost any condition except the explicitly forbidden set.
    """

    FORBIDDEN = {
        "cowering",
        "dying",
        "hungry",
        "maddened",
        "outrageous_misfortune",
        "starving",
        "thirsty",
        "unconscious",
    }

    def apply(self, context: EffectContext) -> None:
        chosen_condition = context.metadata.get("condition_name")

        for target in context.targets:
            states = _ensure_states(target)
            if chosen_condition and chosen_condition not in self.FORBIDDEN:
                states.pop(chosen_condition, None)

            states["remove_condition_applied"] = {
                "removed_condition": chosen_condition,
                "source": context.source,
                "source_ability": "Remove Condition",
            }


class DispelMagicEffect(Effect):
    """
    Placeholder for contested dispel / suppression logic.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["dispel_magic_ready"] = {
            "active": True,
            "attack_stat": "wisdom",
            "skill_name": "Dispel Magic",
            "target_resist_stat": "willpower_or_creator_level_x5",
            "critical_success_dispels_all": True,
            "margin_under_20_dispels": 1,
            "extra_spell_per_full_margin_20": True,
            "can_target_person_item_location_or_fixed_spell": True,
            "source_ability": "Dispel Magic",
        }


class DivineConduitEffect(Effect):
    """
    Major divine empowerment state.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["divine_conduit_active"] = {
            "active": True,
            "duration_minutes": _ability_level(context.source, "Divine Conduit"),
            "all_rolls_bonus": 75,
            "all_defenses_bonus": 25,
            "divine_power_visible": True,
            "cost_fortune_per_minute": 50,
            "source_ability": "Divine Conduit",
        }


# Cleric

build_job("Cleric", [

    # Level 1

    {
        "name": "Blessing",
        "cost": 1,
        "cost_pool": "fortune",
        "description": (
            "The Cleric spends fortune to increase a single chosen attribute of an ally by an equal amount. "
            "That fortune remains committed until the spell is cancelled. A being can only be under one blessing "
            "at a time, and the Cleric can only maintain one blessing at a time. This skill is a spell."
        ),
        "duration": "Until Cancelled or Dispelled",
        "effects": BlessingEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Faith",
        "description": "Your Fate is increased by your Cleric level.",
        "duration": "Passive Constant",
        "effects": scaled_derived_buff(
            stat="fate",
            scale_fn=lambda c: c.get_progression_level("adventure", "Cleric", 0),
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Godspell",
        "description": (
            "The Cleric gains access to the unique Godspell of their chosen deity. "
            "This is a structured placeholder until deity selection and godspell binding are implemented."
        ),
        "duration": "Varies",
        "effects": GodspellEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Holy Smite",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "Holy Smite increases the Cleric's next melee attack damage by 1 per level of this skill. "
            "This skill is a spell."
        ),
        "duration": "1 Minute per Level",
        "effects": modify_next_attack(_holy_smite_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    {"grant": "Lesser Healing", "required_level": 1},

    {
        "name": "Shield of Divinity",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "The Cleric buffs a single target's armor by an amount equal to the level of this skill. "
            "The Cleric can only apply this buff to one target at a time. This skill is a spell."
        ),
        "duration": "5 Minutes",
        "effects": ShieldOfDivinityEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Curative",
        "cost": 15,
        "cost_pool": "sanity",
        "description": (
            "Instantly removes one of the following conditions from the target: "
            "Bleeding, Diseased, Drunk, Gassy, Hungover, Nauseated, Numb, or Poisoned. "
            "This skill has no levels. This skill is a spell."
        ),
        "duration": "Instant",
        "effects": CurativeEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Party Heal",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "Instantly heals all living party members within one hundred feet of the Cleric. "
            "The amount healed is 10 plus Party Heal level divided by 10. Undead party members "
            "take light-based damage instead, bypassing defenses and automatically hitting. "
            "This skill is a spell."
        ),
        "duration": "Instant",
        "effects": PartyHealEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "party",
        "type": "skill",
    },

    {
        "name": "Pray to God",
        "cost": 20,
        "cost_pool": "fortune",
        "description": (
            "The Cleric enters mental contact with their deity for up to ten minutes. "
            "The deity can usually answer with hints and riddles within their area of influence. "
            "This skill has no levels. This skill is a spell."
        ),
        "duration": "10 Minutes",
        "effects": PrayToGodEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Divine Transit",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "The Cleric petitions their deity to extract affected people from a dungeon, building, "
            "or alien plane of existence. Wards and similar countermeasures can prevent this. "
            "This skill has no levels. This skill is a spell."
        ),
        "duration": "Instant",
        "effects": DivineTransitEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 10,
        "scales_with_level": False,
        "target": "group",
        "type": "skill",
    },

    {
        "name": "Holy Bolt",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "The Cleric calls down a holy bolt upon a foe, using Wisdom plus Holy Bolt "
            "against the target's Luck. It normally inflicts fortune damage reduced by Fate, "
            "but against undead or dark foes it may instead inflict HP damage. This skill is a spell."
        ),
        "duration": "1 Attack",
        "effects": HolyBoltEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 10,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Back You Fiend!",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "The Cleric becomes a beacon of holy light. Any undead or dark-aligned entity "
            "that comes within fifty feet takes damage equal to the Cleric's level, bypassing "
            "all defenses and automatically hitting. This skill has no levels. This skill is a spell."
        ),
        "duration": "Until Cancelled",
        "effects": BackYouFiendEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 15,
        "scales_with_level": False,
        "target": "undead_or_dark",
        "type": "skill",
    },

    {
        "name": "Greater Healing",
        "cost": 25,
        "cost_pool": "sanity",
        "description": (
            "Instantly heals a living target within one hundred feet of the Cleric, restoring HP equal "
            "to the Cleric's Wisdom plus Greater Healing level. Against undead or negative-natured targets, "
            "it deals light-based damage instead, bypassing defenses and automatically hitting. This skill is a spell."
        ),
        "duration": "1 Action",
        "effects": GreaterHealingEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 15,
        "scales_with_level": True,
        "target": "ally_or_enemy",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Divine Destiny",
        "cost": 5,
        "cost_pool": "fortune",
        "description": (
            "The Cleric spends fortune, increasing all of a target's defenses by one for each five points "
            "of fortune invested. The invested fortune remains committed until the spell is cancelled. "
            "A being can only be under one Divine Destiny at a time, and the Cleric can only maintain one at a time. "
            "This skill is a spell."
        ),
        "duration": "1 Turn per Skill Level",
        "effects": DivineDestinyEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 20,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Remove Condition",
        "cost": 40,
        "cost_pool": "sanity",
        "description": (
            "Instantly removes any condition except Cowering, Dying, Hungry, Maddened, "
            "Outrageous Misfortune, Starving, Thirsty, or Unconscious. "
            "This skill has no levels. This skill is a spell."
        ),
        "duration": "1 Action",
        "effects": RemoveConditionEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "ally",
        "type": "skill",
    },

    # Level 25

    {"grant": "Dispel Magic", "required_level": 25},

    {
        "name": "Divine Conduit",
        "cost": 50,
        "cost_pool": "fortune",
        "description": (
            "The Cleric becomes a minor avatar of their god, gaining +75 to all rolls and +25 to all defenses "
            "while divine power pours off them. This skill is a spell."
        ),
        "duration": "1 Minute per Skill Level",
        "effects": DivineConduitEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 25,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

], source_type="adventure")