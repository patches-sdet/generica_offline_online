from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    DifficultyTable,
    apply_state,
    create_item,
    hp_damage,
    inspect,
    skill_check,
)
from domain.conditions import IS_ENEMY

# Local metadata keys

PRODUCT_TYPE = "product_type"                  # "reagent" | "crystal"
TIER = "tier"                                  # "basic" | "potent" | "greater"
BOOSTER_STAT = "booster_stat"                  # e.g. "strength"
TARGET_POISON_DIFFICULTY = "target_poison_difficulty"
TARGET_DISEASE_DIFFICULTY = "target_disease_difficulty"
TRANQUILIZER_TIER = "tranquilizer_tier"        # "basic" | "heavy"
TRANQUILIZER_FORM = "tranquilizer_form"        # "potion" | "poison"
COLOR_STEPS = "color_steps"                    # int >= 1
EXTRA_SILVER = "extra_silver"                  # optional crafting bonus
SUBSTANCE_DIFFICULTY = "substance_difficulty"
SUBSTANCE_RARITY = "substance_rarity"
SUBSTANCE_PROPERTIES = "substance_properties"
SUBSTANCE_ALCHEMY_VALUE = "substance_alchemy_value"

# Difficulty tables

POTION_DIFFICULTIES = DifficultyTable({
    "basic": 100,
    "potent": 200,
    "greater": 300,
})

DISTILL_I_DIFFICULTIES = DifficultyTable({
    "reagent": 80,
    "crystal": 120,
})

DISTILL_II_DIFFICULTIES = DifficultyTable({
    "reagent": 120,
    "crystal": 180,
})

ATTRIBUTE_BOOSTER_DIFFICULTIES = DifficultyTable({
    "basic": 150,
    "potent": 250,
    "greater": 350,
})

SPEED_POTION_DIFFICULTIES = DifficultyTable({
    "basic": 200,
    "potent": 300,
    "greater": 400,
})

TRANQUILIZER_DIFFICULTIES = DifficultyTable({
    "basic": 180,
    "heavy": 280,
})

# Rule helpers

def _alchemist_level(character) -> int:
    return character.get_progression_level("adventure", "Alchemist", 0)


def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name, 0)


def _target_agility_difficulty(ctx, target) -> int:
    if hasattr(target, "roll_agility"):
        return target.roll_agility()
    return getattr(getattr(target, "attributes", None), "agility", 0)


def _substance_difficulty(ctx, _target) -> int:
    return int(ctx.require_option(SUBSTANCE_DIFFICULTY))


def _poison_or_disease_difficulty(ctx, _target) -> int:
    poison = ctx.get_option(TARGET_POISON_DIFFICULTY)
    disease = ctx.get_option(TARGET_DISEASE_DIFFICULTY)

    if poison is not None and disease is not None:
        return max(int(poison), int(disease))
    if poison is not None:
        return int(poison)
    if disease is not None:
        return int(disease)

    raise ValueError(
        "Universal Antidote requires target_poison_difficulty "
        "or target_disease_difficulty in context metadata"
    )


def _philosophers_stone_difficulty(ctx, _target) -> int:
    color_steps = max(1, int(ctx.get_option(COLOR_STEPS, 1)))
    return 180 + ((color_steps - 1) * 100)

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

build_job("Alchemist", [

    # Level 1

    {
        "name": "Analyze",
        "required_level": 1,
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "10 seconds",
        "description": (
            "Determine the properties of a studied liquid, powder, crystal, or reagent. "
            "Roll Intelligence + Analyze against the difficulty of the substance. "
            "Failure reveals nothing that day."
        ),
        "effects": skill_check(
            ability="Analyze",
            stat="intelligence",
            difficulty=_substance_difficulty,
            on_success=inspect(
                reveal_fn=lambda ctx, target: {
                    "properties": getattr(
                        target,
                        "properties",
                        ctx.get_option(SUBSTANCE_PROPERTIES),
                    ),
                    "rarity": getattr(
                        target,
                        "rarity",
                        ctx.get_option(SUBSTANCE_RARITY),
                    ),
                    "alchemy_value": getattr(
                        target,
                        "alchemy_value",
                        ctx.get_option(SUBSTANCE_ALCHEMY_VALUE),
                    ),
                }
            ),
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
        "duration": "1 attack",
        "description": (
            "Throw an improvised bomb. Roll Dexterity + Bomb against the target's agility. "
            "The bomb is treated as a weapon with a damage boost equal to Alchemist level, "
            "and also damages nearby foes. Current implementation models the level-scaled "
            "damage effect; splash-shape and weapon-boost details remain runtime-facing."
        ),
        "effects": skill_check(
            ability="Bomb",
            stat="dexterity",
            difficulty=_target_agility_difficulty,
            on_success=hp_damage(
                scale_fn=_alchemist_level,
                condition=IS_ENEMY,
            ),
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
            "Turn valuable substances into red reagents or level 1 crystals. "
            "Reagent difficulty 80, crystal difficulty 120. Components are consumed either way. "
            "Extra material can improve the odds, but that remains descriptive metadata here."
        ),
        "effects": skill_check(
            ability="Distill",
            stat="intelligence",
            difficulty=lambda ctx, target: DISTILL_I_DIFFICULTIES[
                ctx.require_option(PRODUCT_TYPE)
            ],
            on_success=create_item(
                factory_fn=lambda source, target: _make_distilled_material_factory(
                    source.get_option(PRODUCT_TYPE) if hasattr(source, "get_option") else "reagent",
                    tier="level_1",
                )(source, target),
            ),
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
            "Create a basic, potent, or greater healing potion. "
            "Difficulty is 100 / 200 / 300 by tier. Reagent substitutions and critical "
            "double-batch remain represented by metadata/description rather than hard runtime rules."
        ),
        "effects": skill_check(
            ability="Healing Potion",
            stat="intelligence",
            difficulty=lambda ctx, target: POTION_DIFFICULTIES[
                ctx.get_option(TIER, "basic")
            ],
            on_success=create_item(
                factory_fn=lambda source, target: _make_healing_potion_factory("basic")(source, target),
            ),
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
            "Create a basic, potent, or greater mana potion. "
            "Difficulty is 100 / 200 / 300 by tier. Reagent substitutions and critical "
            "double-batch remain represented by metadata/description rather than hard runtime rules."
        ),
        "effects": skill_check(
            ability="Mana Potion",
            stat="intelligence",
            difficulty=lambda ctx, target: POTION_DIFFICULTIES[
                ctx.get_option(TIER, "basic")
            ],
            on_success=create_item(
                factory_fn=lambda source, target: _make_mana_potion_factory("basic")(source, target),
            ),
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
            "Create a basic, potent, or greater attribute booster of a chosen type. "
            "Difficulty is 150 / 250 / 350. Critical double-batch remains descriptive for now."
        ),
        "effects": skill_check(
            ability="Attribute Booster",
            stat="intelligence",
            difficulty=lambda ctx, target: ATTRIBUTE_BOOSTER_DIFFICULTIES[
                ctx.get_option(TIER, "basic")
            ],
            on_success=create_item(
                factory_fn=lambda source, target: _make_attribute_booster_factory(
                    "basic",
                    "strength",
                )(source, target),
            ),
        ),
        "is_skill": True,
        "scales_with_level": False,
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
            "Fall prone without spending an action. While prone, reduce chemical or elemental "
            "damage by Duck and Cover skill level. The prone state is modeled here; the special "
            "damage-reduction and experience-roll behavior remain runtime TODOs."
        ),
        "effects": apply_state("prone"),
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
        "duration": "1 dosage",
        "description": (
            "Examine a poisoned or diseased subject for one minute, then create a cure for that "
            "target alone. Difficulty equals the poison or disease difficulty."
        ),
        "effects": skill_check(
            ability="Universal Antidote",
            stat="intelligence",
            difficulty=_poison_or_disease_difficulty,
            on_success=create_item(
                factory_fn=_make_universal_antidote_factory(),
            ),
        ),
        "is_skill": True,
        "scales_with_level": False,
        "target": "ally",
    },

    # Level 10

    {
        "name": "Geek Fire",
        "required_level": 10,
        "type": "skill",
        "cost": 20,
        "cost_pool": "stamina",
        "duration": "1 attack",
        "description": (
            "Throw improvised napalm. Roll Dexterity + Geek Fire against the target's agility. "
            "Damage is level-scaled fire damage and conceptually ignores conventional armor. "
            "Critical-burning behavior is left as a runtime TODO."
        ),
        "effects": skill_check(
            ability="Geek Fire",
            stat="dexterity",
            difficulty=_target_agility_difficulty,
            on_success=hp_damage(
                scale_fn=_alchemist_level,
                condition=IS_ENEMY,
            ),
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
            "Choose one enhancement whenever consuming a potion: double duration, double one "
            "numerical value, or delay the reaction up to Alchemist level minutes. "
            "Modeled as a passive placeholder until potion-consumption hooks are formalized."
        ),
        "effects": lambda ctx: [],
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
            "Turn valuable substances into orange reagents or level 2 crystals. "
            "Reagent difficulty 120, crystal difficulty 180. Extra material improves the odds "
            "at +1 per five silver worth spent."
        ),
        "effects": skill_check(
            ability="Distill II",
            stat="intelligence",
            difficulty=lambda ctx, target: DISTILL_II_DIFFICULTIES[
                ctx.require_option(PRODUCT_TYPE)
            ],
            on_success=create_item(
                factory_fn=lambda source, target: _make_distilled_material_factory(
                    source.get_option(PRODUCT_TYPE) if hasattr(source, "get_option") else "reagent",
                    tier="level_2",
                )(source, target),
            ),
        ),
        "is_skill": True,
        "scales_with_level": False,
        "target": "self",
    },

    {
        "name": "Distilled Id",
        "required_level": 15,
        "type": "skill",
        "cost": 50,
        "cost_pool": "stamina",
        "duration": "1 turn per alchemist level",
        "description": (
            "Drink a volatile concoction to gain access to Rage at a level equal to Distilled Id, "
            "or buff existing Rage if already known. This is modeled as a stateful placeholder "
            "until temporary borrowed-skill support is formalized."
        ),
        "effects": apply_state(
            "distilled_id_active",
            value_fn=lambda source: {
                "rage_proxy_level": _ability_level(source, "Distilled Id"),
                "duration_turns": _alchemist_level(source),
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
            "Create a basic, potent, or greater speed potion. Difficulty is 200 / 300 / 400. "
            "Basic uses 1 red reagent, potent uses 2, greater uses 3. Critical double-batch "
            "remains descriptive for now."
        ),
        "effects": skill_check(
            ability="Speed Potion",
            stat="intelligence",
            difficulty=lambda ctx, target: SPEED_POTION_DIFFICULTIES[
                ctx.get_option(TIER, "basic")
            ],
            on_success=create_item(
                factory_fn=lambda source, target: _make_speed_potion_factory("basic")(source, target),
            ),
        ),
        "is_skill": True,
        "scales_with_level": False,
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
            "Create a dose of tranquilizer as either a potion or a weapon-applied poison. "
            "Basic difficulty is 180 with a level 1 crystal; heavy-duty is 280 with a level 2 crystal. "
            "Critical double-batch remains descriptive for now."
        ),
        "effects": skill_check(
            ability="Tranquilizer",
            stat="intelligence",
            difficulty=lambda ctx, target: TRANQUILIZER_DIFFICULTIES[
                ctx.get_option(TRANQUILIZER_TIER, "basic")
            ],
            on_success=create_item(
                factory_fn=lambda source, target: _make_tranquilizer_factory(
                    "basic",
                    "potion",
                )(source, target),
            ),
        ),
        "is_skill": True,
        "scales_with_level": False,
        "target": "self",
    },

    # Level 25

    {
        "name": "Alchemical Experimentation",
        "required_level": 25,
        "type": "passive",
        "duration": "N/A",
        "description": (
            "Experiment to discover new alchemical skills. Number of experimental skills usable "
            "at once equals Alchemist level divided by ten; extras must be stored in journals. "
            "Modeled as a passive placeholder until experimentation/equipment systems are formalized."
        ),
        "effects": lambda ctx: [],
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
            "Attempt to transmute a reagent into a higher-level reagent. "
            "Base difficulty is 180, plus 100 for each additional color step beyond the first. "
            "Requires six hours of uninterrupted work and consumes materials regardless of success."
        ),
        "effects": skill_check(
            ability="Philosopher's Stone",
            stat="intelligence",
            difficulty=_philosophers_stone_difficulty,
            on_success=create_item(
                factory_fn=lambda source, target: _make_upgraded_reagent_factory(1)(source, target),
            ),
        ),
        "is_skill": True,
        "scales_with_level": False,
        "target": "self",
    },

    {"grant": "Poison Resistance", "required_level": 25,},

], source_type="adventure")