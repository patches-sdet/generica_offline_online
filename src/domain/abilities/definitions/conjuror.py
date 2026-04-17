from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    inspect,
    skill_check,
)
from domain.effects.base import Effect, EffectContext


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _conjuror_level(character) -> int:
    return character.get_progression_level("adventure", "Conjuror", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


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


# Custom effects / placeholders

class DimensionalPocketEffect(Effect):
    """
    Stores dimensional-pocket carrying rules on a target item with pockets.
    """

    def apply(self, context: EffectContext) -> None:
        capacity = _ability_level(context.source, "Dimensional Pocket")

        for target in context.targets:
            states = _ensure_states(target)
            states["dimensional_pocket"] = {
                "active": True,
                "duration_days": 1,
                "capacity_slots": capacity,
                "capacity_rule": "one_item_or_identical_stack_per_slot",
                "requires_physical_pocket": True,
                "source": context.source,
                "source_ability": "Dimensional Pocket",
            }


class HandyCreationEffect(Effect):
    """
    Placeholder for conjuring a rough common-material object.
    """

    def apply(self, context: EffectContext) -> None:
        chosen_item = context.metadata.get("chosen_item")
        chosen_material = context.metadata.get("chosen_material")

        states = _ensure_states(context.source)
        states["handy_creation_cast"] = {
            "active": True,
            "duration_minutes": _conjuror_level(context.source),
            "item_name": chosen_item or "Rough Object",
            "material": chosen_material or "common material",
            "max_dimensions_feet": (3, 3, 3),
            "max_weight_pounds": _conjuror_level(context.source),
            "cannot_be_dedicated_crafting_tool": True,
            "visibly_magical": True,
            "source_ability": "Handy Creation",
        }


class MagicSnackEffect(Effect):
    """
    Placeholder for conjuring a bland but filling magical meal.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["magic_snack_cast"] = {
            "active": True,
            "duration_meals": 1,
            "item_name": "Magic Snack",
            "effect": "acts_as_daily_nourishment_if_fully_eaten",
            "source_ability": "Magic Snack",
        }


class SummonArcaneEffect(Effect):
    """
    Generic placeholder for the Conjuror's summon line.
    """

    def __init__(self, ability_name: str, difficulty: int, creature_class: int, cost_per_level: int):
        self.ability_name = ability_name
        self.difficulty = difficulty
        self.creature_class = creature_class
        self.cost_per_level = cost_per_level

    def apply(self, context: EffectContext) -> None:
        summon_kind = context.metadata.get("summon_type", "arcane_creature")
        desired_level = context.metadata.get("summon_level", _conjuror_level(context.source))
        desired_level = min(int(desired_level), _conjuror_level(context.source))

        states = _ensure_states(context.source)
        states[f"{self.ability_name.lower().replace(' ', '_')}_cast"] = {
            "active": True,
            "summon_kind": summon_kind,
            "creature_type": "arcane",
            "creature_class": self.creature_class,
            "max_creature_level": _conjuror_level(context.source),
            "chosen_creature_level": desired_level,
            "skill_level": _ability_level(context.source, self.ability_name),
            "summon_difficulty": self.difficulty,
            "duration_rule": "one_minute_per_full_20_over_difficulty",
            "obeys_conjuror_orders": True,
            "cost_moxie_per_creature_level": self.cost_per_level,
            "source_ability": self.ability_name,
        }


class FoolsGoldEffect(Effect):
    """
    Placeholder for temporary conjured gold.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["fools_gold_cast"] = {
            "active": True,
            "duration_minutes": _ability_level(context.source, "Fool's Gold") * 10,
            "coin_count": _conjuror_level(context.source),
            "temporary_gold": True,
            "registers_as_magical": True,
            "disbelief_check": {
                "searcher_stat": "perception",
                "resist_stat": "charisma",
            },
            "source_ability": "Fool's Gold",
        }


class HandyShieldEffect(Effect):
    """
    Placeholder for conjuring a temporary shield.
    """

    def apply(self, context: EffectContext) -> None:
        chosen_level = context.metadata.get("item_level", _conjuror_level(context.source))
        chosen_level = min(int(chosen_level), _conjuror_level(context.source))

        states = _ensure_states(context.source)
        states["handy_shield_cast"] = {
            "active": True,
            "duration_turns": _ability_level(context.source, "Handy Shield"),
            "item_type": "shield",
            "item_level": chosen_level,
            "source_ability": "Handy Shield",
        }


class HandyWeaponEffect(Effect):
    """
    Placeholder for conjuring a temporary weapon.
    """

    def apply(self, context: EffectContext) -> None:
        chosen_weapon = context.metadata.get("chosen_item", "Weapon")
        chosen_level = context.metadata.get("item_level", _conjuror_level(context.source))
        chosen_level = min(int(chosen_level), _conjuror_level(context.source))

        states = _ensure_states(context.source)
        states["handy_weapon_cast"] = {
            "active": True,
            "duration_turns": _ability_level(context.source, "Handy Weapon"),
            "item_type": chosen_weapon,
            "item_level": chosen_level,
            "source_ability": "Handy Weapon",
        }


class HandyToolsEffect(Effect):
    """
    Placeholder for conjuring exceptional crafting tools.
    """

    def apply(self, context: EffectContext) -> None:
        chosen_tool = context.metadata.get("chosen_item", "Crafting Tools")
        bonus = _conjuror_level(context.source) // 5

        states = _ensure_states(context.source)
        states["handy_tools_cast"] = {
            "active": True,
            "duration_minutes": _ability_level(context.source, "Handy Tools"),
            "tool_type": chosen_tool,
            "crafting_bonus": bonus,
            "tool_quality": "exceptional",
            "source_ability": "Handy Tools",
        }


class ConjurorsCacophonyEffect(Effect):
    """
    Placeholder for a fixed-location speech-denial and sanity-damage zone.
    """

    def apply(self, context: EffectContext) -> None:
        states = _ensure_states(context.source)
        states["conjurors_cacophony_active"] = {
            "active": True,
            "duration_turns": _ability_level(context.source, "Conjuror's Cacophony"),
            "fixed_to_cast_location": True,
            "speech_impossible": True,
            "damage_pool": "sanity",
            "damage_amount": _conjuror_level(context.source),
            "resist_roll": {
                "attack_stat": "charisma",
                "skill_name": "Conjuror's Cacophony",
                "target_stat": "willpower",
            },
            "affects_conjuror_too": True,
            "source_ability": "Conjuror's Cacophony",
        }


class StickAroundWhyDontchaEffect(Effect):
    """
    Placeholder for extending one summoned creature's stay.
    """

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            states = _ensure_states(target)
            states["stick_around_why_dontcha"] = {
                "active": True,
                "duration_days": 1,
                "single_enchanted_summon_per_conjuror": True,
                "dispel_sends_target_home": True,
                "source": context.source,
                "source_ability": "Stick Around, Why Dontcha",
            }

        source_states = _ensure_states(context.source)
        source_states["stick_around_active"] = {
            "active": True,
            "targets": list(context.targets),
            "one_active_target_only": True,
            "duration_days": 1,
            "source_ability": "Stick Around, Why Dontcha",
        }


# Conjuror

build_job("Conjuror", [

    # Level 1

    {
        "name": "Conjuror's Eye",
        "cost": 5,
        "cost_pool": "sanity",
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
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "arcane_creature",
        "type": "skill",
    },

    {
        "name": "Dimensional Pocket",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "The Conjuror enchants any item with at least one pocket into a dimensional pocket. "
            "It can hold a number of items or identical collections of items equal to this skill's level. "
            "This skill is a spell."
        ),
        "duration": "1 Day",
        "effects": DimensionalPocketEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "item_with_pocket",
        "type": "skill",
    },

    {
        "name": "Handy Creation",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "The Conjuror creates a rough object of common material. It cannot exceed three feet "
            "in any dimension, cannot be a dedicated crafting tool, is visibly magical, and cannot "
            "weigh more than one pound per Conjuror level. This skill is a spell."
        ),
        "duration": "1 Minute per Level",
        "effects": HandyCreationEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "unoccupied_space",
        "type": "skill",
    },

    {
        "name": "Magic Snack",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "The Conjuror creates a bland but filling magical meal that provides daily nourishment "
            "to anyone who eats all of it. This skill has no levels. This skill is a spell."
        ),
        "duration": "1 Meal",
        "effects": MagicSnackEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "unoccupied_space",
        "type": "skill",
    },

    {
        "name": "Summon Least",
        "cost": 5,
        "cost_pool": "moxie",
        "description": (
            "The Conjuror calls forth a Class One Arcane being, typically a daemon, djinn, elemental, "
            "manabeast, or old one. The creature may be any level up to the Conjuror's level and obeys "
            "the Conjuror's orders. Its skill levels equal Summon Least level. Duration depends on the "
            "margin over difficulty 100. This skill is a spell."
        ),
        "duration": "Varies",
        "effects": SummonArcaneEffect(
            ability_name="Summon Least",
            difficulty=100,
            creature_class=1,
            cost_per_level=5,
        ),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "unoccupied_space",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Fool's Gold",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "The Conjuror creates temporary gold coins equal to Conjuror level. The coins soon dissipate, "
            "register as magical, and may be recognized as fraudulent by perception against the Conjuror's "
            "charisma. This skill is a spell."
        ),
        "duration": "10 Minutes per Level",
        "effects": FoolsGoldEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Handy Shield",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "The Conjuror pulls out a shield from a dimension full of shields. It creates a shield "
            "of the caster's choosing with an item level up to the Conjuror's level. This skill is a spell."
        ),
        "duration": "1 Turn per Level",
        "effects": HandyShieldEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {"grant": "Mana Focus", "required_level": 5},

    # Level 10

    {
        "name": "Handy Weapon",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "The Conjuror pulls out a weapon from a dimension full of weapons. It creates a weapon "
            "of the caster's choosing with an item level up to the Conjuror's level. This skill is a spell."
        ),
        "duration": "1 Turn per Level",
        "effects": HandyWeaponEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 10,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Summon Minor",
        "cost": 20,
        "cost_pool": "moxie",
        "description": (
            "The Conjuror calls forth a Class Two Arcane being. The spell works like Summon Least, "
            "but uses difficulty 150 and produces a stronger minion. Its skill levels equal Summon Minor "
            "level. This skill is a spell."
        ),
        "duration": "Varies",
        "effects": SummonArcaneEffect(
            ability_name="Summon Minor",
            difficulty=150,
            creature_class=2,
            cost_per_level=20,
        ),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 10,
        "scales_with_level": True,
        "target": "unoccupied_space",
        "type": "skill",
    },

    # Level 15

    {"grant": "Cannon Fodder", "required_level": 15},

    {
        "name": "Handy Tools",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "The Conjuror creates an exceptional set of crafting tools. These tools grant a bonus to "
            "their associated crafting skills equal to Conjuror level divided by five. This skill is a spell."
        ),
        "duration": "1 Minute per Level",
        "effects": HandyToolsEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 15,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Conjuror's Cacophony",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "The Conjuror calls up a swarm of gibbering and howling voices fixed to a location. "
            "Speech becomes impossible there, and everyone who hears it, including the Conjuror, "
            "takes sanity damage equal to Conjuror level each turn unless they succeed on a Willpower "
            "roll against the Conjuror's charisma plus Conjuror's Cacophony. This skill is a spell."
        ),
        "duration": "1 Turn per Level",
        "effects": ConjurorsCacophonyEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 20,
        "scales_with_level": True,
        "target": "location",
        "type": "skill",
    },

    {
        "name": "Summon Lesser",
        "cost": 50,
        "cost_pool": "moxie",
        "description": (
            "The Conjuror calls forth a Class Three Arcane being. The spell works like Summon Least, "
            "but uses difficulty 200 and produces a skilled fighter or highly skilled specialist. "
            "Its skill levels equal Summon Lesser level. This skill is a spell."
        ),
        "duration": "Varies",
        "effects": SummonArcaneEffect(
            ability_name="Summon Lesser",
            difficulty=200,
            creature_class=3,
            cost_per_level=50,
        ),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 20,
        "scales_with_level": True,
        "target": "unoccupied_space",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Stick Around, Why Dontcha",
        "cost": 100,
        "cost_pool": "sanity",
        "description": (
            "The Conjuror enchants a summoned creature to remain for a full day. Only one creature may "
            "be affected at a time. This acts as a buff on the creature and may be dispelled, which "
            "instantly sends it home. This skill is a spell."
        ),
        "duration": "1 Day",
        "effects": StickAroundWhyDontchaEffect(),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "summoned_creature",
        "type": "skill",
    },

    {
        "name": "Summon Greater",
        "cost": 100,
        "cost_pool": "moxie",
        "description": (
            "The Conjuror calls forth a Class Four Arcane being. The spell works like Summon Least, "
            "but uses difficulty 250 and produces a powerful fighter or mage. Its skill levels equal "
            "Summon Greater level. This skill is a spell."
        ),
        "duration": "Varies",
        "effects": SummonArcaneEffect(
            ability_name="Summon Greater",
            difficulty=250,
            creature_class=4,
            cost_per_level=100,
        ),
        "is_passive": False,
        "is_spell": True,
        "is_skill": True,
        "required_level": 25,
        "scales_with_level": True,
        "target": "unoccupied_space",
        "type": "skill",
    },

], source_type="adventure")