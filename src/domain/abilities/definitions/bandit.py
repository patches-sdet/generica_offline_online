from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    inspect,
    modify_next_attack,
    passive_modifier,
    skill_check,
)
from domain.conditions import IS_ALLY, tagged
from domain.effects.base import Effect, EffectContext
from domain.effects.special.roll import RollModifierEffect
from domain.effects.stat_effects import DerivedStatBonus

# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.ability_levels.get(ability_name, 0)


def _bandit_level(character) -> int:
    return character.get_progression_level("adventure", "Bandit", 0)


def _highest_job_level(entity) -> int:
    progressions = getattr(entity, "progressions", {}) or {}
    best = 0
    for (_, ptype_name), progression in progressions.items():
        ptype = ptype_name
        # defensive in case keys are shaped differently elsewhere
        if isinstance(ptype_name, tuple):
            ptype = ptype_name[0]
        if getattr(progression, "type", None) in {"adventure", "profession", "advanced"}:
            best = max(best, progression.level)
    return best


def bastard_is_eligible(ctx, target) -> bool:
    """
    Interprets 'job level higher than the Bandit' as:
    target's highest job level (adventure/profession/advanced)
    may not exceed the source Bandit's level.
    """
    return _highest_job_level(target) <= _bandit_level(ctx.source)


def evaluate_ambush_site(ctx, target) -> str:
    """
    Lightweight inspection helper for Lay of the Land.
    """
    if hasattr(target, "ambush_quality"):
        return getattr(target, "ambush_quality")

    terrain = getattr(target, "terrain_type", None)
    if terrain in {"forest", "jungle", "ruins"}:
        return "good"
    if terrain in {"plains", "road"}:
        return "poor"
    return "unknown"


def get_terrain_advantages(ctx, target) -> list[str]:
    """
    Lightweight inspection helper for Lay of the Land.
    """
    advantages: list[str] = []

    if getattr(target, "has_cover", False):
        advantages.append("cover")
    if getattr(target, "has_high_ground", False):
        advantages.append("high ground")
    if getattr(target, "has_chokepoint", False):
        advantages.append("chokepoint")
    if getattr(target, "concealment", False):
        advantages.append("concealment")

    return advantages


def _lay_of_the_land_difficulty(ctx, target) -> int:
    if hasattr(target, "difficulty"):
        return int(target.difficulty)
    return int(ctx.get_option("site_difficulty", 120))


def _ensure_tags(target) -> set:
    tags = getattr(target, "tags", None)
    if tags is None:
        tags = set()
        setattr(target, "tags", tags)
    return tags


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


def _set_attack_attr(attack, key: str, value) -> None:
    setattr(attack, key, value)

# Attack modifier helpers

def _dirty_trick_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "target_stat", "perception")
    _set_attack_attr(attack, "bonus_damage", _ability_level(ctx.source, "Dirty Trick"))
    _set_attack_attr(attack, "dirty_trick", True)

# Passive modifier helpers

def _gang_up_modifier(ctx) -> None:
    """
    Runtime-facing passive hook:
    doubles the normal outnumbering bonus.
    """
    if hasattr(ctx, "modify_outnumber_bonus"):
        ctx.modify_outnumber_bonus(multiplier=2)
        return

    if hasattr(ctx.source, "states"):
        ctx.source.states["gang_up_active"] = True

# Custom effects

class ApplyBastardStatusEffect(Effect):
    """
    Marks targets as bastards and records the source Bandit's authority.
    Long-duration buff details are stored as state placeholders rather than
    pretending duration enforcement already exists.
    """

    def apply(self, context: EffectContext) -> None:
        bonus = _ability_level(context.source, "Band O' Bastards")

        for target in context.targets:
            tags = _ensure_tags(target)
            tags.add("bastard")

            states = _ensure_states(target)
            states["bastard_status"] = {
                "controller": context.source,
                "duration_days": 1,
                "eligible_for_bastard_buffs": bastard_is_eligible(context, target),
                "hp_bonus": bonus if bastard_is_eligible(context, target) else 0,
                "source_ability": "Band O' Bastards",
            }


class HogtieEffect(Effect):
    """
    Runtime-facing placeholder for hogtying helpless targets.
    Stores the intended escape challenge structure until full roll handling exists.
    """

    def apply(self, context: EffectContext) -> None:
        duration_turns = _ability_level(context.source, "Hogtie") * 10

        for target in context.targets:
            states = _ensure_states(target)
            states["hogtied"] = {
                "controller": context.source,
                "duration_turns": duration_turns,
                "escape_roll": {
                    "stat": "strength",
                    "ability": "Hogtie",
                    "source": context.source,
                },
                "notify_if_removed": True,
                "source_ability": "Hogtie",
            }


class PromoteBastardEffect(Effect):
    """
    Promotes a bastard to lieutenant status.
    Buff is stored as explicit state so later runtime / sheet logic can inspect it.
    """

    def apply(self, context: EffectContext) -> None:
        for target in context.targets:
            tags = _ensure_tags(target)
            if "bastard" not in tags:
                continue

            states = _ensure_states(target)
            states["lieutenant_status"] = {
                "controller": context.source,
                "duration_days": 1,
                "attribute_bonus": _bandit_level(context.source),
                "substitute_keep_the_boys_in_line": _ability_level(context.source, "Keep the Boys in Line"),
                "breaks_on_betrayal": True,
                "source_ability": "Promote Bastard",
            }


def _unimpressed_effects(ctx: EffectContext) -> list[Effect]:
    amount = _bandit_level(ctx.source) // 2
    return [
        DerivedStatBonus(stat="mental_fortitude", amount=amount, source="Unimpressed"),
        DerivedStatBonus(stat="cool", amount=amount, source="Unimpressed"),
    ]

# Bandit

build_job("Bandit", [

    # Level 1

    {
        "name": "Ambush",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "After succeeding on a stealth setup against at least one enemy, the Bandit may call an ambush. "
            "Every bastard or party member gains a bonus to attack rolls equal to the level of this skill. "
            "This is a buff."
        ),
        "duration": "1 turn",
        "effects": RollModifierEffect(
            scale_fn=lambda c: c.get_ability_effective_level("Ambush", 0),
            source_tag="ambush",
            condition=lambda ctx, target: IS_ALLY(ctx, target) or tagged("bastard")(ctx, target),
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "party",
        "type": "skill",
    },

    {
        "name": "Band O' Bastards",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "The Bandit designates creatures as bastards. Eligible bastards gain a hit point buff equal "
            "to this skill's level. Creatures with a higher job level than the Bandit cannot benefit from the buff."
        ),
        "duration": "1 day",
        "effects": ApplyBastardStatusEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "creature",
        "type": "skill",
    },

    {
        "name": "Keep the Boys in Line",
        "description": (
            "Bastards who attempt treachery must overcome the Bandit's force of personality and strength. "
            "Failure means they lose their nerve and suffer Moxie damage equal to this skill."
        ),
        "effects": apply_state(
            "keep_the_boys_in_line",
            value_fn=lambda source: {
                "treachery_dc_stat": "strength",
                "treachery_damage_moxie": _ability_level(source, "Keep the Boys in Line"),
                "applies_to": "bastards",
            },
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "bastard",
        "type": "passive",
    },

    {
        "name": "Lay of the Land",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "The Bandit examines a site to determine geographic bonuses or penalties that might affect "
            "ambushes or combat. The difficulty is set by the GM."
        ),
        "duration": "1 minute",
        "effects": skill_check(
            ability="Lay of the Land",
            stat="perception",
            difficulty=_lay_of_the_land_difficulty,
            on_success=inspect(
                reveal_fn=lambda ctx, target: {
                    "ambush_quality": evaluate_ambush_site(ctx, target),
                    "terrain_advantages": get_terrain_advantages(ctx, target),
                }
            ),
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "site",
        "type": "skill",
    },

    {
        "name": "Subdue",
        "cost": 5,
        "cost_pool": "stamina",
        "description": (
            "The Bandit can convert normally lethal attacks to nonlethal attacks, dealing Stamina damage "
            "instead of HP without penalty."
        ),
        "duration": "1 turn per level",
        "effects": apply_state(
            "subdue_active",
            value_fn=lambda source: {
                "damage_pool": "stamina",
                "duration_turns": _ability_level(source, "Subdue"),
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 5

    {"grant": "Cannon Fodder", "required_level": 5,},

    {
        "name": "Gang Up",
        "description": (
            "The Bandit doubles the normal situational bonus for outnumbering a target. "
            "This skill has no levels."
        ),
        "effects": passive_modifier(_gang_up_modifier),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Hogtie",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "The Bandit hogties a helpless target, making escape difficult and establishing a mystical "
            "awareness if the ropes are cut or removed."
        ),
        "duration": "10 minutes per skill level",
        "effects": HogtieEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": True,
        "target": "helpless_target",
        "type": "skill",
    },

    # Level 10

    {"grant": "Get That Guy!", "required_level": 10},

    {
        "name": "Stand and Deliver!",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "While in stealth, the Bandit may speak one word per level without breaking stealth, "
            "and may use fear-based social skills and intimidation before triggering an ambush."
        ),
        "duration": "1 turn",
        "effects": apply_state(
            "stand_and_deliver",
            value_fn=lambda source: {
                "duration_turns": 1,
                "words_allowed": _ability_level(source, "Stand and Deliver!"),
                "maintain_stealth_while_speaking": True,
                "allow_fear_social_skills": True,
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 10,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Forest Lair",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "The Bandit designates a hidden forest or jungle lair. Seekers subtract the Bandit's level "
            "from Perception while searching for it, and the Bandit plus bastards gain a Perception bonus "
            "equal to Bandit level while in the lair."
        ),
        "duration": "1 week",
        "effects": apply_state(
            "forest_lair",
            value_fn=lambda source: {
                "terrain": {"forest", "jungle"},
                "duration_days": 7,
                "search_penalty": _bandit_level(source),
                "lair_perception_bonus": _bandit_level(source),
                "hide_container": True,
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 15,
        "scales_with_level": False,
        "target": "site",
        "type": "skill",
    },

    {
        "name": "Mocking Laugh",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "The Bandit's sinister laugh attacks the nerves of nearby opponents. "
            "It uses Charisma + Mocking Laugh against the Willpower of all opponents within earshot, "
            "and inflicts Moxie damage equal to margin of success after Cool."
        ),
        "duration": "1 attack",
        "effects": apply_state(
            "mocking_laugh_ready",
            value_fn=lambda source: {
                "active": True,
                "attack_stat": "charisma",
                "target_stat": "willpower",
                "damage_pool": "moxie",
                "defense_stat": "cool",
                "stealth_halves_resistance": True,
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 15,
        "scales_with_level": False,
        "target": "enemies_in_earshot",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Dirty Trick",
        "cost": 40,
        "cost_pool": "stamina",
        "description": (
            "The Bandit's next melee attack uses the target's Perception instead of Agility, "
            "and adds Dirty Trick level to the damage inflicted."
        ),
        "duration": "1 attack",
        "effects": modify_next_attack(_dirty_trick_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 20,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Unimpressed",
        "description": (
            "Hardened Bandits have seen it all. They gain a bonus to Mental Fortitude and Cool "
            "equal to half their Bandit level, rounded down."
        ),
        "effects": _unimpressed_effects,
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Level 25

    {
        "name": "Mountain Lair",
        "cost": 100,
        "cost_pool": "sanity",
        "description": (
            "The Bandit designates a hidden hill or mountain lair. Seekers subtract Bandit level from "
            "Perception and Climbing while searching for it, and the Bandit plus bastards gain bonuses "
            "equal to Bandit level while inside."
        ),
        "duration": "1 week",
        "effects": apply_state(
            "mountain_lair",
            value_fn=lambda source: {
                "terrain": {"hill", "mountain"},
                "duration_days": 7,
                "search_perception_penalty": _bandit_level(source),
                "search_climbing_penalty": _bandit_level(source),
                "lair_perception_bonus": _bandit_level(source),
                "lair_climbing_bonus": _bandit_level(source),
                "hide_container": True,
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": False,
        "target": "site",
        "type": "skill",
    },

    {
        "name": "Promote Bastard",
        "cost": 100,
        "cost_pool": "sanity",
        "description": (
            "The Bandit designates a single bastard as a lieutenant. The lieutenant gains a buff to all "
            "attributes equal to the Bandit's level and may substitute the Bandit's Keep the Boys in Line "
            "skill level for their own while loyal."
        ),
        "duration": "1 day",
        "effects": PromoteBastardEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": False,
        "target": "bastard",
        "type": "skill",
    },

], source_type="adventure")