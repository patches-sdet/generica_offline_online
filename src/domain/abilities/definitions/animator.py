from domain.abilities.definitions._job_builder import build_job
from domain.abilities.patterns import (
    heal,
    buff,
    summon,
    control,
    inspect,
    skill_check,
)
from domain.conditions.entity import IS_CONSTRUCT, IS_OBJECT, NOT_IN_PARTY
from domain.effects.base import Effect

# Animus data tables

ANIMUS_SIZE_TABLE = {
    "small": {
        "hp": 50,
        "strength": 20,
        "agility": 50,
        "sanity": 10,
        "cost": 10,
        "difficulty": 80,
    },
    "medium": {
        "hp": 100,
        "strength": 50,
        "agility": 40,
        "sanity": 25,
        "cost": 20,
        "difficulty": 120,
    },
    "large": {
        "hp": 200,
        "strength": 75,
        "agility": 25,
        "sanity": 50,
        "difficulty": 180,
    },
    "enormous": {
        "hp": 300,
        "strength": 100,
        "agility": 10,
        "sanity": 100,
        "cost": 100,
        "difficulty": 250,
    },
}

ANIMUS_MATERIAL_ARMOR = {
    "cloth": 5,
    "soft": 5,
    "leather": 8,
    "flexible": 8,
    "wood": 12,
    "bone": 12,
    "light_hard": 12,
    "pottery": 20,
    "brittle": 20,
    "metal": 25,
}

# Animus helpers

def get_animus_size_key(obj) -> str:
    """
    Resolve the object's animus size category.

    Expected values:
        small, medium, large, enormous
    """
    size = getattr(obj, "animus_size", None) or getattr(obj, "size", None)
    if not size:
        raise ValueError("Object is missing animus size information.")

    size = str(size).strip().lower()
    if size not in ANIMUS_SIZE_TABLE:
        raise ValueError(f"Unsupported animus size: {size}")

    return size


def get_animus_material_key(obj) -> str:
    """
    Resolve the object's animus material category.
    """
    material = getattr(obj, "animus_material", None) or getattr(obj, "material", None)
    if not material:
        raise ValueError("Object is missing animus material information.")

    material = str(material).strip().lower()
    if material not in ANIMUS_MATERIAL_ARMOR:
        raise ValueError(f"Unsupported animus material: {material}")

    return material


def get_object_length_feet(obj) -> int:
    """
    Used for enormous-object extra sanity costs.
    Defaults to 10 if not provided.
    """
    return int(getattr(obj, "length_feet", 10) or 10)


def get_enormous_extra_cost(obj) -> int:
    """
    For enormous objects:
    +50 sanity for every 10 feet beyond the first 10 feet.
    """
    size = get_animus_size_key(obj)
    if size != "enormous":
        return 0

    length_feet = get_object_length_feet(obj)
    extra_feet = max(0, length_feet - 10)

    # Floor division keeps it in 10-foot chunks.
    extra_steps = extra_feet // 10
    return extra_steps * 50


def resolve_animus_profile(obj) -> dict:
    """
    Produce the full derived stat/cost profile for an object to be animated.
    """
    size = get_animus_size_key(obj)
    material = get_animus_material_key(obj)

    base = dict(ANIMUS_SIZE_TABLE[size])
    base["armor"] = ANIMUS_MATERIAL_ARMOR[material]
    base["size"] = size
    base["material"] = material
    base["extra_cost"] = get_enormous_extra_cost(obj)
    base["total_cost"] = base["cost"] + base["extra_cost"]

    return base


def animus_duration(ctx) -> str:
    """
    Human-readable duration text based on Animus ability level.
    """
    level = ctx.source.ability_levels.get("Animus", 0)
    return f"{level * 10} minutes"


def estimate_animus_value(target) -> dict:
    """
    Used by Eye for Detail to preview what Animus would do to an object.
    """
    if not (getattr(target, "animus_size", None) or getattr(target, "size", None)):
        return {"animus_possible": False}

    profile = resolve_animus_profile(target)
    return {
        "animus_possible": True,
        "size": profile["size"],
        "material": profile["material"],
        "hp": profile["hp"],
        "strength": profile["strength"],
        "agility": profile["agility"],
        "sanity": profile["sanity"],
        "armor": profile["armor"],
        "difficulty": profile["difficulty"],
        "sanity_cost": profile["total_cost"],
    }

# Specialized effect: extra sanity cost on Animus attempt

class SpendAnimusExtraSanityEffect(Effect):
    """
    Spend the Animus cost above the base ability cost.

    The schema cost for Animus should remain 10 sanity.
    This effect spends only the extra amount required by the object.
    It is spent on attempt, not only on success.
    """

    def apply(self, context):
        if not context.targets:
            return

        obj = context.targets[0]
        profile = resolve_animus_profile(obj)

        extra_cost = max(0, profile["total_cost"] - 10)
        if extra_cost <= 0:
            return

        # Prefer spend_resource if available, otherwise fall back to modify_resource.
        if hasattr(context.source, "spend_resource"):
            ok = context.source.spend_resource("sanity", extra_cost)
            if ok is False:
                raise ValueError("Not enough Sanity for Animus extra cost.")
        elif hasattr(context.source, "modify_resource"):
            context.source.modify_resource("sanity", -extra_cost)
        else:
            raise AttributeError("Character cannot spend or modify sanity resources.")


def spend_animus_extra_sanity():
    return SpendAnimusExtraSanityEffect()

# Animator Job

build_job("Animator", [

    # Animus
    {
        "name": "Animus",
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "duration": "10 minutes per Animus level",
        "description": "Turns a touched object into an animi, capable of movement, combat, and simple tasks as ordered by its creator. Must be in its creator's party to do anything beyond defend itself. The greater the size and mass of the object, the more it costs to animate, and the more hit points and strength it begins with. The type of material also factors in, and determines the starting armor rating of the animi. The larger the size, the more difficult the roll to animate the object. This skill is a spell, that uses intelligence plus Animus for the roll.",
        "target": "touch",
        "effects": lambda ctx: [
            spend_animus_extra_sanity(),
            skill_check(
                ability="Animus",
                stat="intelligence",
                difficulty=lambda check_ctx, target: resolve_animus_profile(target)["difficulty"],
                on_success=[
                    summon(
                        factory_fn=lambda summon_ctx, obj: create_animi_from_object(
                            caster=summon_ctx.source,
                            obj=obj,
                            profile=resolve_animus_profile(obj),
                            duration_minutes=summon_ctx.source.ability_levels.get("Animus", 0) * 10,
                        ),
                        condition=IS_OBJECT,
                    )
                ],
            ),
        ],
    },

    # Command Animus
    {
        "name": "Command Animus",
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "1 command",
        "description": "Allows the caster to issue one command to an animi not in the creator's party. On a success, the animi will complete the command as best it can. This skill is a spell, and uses Intelligence plus Command Animus for the roll. The difficulty is set by the Animi's Willpower roll.",
        "effects": lambda ctx: [
            skill_check(
                ability="Command Animus",
                stat="intelligence",
                difficulty=lambda check_ctx, target: target.roll_willpower(),
                on_success=[
                    control(
                        duration="1 command",
                        condition=lambda effect_ctx, target: (
                            IS_CONSTRUCT(effect_ctx, target)
                            and NOT_IN_PARTY(effect_ctx.source, target)
                        ),
                    )
                ],
            )
        ],
    },

    # Creator's Guardians
    {
        "name": "Creator's Guardians",
        "type": "passive",
        "description": "Enhances animi in the creator's party, boosting all non-zero attributes. The amount is the creator's Willpower and Creator's Guardians ability level, divided by 10.",
        "effects": lambda ctx: [
            buff(
                scale_fn=lambda c: (
                    c.get_stat("willpower")
                    + c.ability_levels.get("Creator's Guardians", 0)
                ) // 10,
                stats={
                    "strength": 1,
                    "constitution": 1,
                    "dexterity": 1,
                    "agility": 1,
                    "intelligence": 1,
                    "wisdom": 1,
                    "willpower": 1,
                    "perception": 1,
                    "charisma": 1,
                    "luck": 1,
                },
                condition=lambda ctx, target: (
                    IS_CONSTRUCT(ctx, target)
                    and IN_PARTY(ctx.source, target)
                ),
            )
        ],
    },

    # Eye for Detail
    {
        "name": "Eye for Detail",
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "1 minute",
        "description": "Allows the Animator to examine the status of any animi, golem, or other construct. Also used to analyze any object for animus potential and sanity cost. This is accomplished with an Intelligence plus Eye for Detail roll. The object can make a Willpower roll to resist, with Animi or constructs in a party able to use their creator's Willpower. This skill is a spell.",
        "effects": lambda ctx: [
            skill_check(
                ability="Eye for Detail",
                stat="intelligence",
                difficulty=lambda check_ctx, target: target.roll_willpower(),
                on_success=[
                    inspect(
                        reveal_fn=lambda inspect_ctx, target: {
                            "type": getattr(target, "type", None),
                            "hp": getattr(target, "hp", None),
                            "attributes": getattr(target, "attributes", None),
                            "animus_potential": estimate_animus_value(target),
                        },
                        condition=lambda effect_ctx, target: (
                            IS_CONSTRUCT(effect_ctx, target)
                            or IS_OBJECT(effect_ctx, target)
                        ),
                    )
                ],
            )
        ],
    },

    # Mend
    {
    "name": "Mend",
    "type": "skill",
    "cost": 5,
    "cost_pool": "sanity",
    "duration": "1 action",
    "description": "Instantly repair the targeted construct or object, restoring a number of HP equal to the Animator's level plus the Mend ability level, divided by two. This is earth-based healing, and can affect earth elementals, but not other living creatures. This skill is a spell.",
    "effects": lambda ctx: [
        heal(
            scale_fn=lambda c: (
                c.get_progression_level("adventure", "Animator", 0)
                + c.ability_levels.get("Mend", 0)
            ) // 2,
            condition=lambda effect_ctx, target: (
                IS_CONSTRUCT(effect_ctx, target) or IS_OBJECT(effect_ctx, target)
            ),
        )
    ],
},
])