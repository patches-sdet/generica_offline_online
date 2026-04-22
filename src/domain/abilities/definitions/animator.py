from __future__ import annotations
from dataclasses import dataclass, field
from domain.conditions import IS_CONSTRUCT, IS_OBJECT, IN_PARTY
from domain.effects.base import EffectContext
from domain.effects.special.minions import ScaledNonZeroAttributeBuffEffect
from domain.abilities.builders._job_builder import build_job
from domain.abilities import ability_level, progression_level
from domain.abilities.patterns import (
    apply_state,
    composite,
    heal_hp,
    inspect,
    summon,
)

# Local metadata keys

COMMAND_TEXT = "command"
WEAPON_SKILL = "weapon_skill"
DOLLSEYE_POWER = "dollseye_power"
EYE_INDEX = "eye_index"

# Animus reference tables

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
        "cost": 50,
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

# Runtime animi entity

@dataclass(slots=True)
class Animi:
    name: str
    creator: object
    source_object: object

    type: str = "construct"
    attributes: dict[str, int] = field(default_factory=dict)

    current_hp: int = 0
    max_hp: int = 0
    current_sanity: int = 0
    max_sanity: int = 0
    current_stamina: int = 0
    max_stamina: int = 0
    current_moxie: int = 0
    max_moxie: int = 0
    current_fortune: int = 0
    max_fortune: int = 0

    armor: int = 0
    animus_size: str = "small"
    animus_material: str = "wood"
    duration_minutes: int = 0

    tags: set[str] = field(default_factory=set)
    states: dict = field(default_factory=dict)

    skill_levels: dict[str, int] = field(default_factory=dict)
    ability_levels: dict[str, int] = field(default_factory=dict)

    def add_stat(self, stat: str, value: int, source: str | None = None) -> None:
        self.attributes[stat] = self.attributes.get(stat, 0) + value

    def get_stat(self, stat: str, default: int = 0) -> int:
        return self.attributes.get(stat, default)

    def get_skill_level(self, skill_name: str, default: int = 0) -> int:
        return self.skill_levels.get(skill_name, default)

    def roll_willpower(self, *_args) -> int:
        return self.get_stat("willpower", 0)

    def modify_resource(self, pool: str, amount: int) -> bool:
        attr = f"current_{pool}"
        if not hasattr(self, attr):
            raise ValueError(f"Invalid resource pool: {pool}")

        current = getattr(self, attr)
        new_value = current + amount
        if new_value < 0:
            return False

        max_attr = f"max_{pool}"
        max_value = getattr(self, max_attr, 0)
        if max_value > 0:
            new_value = min(new_value, max_value)

        setattr(self, attr, new_value)
        return True

    def spend_resource(self, pool: str, amount: int) -> bool:
        return self.modify_resource(pool, -amount)

# Rule helpers

def _ensure_party(owner) -> list:
    if not hasattr(owner, "party") or owner.party is None:
        owner.party = []
    return owner.party

def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states

def _size_key(obj) -> str:
    size = getattr(obj, "animus_size", None) or getattr(obj, "size", None)
    if not size:
        raise ValueError("Object is missing animus size information.")

    size = str(size).strip().lower()
    if size not in ANIMUS_SIZE_TABLE:
        raise ValueError(f"Unsupported animus size: {size}")

    return size

def _material_key(obj) -> str:
    material = getattr(obj, "animus_material", None) or getattr(obj, "material", None)
    if not material:
        raise ValueError("Object is missing animus material information.")

    material = str(material).strip().lower()
    if material not in ANIMUS_MATERIAL_ARMOR:
        raise ValueError(f"Unsupported animus material: {material}")

    return material

def _length_feet(obj) -> int:
    return int(getattr(obj, "length_feet", 10) or 10)

def _enormous_extra_cost(obj) -> int:
    if _size_key(obj) != "enormous":
        return 0

    extra_feet = max(0, _length_feet(obj) - 10)
    return (extra_feet // 10) * 50

def _animus_profile(obj) -> dict:
    size = _size_key(obj)
    material = _material_key(obj)

    base = dict(ANIMUS_SIZE_TABLE[size])
    base["armor"] = ANIMUS_MATERIAL_ARMOR[material]
    base["size"] = size
    base["material"] = material
    base["extra_cost"] = _enormous_extra_cost(obj)
    base["total_cost"] = base["cost"] + base["extra_cost"]
    return base

def _animus_duration_minutes(caster) -> int:
    return max(1, ability_level(caster, "Animus")) * 10

def _construct_resist_difficulty(source, target) -> int:
    creator = getattr(target, "creator", None)
    if creator is not None and target in getattr(creator, "party", []):
        roll_fn = getattr(creator, "roll_willpower", None)
        if callable(roll_fn):
            return roll_fn()

    roll_fn = getattr(target, "roll_willpower", None)
    if callable(roll_fn):
        return roll_fn()

    return getattr(target, "willpower", 0)

def _estimate_animus_value(target) -> dict:
    try:
        profile = _animus_profile(target)
    except Exception:
        return {"animus_possible": False}

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

# Entity factory helpers

def create_animi_from_object(
    caster,
    obj,
    profile: dict,
    duration_minutes: int,
    *,
    name: str | None = None,
    extra_tags: set[str] | None = None,
    states: dict | None = None,
    skill_levels: dict | None = None,
    ability_levels: dict | None = None,
):
    tags = {"construct", "animi", "summon"}
    if extra_tags:
        tags |= set(extra_tags)

    payload = {
        "source_ability": "Animus",
        "duration_minutes": duration_minutes,
        "obeys_creator_only": True,
        "can_act_freely_outside_party": False,
    }
    if states:
        payload.update(states)

    animi = Animi(
        name=name or getattr(obj, "name", "Animated Object"),
        creator=caster,
        source_object=obj,
        attributes={
            "strength": profile["strength"],
            "constitution": 0,
            "dexterity": 0,
            "agility": profile["agility"],
            "intelligence": 0,
            "wisdom": 0,
            "willpower": 0,
            "perception": 0,
            "charisma": 0,
            "luck": 0,
        },
        current_hp=profile["hp"],
        max_hp=profile["hp"],
        current_sanity=profile["sanity"],
        max_sanity=profile["sanity"],
        armor=profile["armor"],
        animus_size=profile["size"],
        animus_material=profile["material"],
        duration_minutes=duration_minutes,
        tags=tags,
        states=payload,
        skill_levels=dict(skill_levels or {}),
        ability_levels=dict(ability_levels or {}),
    )

    party = _ensure_party(caster)
    if animi not in party:
        party.append(animi)

    return animi

def _animus_factory(source, target):
    if target is None:
        raise ValueError("Animus requires a target object.")

    profile = _animus_profile(target)
    return create_animi_from_object(
        caster=source,
        obj=target,
        profile=profile,
        duration_minutes=_animus_duration_minutes(source),
    )

def _animus_blade_factory(source, target):
    if target is None:
        raise ValueError("Animus Blade requires a weapon target.")

    return create_animi_from_object(
        caster=source,
        obj=target,
        profile={
            "hp": 50,
            "strength": source.get_stat("willpower", 0),
            "agility": 50,
            "sanity": 0,
            "armor": 0,
            "size": "small",
            "material": getattr(target, "material", "metal"),
        },
        duration_minutes=progression_level(source, "adventure", "Animator") * 10,
        name=getattr(target, "name", "Animus Blade"),
        extra_tags={"weapon_animi", "flying"},
        states={
            "source_ability": "Animus Blade",
            "attack_mode": "melee_slashing",
            "max_attacks_per_turn": 1,
            "orbits_creator": True,
        },
    )

def _animus_shield_factory(source, target):
    if target is None:
        raise ValueError("Animus Shield requires a shield target.")

    return create_animi_from_object(
        caster=source,
        obj=target,
        profile={
            "hp": 100,
            "strength": source.get_stat("willpower", 0),
            "agility": 30,
            "sanity": 0,
            "armor": getattr(target, "armor", 0),
            "size": "medium",
            "material": getattr(target, "material", "metal"),
        },
        duration_minutes=progression_level(source, "adventure", "Animator") * 10,
        name=getattr(target, "name", "Animus Shield"),
        extra_tags={"shield_animi", "flying"},
        states={
            "source_ability": "Animus Shield",
            "max_attacks_per_turn": 1,
            "orbits_creator": True,
            "granted_skills": {
                "Shield": ability_level(source, "Animus Shield"),
                "Bodyguard": ability_level(source, "Animus Shield"),
            },
        },
    )

def _animus_bow_factory(source, target):
    if target is None:
        raise ValueError("Animus Bow requires a bow or crossbow target.")

    return create_animi_from_object(
        caster=source,
        obj=target,
        profile={
            "hp": 50,
            "strength": 0,
            "agility": 50,
            "sanity": 0,
            "armor": 0,
            "size": "small",
            "material": getattr(target, "material", "wood"),
        },
        duration_minutes=progression_level(source, "adventure", "Animator") * 10,
        name=getattr(target, "name", "Animus Bow"),
        extra_tags={"weapon_animi", "ranged_weapon_animi", "flying"},
        states={
            "source_ability": "Animus Bow",
            "attack_mode": "ranged_bow",
            "max_attacks_per_turn": 1,
            "orbits_creator": True,
            "dexterity_override": source.get_stat("willpower", 0),
        },
    )

# Passive effect helper

def _creators_guardians_effect(ctx: EffectContext):
    return ScaledNonZeroAttributeBuffEffect(
        scale_fn=lambda c: (
            c.get_stat("willpower", 0)
            + ability_level(c, "Creator's Guardians")
        ) // 10,
        condition=lambda inner_ctx, target: IS_CONSTRUCT(inner_ctx, target) and IN_PARTY(inner_ctx, target),
        source_name="Creator's Guardians",
    )

# Job definition

build_job("Animator", [

    # Level 1

    {
        "name": "Animus",
        "required_level": 1,
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "duration": "10 minutes per Animus level",
        "description": (
            "Turn a touched object into an animi, capable of movement, combat, and simple tasks "
            "as ordered by its creator. Must be in its creator's party to do anything beyond defend itself."
        ),
        "effects": composite(
            apply_state(
                "animus_cast",
                value_fn=lambda source: {
                    "active": True,
                    "requires_object_target": True,
                    "animus_duration_minutes": _animus_duration_minutes(source),
                    "difficulty_from_target_profile": True,
                    "extra_sanity_cost_from_target_profile": True,
                    "source_ability": "Animus",
                },
            ),
            summon(
                factory_fn=_animus_factory,
                condition=IS_OBJECT,
            ),
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "touch",
    },

    {
        "name": "Command Animus",
        "required_level": 1,
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "Until no longer possible",
        "description": (
            "Issue one command to an animi not in the creator's party. On success, it follows the command "
            "as best it can until impossible."
        ),
        "effects": apply_state(
            "command_animus_active",
            value_fn=lambda source: {
                "active": True,
                "contest": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Command Animus",
                    "target_difficulty": "construct_resist_difficulty",
                },
                "stores_command_text_from_context": True,
                "controller": source,
                "source_ability": "Command Animus",
            },
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "animus",
    },

    {
        "name": "Creator's Guardians",
        "required_level": 1,
        "type": "passive",
        "duration": "Passive Constant",
        "description": (
            "Enhances animi in the creator's party, boosting all non-zero attributes."
        ),
        "effects": _creators_guardians_effect,
        "scales_with_level": True,
        "target": "party",
    },

    {
        "name": "Eye for Detail",
        "required_level": 1,
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "1 minute",
        "description": (
            "Examine an animi, golem, construct, or object for animus potential and sanity cost."
        ),
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "eye_for_detail",
                "valid_targets": ("construct", "object"),
                "check": {
                    "stat": "intelligence",
                    "skill": "Eye for Detail",
                    "difficulty": "construct_resist_difficulty",
                },
                "reveals": {
                    "type": True,
                    "hp": True,
                    "attributes": True,
                    "animus_potential": True,
                },
                "source_ability": "Eye for Detail",
            },
        ),
        "is_spell": True,
        "scales_with_level": False,
        "target": "animus_or_object",
    },

    {
        "name": "Mend",
        "required_level": 1,
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "1 action",
        "description": (
            "Instantly repairs the target construct or object, restoring HP equal to "
            "(Animator level + Mend level) // 2."
        ),
        "effects": heal_hp(
            scale_fn=lambda c: (progression_level(c, "adventure", "Animator") + ability_level(c, "Mend")) // 2,
            condition=lambda ctx, target: IS_CONSTRUCT(ctx, target) or IS_OBJECT(ctx, target),
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "animus_or_object",
    },

    # Level 5

    {
        "name": "Animus Blade",
        "required_level": 5,
        "type": "skill",
        "cost": 15,
        "cost_pool": "sanity",
        "duration": "10 minutes per Animator level",
        "description": (
            "Animates a slashing weapon and grants it minor flight, causing it to move and attack on its own."
        ),
        "effects": summon(
            factory_fn=_animus_blade_factory,
            condition=IS_OBJECT,
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "weapon",
    },

    {
        "name": "Arm Creation",
        "required_level": 5,
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": (
            "Teach an animi a weapon skill that you know, up to this skill's level, but never above your own skill."
        ),
        "effects": apply_state(
            "arm_creation_active",
            value_fn=lambda source: {
                "active": True,
                "contest": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Arm Creation",
                    "target_difficulty": "construct_resist_difficulty",
                },
                "stores_weapon_skill_from_context": True,
                "teaches_up_to_arm_creation_level": True,
                "never_above_creator_skill": True,
                "source_ability": "Arm Creation",
            },
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "animi",
    },

    {
        "name": "Dollseye",
        "required_level": 5,
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "Permanent",
        "description": (
            "Allows the animator to see through one of their animi. The caster may choose to use less than full skill power."
        ),
        "effects": apply_state(
            "dollseye_active",
            value_fn=lambda source: {
                "active": True,
                "contest": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Dollseye",
                    "target_difficulty": "construct_resist_difficulty",
                },
                "stores_eye_index_from_context": True,
                "stores_requested_power_from_context": True,
                "max_power": ability_level(source, "Dollseye"),
                "source_ability": "Dollseye",
            },
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "owned_animi",
    },

    # Level 10

    {
        "name": "Animus Shield",
        "required_level": 10,
        "type": "skill",
        "cost": 20,
        "cost_pool": "sanity",
        "duration": "10 minutes per Animator level",
        "description": (
            "Animates a shield that moves as if wielded by an invisible warrior. "
            "It gains Shield and Bodyguard at the level of this skill."
        ),
        "effects": summon(
            factory_fn=_animus_shield_factory,
            condition=IS_OBJECT,
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "shield",
    },

    {"grant": "Magic Mouth", "required_level": 10},

    # Level 15

    {
        "name": "Deanimate",
        "required_level": 15,
        "type": "skill",
        "cost": 50,
        "cost_pool": "sanity",
        "duration": "1 attack",
        "description": (
            "A ray that inflicts damage on an animus, construct, golem, or other animated object. "
            "Armor and Resist Magic do not reduce this damage."
        ),
        "effects": apply_state(
            "deanimate_active",
            value_fn=lambda source: {
                "active": True,
                "attack_stat": "dexterity",
                "attack_skill": "Deanimate",
                "target_stat": "agility",
                "damage_pool": "hp",
                "damage_amount": "margin_of_success",
                "bypasses_armor": True,
                "bypasses_resist_magic": True,
                "valid_targets": ("construct", "animated_object", "golem", "animi"),
                "source_ability": "Deanimate",
            },
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "construct",
    },

    {
        "name": "Distant Animus",
        "required_level": 15,
        "type": "skill",
        "cost": 50,
        "cost_pool": "sanity",
        "duration": "1 action",
        "description": (
            "The next Animus spell the Animator casts animates an object at range instead of touch."
        ),
        "effects": apply_state(
            "distant_animus_ready",
            value_fn=lambda source: {
                "active": True,
                "applies_to_next_animus": True,
                "range_feet": progression_level(source, "adventure", "Animator"),
                "source_ability": "Distant Animus",
            },
        ),
        "is_spell": True,
        "scales_with_level": False,
        "target": "self",
    },

    # Level 20

    {
        "name": "Animus Bow",
        "required_level": 20,
        "type": "skill",
        "cost": 75,
        "cost_pool": "sanity",
        "duration": "10 minutes per Animator level",
        "description": (
            "Animates a bow or crossbow and grants it minor flight, causing it to move and attack on its own."
        ),
        "effects": summon(
            factory_fn=_animus_bow_factory,
            condition=IS_OBJECT,
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "bow_or_crossbow",
    },

    {
        "name": "Dollsbody",
        "required_level": 20,
        "type": "skill",
        "cost": 100,
        "cost_pool": "sanity",
        "duration": "1 minute per skill level",
        "description": (
            "Moves the animator's consciousness out of their body and temporarily into an animi."
        ),
        "effects": apply_state(
            "dollsbody_active",
            value_fn=lambda source: {
                "active": True,
                "contest": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Dollsbody",
                    "target_difficulty": "construct_resist_difficulty",
                },
                "duration_minutes": ability_level(source, "Dollsbody"),
                "moves_consciousness_into_target_animi": True,
                "source_ability": "Dollsbody",
            },
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "owned_animi",
    },

    # Level 25

    {
        "name": "Animus All",
        "required_level": 25,
        "type": "skill",
        "cost": 100,
        "cost_pool": "sanity",
        "duration": "1 minute",
        "description": (
            "The next Animus spell the Animator casts animates up to six objects simultaneously."
        ),
        "effects": apply_state(
            "animus_all_ready",
            value_fn=lambda source: {
                "active": True,
                "applies_to_next_animus": True,
                "max_targets": 6,
                "duration_minutes": 1,
                "source_ability": "Animus All",
            },
        ),
        "is_spell": True,
        "scales_with_level": False,
        "target": "self",
    },

    {
        "name": "Focus Will",
        "required_level": 25,
        "type": "skill",
        "cost": 50,
        "cost_pool": "sanity",
        "duration": "Until concentration is broken",
        "description": (
            "The animator focuses their will on a single animus, supercharging it while the rest deanimate."
        ),
        "effects": apply_state(
            "focus_will_active",
            value_fn=lambda source: {
                "active": True,
                "contest": {
                    "caster_stat": "willpower",
                    "caster_skill": "Focus Will",
                    "target_difficulty": "construct_resist_difficulty",
                },
                "bonus": ability_level(source, "Focus Will"),
                "sanity_per_minute": 50,
                "all_other_animi_deanimate": True,
                "source_ability": "Focus Will",
            },
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "owned_animi",
    },

], source_type="adventure")