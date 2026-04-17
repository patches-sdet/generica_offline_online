from __future__ import annotations
from dataclasses import dataclass, field
from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    composite,
    heal_hp,
    inspect,
    skill_check,
    summon,
)
from domain.conditions import IS_CONSTRUCT, IS_OBJECT, IN_PARTY, NOT_IN_PARTY
from domain.effects.base import Effect, EffectContext
from domain.effects.special.minions import ScaledNonZeroAttributeBuffEffect

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

def _animator_level(character) -> int:
    return character.get_progression_level("adventure", "Animator", 0)

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name, 0)

def _ensure_party(owner) -> list:
    if not hasattr(owner, "party") or owner.party is None:
        owner.party = []
    return owner.party

def _ensure_bucket(obj, key: str) -> dict:
    if not hasattr(obj, "states") or obj.states is None:
        obj.states = {}
    obj.states.setdefault(key, {})
    return obj.states[key]

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
    return max(1, _ability_level(caster, "Animus")) * 10


def _construct_resist_difficulty(ctx, target) -> int:
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

# Entity factory

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

# Custom effects

class SpendAnimusExtraSanityEffect(Effect):
    """
    Base Animus cost remains 10 sanity in the ability schema.
    This effect spends only the extra amount required by the chosen object.
    """

    def apply(self, context: EffectContext) -> None:
        if not context.targets:
            return

        obj = context.targets[0]
        extra_cost = max(0, _animus_profile(obj)["total_cost"] - 10)
        if extra_cost <= 0:
            return

        ok = context.source.spend_resource("sanity", extra_cost)
        if ok is False:
            raise ValueError("Not enough sanity for Animus extra cost.")

class CommandAnimusEffect(Effect):
    def apply(self, context: EffectContext) -> None:
        if not context.targets:
            return

        target = context.targets[0]
        command = context.get_option(COMMAND_TEXT)
        bucket = _ensure_bucket(target, "command_animus")
        bucket["controller"] = context.source
        bucket["command"] = command
        bucket["source"] = "Command Animus"

class TeachWeaponSkillEffect(Effect):
    def apply(self, context: EffectContext) -> None:
        if not context.targets:
            return

        target = context.targets[0]
        weapon_skill = context.require_option(WEAPON_SKILL)

        owner_level = context.source.get_skill_level(weapon_skill, 0)
        imparted = min(_ability_level(context.source, "Arm Creation"), owner_level)

        bucket = _ensure_bucket(target, "arm_creation_skills")
        bucket[weapon_skill] = imparted

class ActivateDollseyeEffect(Effect):
    def apply(self, context: EffectContext) -> None:
        if not context.targets:
            return

        target = context.targets[0]
        requested_power = context.get_option(DOLLSEYE_POWER)
        eye_index = int(context.get_option(EYE_INDEX, 0))

        max_power = _ability_level(context.source, "Dollseye")
        applied_power = max_power if requested_power is None else min(int(requested_power), max_power)

        bucket = _ensure_bucket(context.source, "dollseye_links")
        bucket[eye_index] = {
            "target": target,
            "power": applied_power,
        }

class MagicMouthEffect(Effect):
    def apply(self, context: EffectContext) -> None:
        if not context.targets:
            return

        target = context.targets[0]
        bucket = _ensure_bucket(target, "magic_mouth")
        bucket["speaker"] = context.source
        bucket["duration_minutes"] = _ability_level(context.source, "Magic Mouth") * 10

class NoDefenseDamageEffect(Effect):
    """
    Placeholder direct-damage effect for rare rules that bypass normal defenses.
    Used for Deanimate until full roll / damage resolution exists.
    """

    def __init__(self, amount_fn, condition=None):
        self.amount_fn = amount_fn
        self.condition = condition

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            if self.condition is not None and not self.condition(context, target):
                continue

            amount = int(self.amount_fn(context.source, target))
            if amount <= 0:
                continue

            target.modify_resource("hp", -amount)

class EnableNextAnimusAtRangeEffect(Effect):
    def apply(self, context: EffectContext) -> None:
        bucket = _ensure_bucket(context.source, "next_animus_at_range")
        bucket["range_feet"] = _animator_level(context.source)
        bucket["source"] = "Distant Animus"

class ActivateDollsbodyEffect(Effect):
    def apply(self, context: EffectContext) -> None:
        if not context.targets:
            return

        target = context.targets[0]
        bucket = _ensure_bucket(context.source, "dollsbody")
        bucket["target"] = target
        bucket["duration_minutes"] = _ability_level(context.source, "Dollsbody")
        bucket["source"] = "Dollsbody"

class EnableAnimusAllEffect(Effect):
    def apply(self, context: EffectContext) -> None:
        bucket = _ensure_bucket(context.source, "animus_all")
        bucket["max_targets"] = 6
        bucket["duration_minutes"] = 1
        bucket["source"] = "Animus All"

class FocusWillEffect(Effect):
    def apply(self, context: EffectContext) -> None:
        if not context.targets:
            return

        target = context.targets[0]
        bucket = _ensure_bucket(context.source, "focus_will")
        bucket["target"] = target
        bucket["bonus"] = _ability_level(context.source, "Focus Will")
        bucket["sanity_per_minute"] = 50
        bucket["source"] = "Focus Will"

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
            "Turns a touched object into an animi, capable of movement, combat, and simple tasks "
            "as ordered by its creator. Must be in its creator's party to do anything beyond defend itself."
        ),
        "effects": composite(
            SpendAnimusExtraSanityEffect(),
            skill_check(
                ability="Animus",
                stat="intelligence",
                difficulty=lambda ctx, target: _animus_profile(target)["difficulty"],
                on_success=summon(
                    factory_fn=lambda source, target: create_animi_from_object(
                        caster=source,
                        obj=target,
                        profile=_animus_profile(target),
                        duration_minutes=_animus_duration_minutes(source),
                    ),
                    condition=IS_OBJECT,
                ),
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
            "Allows the caster to issue one command to an animi not in the creator's party. "
            "On success, the animi follows the command as best it can until impossible."
        ),
        "effects": skill_check(
            ability="Command Animus",
            stat="intelligence",
            difficulty=_construct_resist_difficulty,
            on_success=CommandAnimusEffect(),
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
        "effects": ScaledNonZeroAttributeBuffEffect(
            scale_fn=lambda c: (
                c.get_stat("willpower")
                + c.get_ability_effective_level("Creator's Guardians", 0)
            ) // 10,
            condition=lambda ctx, target: IS_CONSTRUCT(ctx, target) and IN_PARTY(ctx, target),
            source_name="Creator's Guardians",
        ),
    },

    {
        "name": "Eye for Detail",
        "required_level": 1,
        "type": "skill",
        "cost": 5,
        "cost_pool": "sanity",
        "duration": "1 minute",
        "description": (
            "Allows the Animator to examine any animi, golem, construct, or object for animus potential and sanity cost."
        ),
        "effects": skill_check(
            ability="Eye for Detail",
            stat="intelligence",
            difficulty=_construct_resist_difficulty,
            on_success=inspect(
                reveal_fn=lambda ctx, target: {
                    "type": getattr(target, "type", None),
                    "hp": getattr(target, "current_hp", getattr(target, "hp", None)),
                    "attributes": getattr(target, "attributes", None),
                    "animus_potential": _estimate_animus_value(target),
                },
                condition=lambda ctx, target: IS_CONSTRUCT(ctx, target) or IS_OBJECT(ctx, target),
            ),
        ),
        "is_spell": True,
        "scales_with_level": True,
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
            scale_fn=lambda c: (_animator_level(c) + _ability_level(c, "Mend")) // 2,
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
            factory_fn=lambda source, target: create_animi_from_object(
                caster=source,
                obj=target,
                profile={
                    "hp": 50,
                    "strength": source.get_stat("willpower"),
                    "agility": 50,
                    "sanity": 0,
                    "armor": 0,
                    "size": "small",
                    "material": getattr(target, "material", "metal"),
                },
                duration_minutes=_animator_level(source) * 10,
                name=getattr(target, "name", "Animus Blade"),
                extra_tags={"weapon_animi", "flying"},
                states={
                    "source_ability": "Animus Blade",
                    "attack_mode": "melee_slashing",
                    "max_attacks_per_turn": 1,
                    "orbits_creator": True,
                },
            ),
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
            "Teaches an animi a weapon skill that you know, up to this skill's level, "
            "but never above your own skill."
        ),
        "effects": skill_check(
            ability="Arm Creation",
            stat="intelligence",
            difficulty=_construct_resist_difficulty,
            on_success=TeachWeaponSkillEffect(),
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
        "effects": skill_check(
            ability="Dollseye",
            stat="intelligence",
            difficulty=_construct_resist_difficulty,
            on_success=ActivateDollseyeEffect(),
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
            factory_fn=lambda source, target: create_animi_from_object(
                caster=source,
                obj=target,
                profile={
                    "hp": 100,
                    "strength": source.get_stat("willpower"),
                    "agility": 30,
                    "sanity": 0,
                    "armor": getattr(target, "armor", 0),
                    "size": "medium",
                    "material": getattr(target, "material", "metal"),
                },
                duration_minutes=_animator_level(source) * 10,
                name=getattr(target, "name", "Animus Shield"),
                extra_tags={"shield_animi", "flying"},
                states={
                    "source_ability": "Animus Shield",
                    "max_attacks_per_turn": 1,
                    "orbits_creator": True,
                    "granted_skills": {
                        "Shield": _ability_level(source, "Animus Shield"),
                        "Bodyguard": _ability_level(source, "Animus Shield"),
                    },
                },
            ),
            condition=IS_OBJECT,
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "shield",
    },

    {
        "name": "Magic Mouth",
        "required_level": 10,
        "type": "skill",
        "cost": 20,
        "cost_pool": "sanity",
        "duration": "10 minutes per skill level",
        "description": (
            "Allows the animator to speak through one of the animi or constructs currently in their party."
        ),
        "effects": skill_check(
            ability="Magic Mouth",
            stat="intelligence",
            difficulty=_construct_resist_difficulty,
            on_success=MagicMouthEffect(),
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "party_construct",
    },

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
            "Roll Dexterity + Deanimate against the target's agility. Damage equals the margin of "
            "success. Armor and Resist Magic do not reduce this damage. Current implementation keeps "
            "this as a success-gated no-defense damage placeholder until rolls are formalized."
        ),
        "effects": skill_check(
            ability="Deanimate",
            stat="dexterity",
            difficulty=lambda ctx, target: getattr(target, "agility", 0),
            on_success=NoDefenseDamageEffect(
                amount_fn=lambda caster, target: _ability_level(caster, "Deanimate"),
                condition=IS_CONSTRUCT,
            ),
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
        "effects": EnableNextAnimusAtRangeEffect(),
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
            factory_fn=lambda source, target: create_animi_from_object(
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
                duration_minutes=_animator_level(source) * 10,
                name=getattr(target, "name", "Animus Bow"),
                extra_tags={"weapon_animi", "ranged_weapon_animi", "flying"},
                states={
                    "source_ability": "Animus Bow",
                    "attack_mode": "ranged_bow",
                    "max_attacks_per_turn": 1,
                    "orbits_creator": True,
                    "dexterity_override": source.get_stat("willpower"),
                },
            ),
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
        "effects": skill_check(
            ability="Dollsbody",
            stat="intelligence",
            difficulty=_construct_resist_difficulty,
            on_success=ActivateDollsbodyEffect(),
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
        "effects": EnableAnimusAllEffect(),
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
        "effects": skill_check(
            ability="Focus Will",
            stat="willpower",
            difficulty=_construct_resist_difficulty,
            on_success=FocusWillEffect(),
        ),
        "is_spell": True,
        "scales_with_level": True,
        "target": "owned_animi",
    },

], source_type="adventure")