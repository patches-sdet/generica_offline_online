from domain.abilities import ability_level, progression_level
from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    inspect,
    modify_next_attack,
    passive_modifier,
    scaled_derived_buff,
    skill_check,
)
from domain.conditions import IS_ALLY, tagged
from domain.effects.base import Effect, EffectContext

def _highest_job_level(entity) -> int:
    progressions = getattr(entity, "progressions", {}) or {}
    best = 0

    for progression in progressions.values():
        if getattr(progression, "type", None) in {"adventure", "profession", "advanced"}:
            best = max(best, progression.level)

    return best

def _bandit_level(character) -> int:
    return progression_level(character, "adventure", "Bandit")

def _bastard_is_eligible(ctx, target) -> bool:
    """
    Interprets 'job level higher than the Bandit' as:
    target's highest job level (adventure/profession/advanced)
    may not exceed the source Bandit's level.
    """
    return _highest_job_level(target) <= _bandit_level(ctx.source)

def _evaluate_ambush_site(ctx, target) -> str:
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

def _get_terrain_advantages(ctx, target) -> list[str]:
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

# Attack modifiers

def _dirty_trick_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "target_stat", "perception")
    _set_attack_attr(attack, "bonus_damage", ability_level(ctx.source, "Dirty Trick"))
    _set_attack_attr(attack, "dirty_trick", True)

# Passive runtime helpers

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
        bonus = ability_level(context.source, "Band O' Bastards")

        for target in context.targets:
            tags = _ensure_tags(target)
            tags.add("bastard")

            eligible = _bastard_is_eligible(context, target)

            states = _ensure_states(target)
            states["bastard_status"] = {
                "controller": context.source,
                "duration_days": 1,
                "eligible_for_bastard_buffs": eligible,
                "hp_bonus": bonus if eligible else 0,
                "source_ability": "Band O' Bastards",
            }

class HogtieEffect(Effect):
    """
    Runtime-facing placeholder for hogtying helpless targets.
    Stores the intended escape challenge structure until full roll handling exists.
    """

    def apply(self, context: EffectContext) -> None:
        duration_turns = ability_level(context.source, "Hogtie") * 10

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
                "substitute_keep_the_boys_in_line": ability_level(
                    context.source,
                    "Keep the Boys in Line",
                ),
                "breaks_on_betrayal": True,
                "source_ability": "Promote Bastard",
            }

# Bandit

build_job(
    "Bandit",
    [
        # Level 1
        {
            "name": "Ambush",
            "type": "skill",
            "cost": 10,
            "cost_pool": "stamina",
            "duration": "1 turn",
            "target": "party",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "After succeeding on a stealth setup against at least one enemy, the "
                "Bandit may call an ambush. Every bastard or party member gains a bonus "
                "to attack rolls equal to the level of this skill. This is a buff."
            ),
            "effects": apply_state(
                "ambush",
                value_fn=lambda source: {
                    "duration_turns": 1,
                    "attack_bonus": ability_level(source, "Ambush"),
                    "applies_to_party": True,
                    "applies_to_bastards": True,
                    "source_ability": "Ambush",
                },
            ),
        },
        {
            "name": "Band O' Bastards",
            "type": "skill",
            "cost": 10,
            "cost_pool": "sanity",
            "duration": "1 day",
            "target": "creature",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "The Bandit designates creatures as bastards. Eligible bastards gain a "
                "hit point buff equal to this skill's level. Creatures with a higher "
                "job level than the Bandit cannot benefit from the buff."
            ),
            "effects": ApplyBastardStatusEffect(),
        },
        {
            "name": "Keep the Boys in Line",
            "type": "passive",
            "target": "bastard",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "Bastards who attempt treachery must overcome the Bandit's force of "
                "personality and strength. Failure means they lose their nerve and "
                "suffer Moxie damage equal to this skill."
            ),
            "effects": apply_state(
                "keep_the_boys_in_line",
                value_fn=lambda source: {
                    "treachery_dc_stat": "strength",
                    "treachery_damage_moxie": ability_level(source, "Keep the Boys in Line"),
                    "applies_to": "bastards",
                },
            ),
        },
        {
            "name": "Lay of the Land",
            "type": "skill",
            "cost": 5,
            "cost_pool": "sanity",
            "duration": "1 minute",
            "target": "site",
            "required_level": 1,
            "scales_with_level": False,
            "description": (
                "The Bandit examines a site to determine geographic bonuses or penalties "
                "that might affect ambushes or combat. The difficulty is set by the GM."
            ),
            "effects": skill_check(
                ability="Lay of the Land",
                stat="perception",
                difficulty=_lay_of_the_land_difficulty,
                on_success=inspect(
                    reveal_fn=lambda ctx, target: {
                        "ambush_quality": _evaluate_ambush_site(ctx, target),
                        "terrain_advantages": _get_terrain_advantages(ctx, target),
                    }
                ),
            ),
        },
        {
            "name": "Subdue",
            "type": "skill",
            "cost": 5,
            "cost_pool": "stamina",
            "duration": "1 turn per level",
            "target": "self",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "The Bandit can convert normally lethal attacks to nonlethal attacks, "
                "dealing Stamina damage instead of HP without penalty."
            ),
            "effects": apply_state(
                "subdue_active",
                value_fn=lambda source: {
                    "damage_pool": "stamina",
                    "duration_turns": ability_level(source, "Subdue"),
                },
            ),
        },

        # Level 5
        {"grant": "Cannon Fodder", "required_level": 5},

        {
            "name": "Gang Up",
            "type": "passive",
            "target": "self",
            "required_level": 5,
            "scales_with_level": False,
            "description": (
                "The Bandit doubles the normal situational bonus for outnumbering a "
                "target. This skill has no levels."
            ),
            "effects": passive_modifier(_gang_up_modifier),
        },
        {
            "name": "Hogtie",
            "type": "skill",
            "cost": 10,
            "cost_pool": "stamina",
            "duration": "10 minutes per skill level",
            "target": "helpless_target",
            "required_level": 5,
            "scales_with_level": True,
            "description": (
                "The Bandit hogties a helpless target, making escape difficult and "
                "establishing a mystical awareness if the ropes are cut or removed."
            ),
            "effects": HogtieEffect(),
        },

        # Level 10
        {"grant": "Get That Guy!", "required_level": 10},
        
        {
            "name": "Stand and Deliver!",
            "type": "skill",
            "cost": 20,
            "cost_pool": "sanity",
            "duration": "1 turn",
            "target": "self",
            "required_level": 10,
            "scales_with_level": True,
            "description": (
                "While in stealth, the Bandit may speak one word per level without "
                "breaking stealth, and may use fear-based social skills and intimidation "
                "before triggering an ambush."
            ),
            "effects": apply_state(
                "stand_and_deliver",
                value_fn=lambda source: {
                    "duration_turns": 1,
                    "words_allowed": ability_level(source, "Stand and Deliver!"),
                    "maintain_stealth_while_speaking": True,
                    "allow_fear_social_skills": True,
                },
            ),
        },

        # Level 15
        {
            "name": "Forest Lair",
            "type": "skill",
            "cost": 50,
            "cost_pool": "sanity",
            "duration": "1 week",
            "target": "site",
            "required_level": 15,
            "scales_with_level": False,
            "description": (
                "The Bandit designates a hidden forest or jungle lair. Seekers subtract "
                "the Bandit's level from Perception while searching for it, and the "
                "Bandit plus bastards gain a Perception bonus equal to Bandit level "
                "while in the lair."
            ),
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
        },
        {
            "name": "Mocking Laugh",
            "type": "skill",
            "cost": 30,
            "cost_pool": "sanity",
            "duration": "1 attack",
            "target": "enemies_in_earshot",
            "required_level": 15,
            "scales_with_level": False,
            "description": (
                "The Bandit's sinister laugh attacks the nerves of nearby opponents. "
                "It uses Charisma + Mocking Laugh against the Willpower of all opponents "
                "within earshot, and inflicts Moxie damage equal to margin of success "
                "after Cool."
            ),
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
        },

        # Level 20
        {
            "name": "Dirty Trick",
            "type": "skill",
            "cost": 40,
            "cost_pool": "stamina",
            "duration": "1 attack",
            "target": "self",
            "required_level": 20,
            "scales_with_level": True,
            "description": (
                "The Bandit's next melee attack uses the target's Perception instead of "
                "Agility, and adds Dirty Trick level to the damage inflicted."
            ),
            "effects": modify_next_attack(_dirty_trick_modifier),
        },
        {
            "name": "Unimpressed",
            "type": "passive",
            "target": "self",
            "required_level": 20,
            "scales_with_level": False,
            "description": (
                "Hardened Bandits have seen it all. They gain a bonus to Mental "
                "Fortitude and Cool equal to half their Bandit level, rounded down."
            ),
            "effects": [
                scaled_derived_buff(
                    stat="mental_fortitude",
                    scale_fn=lambda source: _bandit_level(source) // 2,
                ),
                scaled_derived_buff(
                    stat="cool",
                    scale_fn=lambda source: _bandit_level(source) // 2,
                ),
            ],
        },

        # Level 25
        {
            "name": "Mountain Lair",
            "type": "skill",
            "cost": 100,
            "cost_pool": "sanity",
            "duration": "1 week",
            "target": "site",
            "required_level": 25,
            "scales_with_level": False,
            "description": (
                "The Bandit designates a hidden hill or mountain lair. Seekers subtract "
                "Bandit level from Perception and Climbing while searching for it, and "
                "the Bandit plus bastards gain bonuses equal to Bandit level while inside."
            ),
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
        },
        {
            "name": "Promote Bastard",
            "type": "skill",
            "cost": 100,
            "cost_pool": "sanity",
            "duration": "1 day",
            "target": "bastard",
            "required_level": 25,
            "scales_with_level": False,
            "description": (
                "The Bandit designates a single bastard as a lieutenant. The lieutenant "
                "gains a buff to all attributes equal to the Bandit's level and may "
                "substitute the Bandit's Keep the Boys in Line skill level for their own "
                "while loyal."
            ),
            "effects": PromoteBastardEffect(),
        },
    ],
    source_type="adventure",
)