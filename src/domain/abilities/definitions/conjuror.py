from domain.abilities import ability_level, progression_level
from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    inspect,
    skill_check,
)

def _conjurors_eye_difficulty(ctx, target) -> int:
    controller = getattr(target, "controller", None)
    if controller is not None and getattr(target, "type", None) == "arcane":
        return int(getattr(getattr(controller, "attributes", None), "willpower", 0))
    return int(getattr(getattr(target, "attributes", None), "willpower", 0))

def _conjurors_eye_reveal(ctx, target) -> dict:
    return {
        "type": getattr(target, "type", None),
        "current_hp": getattr(target, "current_hp", None),
        "attributes": getattr(target, "attributes", None),
        "progressions": getattr(target, "progressions", None),
        "controller": getattr(target, "controller", None),
    }

def _summon_arcane_state(
    ability_name: str,
    difficulty: int,
    creature_class: int,
    cost_per_level: int,
):
    return apply_state(
        f"{ability_name.lower().replace(' ', '_')}_cast",
        value_fn=lambda source: {
            "active": True,
            "summon_kind": None,
            "selection_required": True,
            "creature_type": "arcane",
            "creature_class": creature_class,
            "max_creature_level": progression_level(source, "adventure", "Conjuror"),
            "chosen_creature_level": "from_metadata_or_conjuror_level_cap",
            "skill_level": ability_level(source, ability_name),
            "summon_difficulty": difficulty,
            "duration_rule": "one_minute_per_full_20_over_difficulty",
            "obeys_conjuror_orders": True,
            "cost_moxie_per_creature_level": cost_per_level,
            "source_ability": ability_name,
        },
    )

build_job(
    "Conjuror",
    [
        # Level 1
        {
            "name": "Conjuror's Eye",
            "type": "skill",
            "cost": 5,
            "cost_pool": "sanity",
            "target": "arcane_creature",
            "required_level": 1,
            "scales_with_level": False,
            "is_spell": True,
            "description": (
                "The Conjuror examines the status of an arcane creature. This is an Intelligence plus "
                "Conjuror's Eye roll resisted by the target's Willpower. Arcane party creatures may "
                "substitute their controller's Willpower. This skill is a spell."
            ),
            "duration": "1 Minute",
            "effects": skill_check(
                ability="Conjuror's Eye",
                stat="intelligence",
                difficulty=_conjurors_eye_difficulty,
                on_success=inspect(
                    reveal_fn=_conjurors_eye_reveal,
                ),
            ),
        },
        {
            "name": "Dimensional Pocket",
            "type": "skill",
            "cost": 20,
            "cost_pool": "sanity",
            "target": "item_with_pocket",
            "required_level": 1,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Conjuror enchants any item with at least one pocket into a dimensional pocket. "
                "It can hold a number of items or identical collections of items equal to this skill's level. "
                "This skill is a spell."
            ),
            "duration": "1 Day",
            "effects": apply_state(
                "dimensional_pocket",
                value_fn=lambda source: {
                    "active": True,
                    "duration_days": 1,
                    "capacity_slots": ability_level(source, "Dimensional Pocket"),
                    "capacity_rule": "one_item_or_identical_stack_per_slot",
                    "requires_physical_pocket": True,
                    "applies_to_target_item": True,
                    "source_ability": "Dimensional Pocket",
                },
            ),
        },
        {
            "name": "Handy Creation",
            "type": "skill",
            "cost": 5,
            "cost_pool": "sanity",
            "target": "unoccupied_space",
            "required_level": 1,
            "scales_with_level": False,
            "is_spell": True,
            "description": (
                "The Conjuror creates a rough object of common material. It cannot exceed three feet "
                "in any dimension, cannot be a dedicated crafting tool, is visibly magical, and cannot "
                "weigh more than one pound per Conjuror level. This skill is a spell."
            ),
            "duration": "1 Minute per Level",
            "effects": apply_state(
                "handy_creation_cast",
                value_fn=lambda source: {
                    "active": True,
                    "duration_minutes": progression_level(source, "adventure", "Conjuror"),
                    "item_name": None,
                    "material": None,
                    "selection_required": True,
                    "default_item_name": "Rough Object",
                    "default_material": "common material",
                    "max_dimensions_feet": (3, 3, 3),
                    "max_weight_pounds": progression_level(source, "adventure", "Conjuror"),
                    "cannot_be_dedicated_crafting_tool": True,
                    "visibly_magical": True,
                    "source_ability": "Handy Creation",
                },
            ),
        },
        {
            "name": "Magic Snack",
            "type": "skill",
            "cost": 10,
            "cost_pool": "sanity",
            "target": "unoccupied_space",
            "required_level": 1,
            "scales_with_level": False,
            "is_spell": True,
            "description": (
                "The Conjuror creates a bland but filling magical meal that provides daily nourishment "
                "to anyone who eats all of it. This skill has no levels. This skill is a spell."
            ),
            "duration": "1 Meal",
            "effects": apply_state(
                "magic_snack_cast",
                value_fn=lambda source: {
                    "active": True,
                    "duration_meals": 1,
                    "item_name": "Magic Snack",
                    "effect": "acts_as_daily_nourishment_if_fully_eaten",
                    "source_ability": "Magic Snack",
                },
            ),
        },
        {
            "name": "Summon Least",
            "type": "skill",
            "cost": 5,
            "cost_pool": "moxie",
            "target": "unoccupied_space",
            "required_level": 1,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Conjuror calls forth a Class One Arcane being, typically a daemon, djinn, elemental, "
                "manabeast, or old one. The creature may be any level up to the Conjuror's level and obeys "
                "the Conjuror's orders. Its skill levels equal Summon Least level. Duration depends on the "
                "margin over difficulty 100. This skill is a spell."
            ),
            "duration": "Varies",
            "effects": _summon_arcane_state(
                ability_name="Summon Least",
                difficulty=100,
                creature_class=1,
                cost_per_level=5,
            ),
        },

        # Level 5
        {
            "name": "Fool's Gold",
            "type": "skill",
            "cost": 10,
            "cost_pool": "sanity",
            "target": "self",
            "required_level": 5,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Conjuror creates temporary gold coins equal to Conjuror level. The coins soon dissipate, "
                "register as magical, and may be recognized as fraudulent by Perception against the Conjuror's "
                "Charisma. This skill is a spell."
            ),
            "duration": "10 Minutes per Level",
            "effects": apply_state(
                "fools_gold_cast",
                value_fn=lambda source: {
                    "active": True,
                    "duration_minutes": ability_level(source, "Fool's Gold") * 10,
                    "coin_count": progression_level(source, "adventure", "Conjuror"),
                    "temporary_gold": True,
                    "registers_as_magical": True,
                    "disbelief_check": {
                        "searcher_stat": "perception",
                        "resist_stat": "charisma",
                    },
                    "source_ability": "Fool's Gold",
                },
            ),
        },
        {
            "name": "Handy Shield",
            "type": "skill",
            "cost": 10,
            "cost_pool": "sanity",
            "target": "self",
            "required_level": 5,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Conjuror pulls out a shield from a dimension full of shields. It creates a shield "
                "of the caster's choosing with an item level up to the Conjuror's level. This skill is a spell."
            ),
            "duration": "1 Turn per Level",
            "effects": apply_state(
                "handy_shield_cast",
                value_fn=lambda source: {
                    "active": True,
                    "duration_turns": ability_level(source, "Handy Shield"),
                    "item_type": "shield",
                    "item_level": "from_metadata_or_conjuror_level_cap",
                    "selection_required": True,
                    "max_item_level": progression_level(source, "adventure", "Conjuror"),
                    "source_ability": "Handy Shield",
                },
            ),
        },
        {"grant": "Mana Focus", "required_level": 5},

        # Level 10
        {
            "name": "Handy Weapon",
            "type": "skill",
            "cost": 20,
            "cost_pool": "sanity",
            "target": "self",
            "required_level": 10,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Conjuror pulls out a weapon from a dimension full of weapons. It creates a weapon "
                "of the caster's choosing with an item level up to the Conjuror's level. This skill is a spell."
            ),
            "duration": "1 Turn per Level",
            "effects": apply_state(
                "handy_weapon_cast",
                value_fn=lambda source: {
                    "active": True,
                    "duration_turns": ability_level(source, "Handy Weapon"),
                    "item_type": None,
                    "selection_required": True,
                    "default_item_type": "Weapon",
                    "item_level": "from_metadata_or_conjuror_level_cap",
                    "max_item_level": progression_level(source, "adventure", "Conjuror"),
                    "source_ability": "Handy Weapon",
                },
            ),
        },
        {
            "name": "Summon Minor",
            "type": "skill",
            "cost": 20,
            "cost_pool": "moxie",
            "target": "unoccupied_space",
            "required_level": 10,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Conjuror calls forth a Class Two Arcane being. The spell works like Summon Least, "
                "but uses difficulty 150 and produces a stronger minion. Its skill levels equal Summon Minor "
                "level. This skill is a spell."
            ),
            "duration": "Varies",
            "effects": _summon_arcane_state(
                ability_name="Summon Minor",
                difficulty=150,
                creature_class=2,
                cost_per_level=20,
            ),
        },

        # Level 15
        {"grant": "Cannon Fodder", "required_level": 15},

        {
            "name": "Handy Tools",
            "type": "skill",
            "cost": 30,
            "cost_pool": "sanity",
            "target": "self",
            "required_level": 15,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Conjuror creates an exceptional set of crafting tools. These tools grant a bonus to "
                "their associated crafting skills equal to Conjuror level divided by five. This skill is a spell."
            ),
            "duration": "1 Minute per Level",
            "effects": apply_state(
                "handy_tools_cast",
                value_fn=lambda source: {
                    "active": True,
                    "duration_minutes": ability_level(source, "Handy Tools"),
                    "tool_type": None,
                    "selection_required": True,
                    "default_tool_type": "Crafting Tools",
                    "crafting_bonus": progression_level(source, "adventure", "Conjuror") // 5,
                    "tool_quality": "exceptional",
                    "source_ability": "Handy Tools",
                },
            ),
        },

        # Level 20
        {
            "name": "Conjuror's Cacophony",
            "type": "skill",
            "cost": 50,
            "cost_pool": "sanity",
            "target": "location",
            "required_level": 20,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Conjuror calls up a swarm of gibbering and howling voices fixed to a location. "
                "Speech becomes impossible there, and everyone who hears it, including the Conjuror, "
                "takes Sanity damage equal to Conjuror level each turn unless they succeed on a Willpower "
                "roll against the Conjuror's Charisma plus Conjuror's Cacophony. This skill is a spell."
            ),
            "duration": "1 Turn per Level",
            "effects": apply_state(
                "conjurors_cacophony_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_turns": ability_level(source, "Conjuror's Cacophony"),
                    "fixed_to_cast_location": True,
                    "speech_impossible": True,
                    "damage_pool": "sanity",
                    "damage_amount": progression_level(source, "adventure", "Conjuror"),
                    "resist_roll": {
                        "attack_stat": "charisma",
                        "skill_name": "Conjuror's Cacophony",
                        "target_stat": "willpower",
                    },
                    "affects_conjuror_too": True,
                    "source_ability": "Conjuror's Cacophony",
                },
            ),
        },
        {
            "name": "Summon Lesser",
            "type": "skill",
            "cost": 50,
            "cost_pool": "moxie",
            "target": "unoccupied_space",
            "required_level": 20,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Conjuror calls forth a Class Three Arcane being. The spell works like Summon Least, "
                "but uses difficulty 200 and produces a skilled fighter or highly skilled specialist. "
                "Its skill levels equal Summon Lesser level. This skill is a spell."
            ),
            "duration": "Varies",
            "effects": _summon_arcane_state(
                ability_name="Summon Lesser",
                difficulty=200,
                creature_class=3,
                cost_per_level=50,
            ),
        },

        # Level 25
        {
            "name": "Stick Around, Why Dontcha",
            "type": "skill",
            "cost": 100,
            "cost_pool": "sanity",
            "target": "summoned_creature",
            "required_level": 25,
            "scales_with_level": False,
            "is_spell": True,
            "description": (
                "The Conjuror enchants a summoned creature to remain for a full day. Only one creature may "
                "be affected at a time. This acts as a buff on the creature and may be dispelled, which "
                "instantly sends it home. This skill is a spell."
            ),
            "duration": "1 Day",
            "effects": apply_state(
                "stick_around_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_days": 1,
                    "one_active_target_only": True,
                    "applies_state_to_targets": "stick_around_why_dontcha",
                    "target_state_payload": {
                        "active": True,
                        "duration_days": 1,
                        "single_enchanted_summon_per_conjuror": True,
                        "dispel_sends_target_home": True,
                    },
                    "source_ability": "Stick Around, Why Dontcha",
                },
            ),
        },
        {
            "name": "Summon Greater",
            "type": "skill",
            "cost": 100,
            "cost_pool": "moxie",
            "target": "unoccupied_space",
            "required_level": 25,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Conjuror calls forth a Class Four Arcane being. The spell works like Summon Least, "
                "but uses difficulty 250 and produces a powerful fighter or mage. Its skill levels equal "
                "Summon Greater level. This skill is a spell."
            ),
            "duration": "Varies",
            "effects": _summon_arcane_state(
                ability_name="Summon Greater",
                difficulty=250,
                creature_class=4,
                cost_per_level=100,
            ),
        },
    ],
    source_type="adventure",
)