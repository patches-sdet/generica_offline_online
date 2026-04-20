from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    create_item,
    inspect,
    passive_modifier,
)

# Local metadata keys

PRODUCT_TYPE = "product_type"                  # "reagent" | "crystal"
TIER = "tier"                                  # "basic" | "potent" | "greater"
BOOSTER_STAT = "booster_stat"                  # e.g. "strength"
TARGET_POISON_DIFFICULTY = "target_poison_difficulty"
TARGET_DISEASE_DIFFICULTY = "target_disease_difficulty"
TRANQUILIZER_TIER = "tranquilizer_tier"        # "basic" | "heavy"
TRANQUILIZER_FORM = "tranquilizer_form"        # "potion" | "poison"
COLOR_STEPS = "color_steps"                    # int >= 1
EXTRA_SILVER = "extra_silver"
SUBSTANCE_DIFFICULTY = "substance_difficulty"
SUBSTANCE_RARITY = "substance_rarity"
SUBSTANCE_PROPERTIES = "substance_properties"
SUBSTANCE_ALCHEMY_VALUE = "substance_alchemy_value"

# Rule helpers

def _alchemist_level(character) -> int:
    return character.get_progression_level("adventure", "Alchemist", 0)


def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


# Item factory helpers

def _make_distilled_material_factory(product_type: str, *, tier: str):
    def factory_fn(source, _target):
        return {
            "type": "alchemy_material",
            "name": f"{tier.title()} Distilled {product_type.title()}",
            "product_type": product_type,
            "tier": tier,
            "source_job": "Alchemist",
        }
    return factory_fn


def _make_healing_potion_factory(tier: str):
    reagent_tier = {
        "basic": "red",
        "potent": "orange",
        "greater": "yellow",
    }[tier]

    def factory_fn(source, _target):
        return {
            "type": "potion",
            "name": f"{tier.title()} Healing Potion",
            "potion_family": "healing",
            "tier": tier,
            "reagent_tier": reagent_tier,
            "source_job": "Alchemist",
        }
    return factory_fn


def _make_mana_potion_factory(tier: str):
    reagent_tier = {
        "basic": "red",
        "potent": "orange",
        "greater": "yellow",
    }[tier]

    def factory_fn(source, _target):
        return {
            "type": "potion",
            "name": f"{tier.title()} Mana Potion",
            "potion_family": "mana",
            "tier": tier,
            "reagent_tier": reagent_tier,
            "source_job": "Alchemist",
        }
    return factory_fn


def _make_attribute_booster_factory(tier: str, booster_stat: str):
    def factory_fn(source, _target):
        return {
            "type": "potion",
            "name": f"{tier.title()} {booster_stat.title()} Booster",
            "potion_family": "attribute_booster",
            "tier": tier,
            "booster_stat": booster_stat,
            "crystal_tier": "level_1",
            "source_job": "Alchemist",
        }
    return factory_fn


def _make_universal_antidote_factory():
    def factory_fn(source, target):
        return {
            "type": "cure",
            "name": "Universal Antidote",
            "cure_family": "universal_antidote",
            "target_name": getattr(target, "name", None),
            "source_job": "Alchemist",
        }
    return factory_fn


def _make_speed_potion_factory(tier: str):
    reagent_count = {
        "basic": 1,
        "potent": 2,
        "greater": 3,
    }[tier]

    def factory_fn(source, _target):
        return {
            "type": "potion",
            "name": f"{tier.title()} Speed Potion",
            "potion_family": "speed",
            "tier": tier,
            "reagent_tier": "red",
            "reagent_count": reagent_count,
            "source_job": "Alchemist",
        }
    return factory_fn


def _make_tranquilizer_factory(tier: str, form: str):
    crystal_tier = "level_1" if tier == "basic" else "level_2"

    def factory_fn(source, _target):
        return {
            "type": "tranquilizer",
            "name": f"{tier.title()} Tranquilizer",
            "tranquilizer_tier": tier,
            "form": form,
            "crystal_tier": crystal_tier,
            "source_job": "Alchemist",
        }
    return factory_fn


def _make_upgraded_reagent_factory(color_steps: int):
    def factory_fn(source, _target):
        return {
            "type": "alchemy_material",
            "name": "Upgraded Reagent",
            "product_type": "upgraded_reagent",
            "color_steps": color_steps,
            "source_job": "Alchemist",
        }
    return factory_fn


# Passive helpers

def _internal_chemistry_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["internal_chemistry"] = {
        "active": True,
        "choose_one_on_potion_use": True,
        "options": (
            "double_duration",
            "double_one_numerical_value",
            "delay_reaction",
        ),
        "max_delay_minutes": _alchemist_level(ctx.source),
        "source_ability": "Internal Chemistry",
    }


def _alchemical_experimentation_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["alchemical_experimentation"] = {
        "active": True,
        "experimental_skill_capacity": _alchemist_level(ctx.source) // 10,
        "extra_experimental_skills_stored_in_journals": True,
        "source_ability": "Alchemical Experimentation",
    }


build_job("Alchemist", [

    # Level 1

    {
        "name": "Analyze",
        "required_level": 1,
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "10 Seconds",
        "description": (
            "Determine the properties of a studied liquid, powder, crystal, or reagent."
        ),
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "analyze",
                "check": {
                    "stat": "intelligence",
                    "skill": "Analyze",
                    "difficulty_from_context": SUBSTANCE_DIFFICULTY,
                },
                "reveals": {
                    "properties": SUBSTANCE_PROPERTIES,
                    "rarity": SUBSTANCE_RARITY,
                    "alchemy_value": SUBSTANCE_ALCHEMY_VALUE,
                },
                "failure_blocks_further_attempts_today": True,
                "source_ability": "Analyze",
            },
        ),
        "is_skill": True,
        "scales_with_level": False,
        "target": "object",
    },

    {
        "name": "Bomb",
        "required_level": 1,
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "duration": "1 Attack",
        "description": (
            "Throw an improvised bomb that damages the target and nearby foes."
        ),
        "effects": apply_state(
            "bomb_active",
            value_fn=lambda source: {
                "active": True,
                "attack_stat": "dexterity",
                "attack_skill": "Bomb",
                "target_stat": "agility",
                "damage_pool": "hp",
                "damage_bonus_from_alchemist_level": _alchemist_level(source),
                "affects_nearby_foes": True,
                "splash_shape_runtime_defined": True,
                "source_ability": "Bomb",
            },
        ),
        "is_skill": True,
        "scales_with_level": True,
        "target": "enemy",
    },

    {
        "name": "Distill",
        "required_level": 1,
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": (
            "Turn valuable substances into red reagents or level 1 crystals."
        ),
        "effects": create_item(
            factory_fn=lambda source, target: _make_distilled_material_factory(
                product_type="reagent",
                tier="level_1",
            )(source, target),
        ),
        "is_skill": True,
        "scales_with_level": False,
        "target": "self",
    },

    {
        "name": "Healing Potion",
        "required_level": 1,
        "type": "skill",
        "cost": 20,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": (
            "Create a basic, potent, or greater healing potion."
        ),
        "effects": create_item(
            factory_fn=lambda source, target: _make_healing_potion_factory("basic")(source, target),
        ),
        "is_skill": True,
        "scales_with_level": False,
        "target": "self",
    },

    {
        "name": "Mana Potion",
        "required_level": 1,
        "type": "skill",
        "cost": 20,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": (
            "Create a basic, potent, or greater mana potion."
        ),
        "effects": create_item(
            factory_fn=lambda source, target: _make_mana_potion_factory("basic")(source, target),
        ),
        "is_skill": True,
        "scales_with_level": False,
        "target": "self",
    },

    # Level 5

    {
        "name": "Attribute Booster",
        "required_level": 5,
        "type": "skill",
        "cost": 40,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": (
            "Create a basic, potent, or greater attribute booster of a chosen type."
        ),
        "effects": create_item(
            factory_fn=lambda source, target: _make_attribute_booster_factory(
                "basic",
                "strength",
            )(source, target),
        ),
        "is_skill": True,
        "scales_with_level": True,
        "target": "self",
    },

    {
        "name": "Duck and Cover",
        "required_level": 5,
        "type": "skill",
        "cost": 10,
        "cost_pool": "stamina",
        "duration": "Instant",
        "description": (
            "Fall prone without spending an action, reducing certain incoming damage while prone."
        ),
        "effects": apply_state(
            "duck_and_cover_active",
            value_fn=lambda source: {
                "active": True,
                "apply_condition": "prone",
                "chemical_damage_reduction": _ability_level(source, "Duck and Cover"),
                "elemental_damage_reduction": _ability_level(source, "Duck and Cover"),
                "source_ability": "Duck and Cover",
            },
        ),
        "is_skill": True,
        "scales_with_level": True,
        "target": "self",
    },

    {
        "name": "Universal Antidote",
        "required_level": 5,
        "type": "skill",
        "cost": 40,
        "cost_pool": "sanity",
        "duration": "1 Dosage",
        "description": (
            "Create a cure for a studied poison or disease affecting a specific target."
        ),
        "effects": create_item(
            factory_fn=_make_universal_antidote_factory(),
        ),
        "is_skill": True,
        "scales_with_level": True,
        "target": "ally",
    },

    # Level 10

    {
        "name": "Geek Fire",
        "required_level": 10,
        "type": "skill",
        "cost": 20,
        "cost_pool": "stamina",
        "duration": "1 Attack",
        "description": (
            "Throw improvised napalm, dealing fire damage and potentially igniting the target."
        ),
        "effects": apply_state(
            "geek_fire_active",
            value_fn=lambda source: {
                "active": True,
                "attack_stat": "dexterity",
                "attack_skill": "Geek Fire",
                "target_stat": "agility",
                "damage_pool": "hp",
                "damage_bonus_from_alchemist_level": _alchemist_level(source),
                "damage_type": "fire",
                "critical_burning_runtime_defined": True,
                "source_ability": "Geek Fire",
            },
        ),
        "is_skill": True,
        "scales_with_level": True,
        "target": "enemy",
    },

    {
        "name": "Internal Chemistry",
        "required_level": 10,
        "type": "passive",
        "duration": "Passive Constant",
        "description": (
            "Choose one enhancement whenever consuming a potion."
        ),
        "effects": passive_modifier(_internal_chemistry_modifier),
        "scales_with_level": False,
    },

    # Level 15

    {
        "name": "Distill II",
        "required_level": 15,
        "type": "skill",
        "cost": 30,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": (
            "Turn valuable substances into orange reagents or level 2 crystals."
        ),
        "effects": create_item(
            factory_fn=lambda source, target: _make_distilled_material_factory(
                product_type="reagent",
                tier="level_2",
            )(source, target),
        ),
        "is_skill": True,
        "scales_with_level": True,
        "target": "self",
    },

    {
        "name": "Distilled Id",
        "required_level": 15,
        "type": "skill",
        "cost": 50,
        "cost_pool": "stamina",
        "duration": "1 Turn per Alchemist Level",
        "description": (
            "Drink a volatile concoction to gain or enhance Rage temporarily."
        ),
        "effects": apply_state(
            "distilled_id_active",
            value_fn=lambda source: {
                "active": True,
                "rage_proxy_level": _ability_level(source, "Distilled Id"),
                "duration_turns": _alchemist_level(source),
                "source_ability": "Distilled Id",
            },
        ),
        "is_skill": True,
        "scales_with_level": True,
        "target": "self",
    },

    # Level 20

    {
        "name": "Speed Potion",
        "required_level": 20,
        "type": "skill",
        "cost": 80,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": (
            "Create a basic, potent, or greater speed potion."
        ),
        "effects": create_item(
            factory_fn=lambda source, target: _make_speed_potion_factory("basic")(source, target),
        ),
        "is_skill": True,
        "scales_with_level": True,
        "target": "self",
    },

    {
        "name": "Tranquilizer",
        "required_level": 20,
        "type": "skill",
        "cost": 40,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": (
            "Create a dose of tranquilizer as either a potion or a weapon-applied poison."
        ),
        "effects": create_item(
            factory_fn=lambda source, target: _make_tranquilizer_factory(
                "basic",
                "potion",
            )(source, target),
        ),
        "is_skill": True,
        "scales_with_level": True,
        "target": "self",
    },

    # Level 25

    {
        "name": "Alchemical Experimentation",
        "required_level": 25,
        "type": "passive",
        "duration": "Passive Constant",
        "description": (
            "Experiment to discover new alchemical skills."
        ),
        "effects": passive_modifier(_alchemical_experimentation_modifier),
        "scales_with_level": False,
    },

    {
        "name": "Philosopher's Stone",
        "required_level": 25,
        "type": "skill",
        "cost": 100,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": (
            "Attempt to transmute a reagent into a higher-level reagent."
        ),
        "effects": create_item(
            factory_fn=lambda source, target: _make_upgraded_reagent_factory(1)(source, target),
        ),
        "is_skill": True,
        "scales_with_level": True,
        "target": "self",
    },

    {"grant": "Poison Resistance", "required_level": 25},

], source_type="adventure")