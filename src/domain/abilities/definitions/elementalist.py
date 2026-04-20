from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    composite,
    create_item,
    heal_fortune,
    heal_hp,
    heal_moxie,
    heal_sanity,
    heal_stamina,
    passive_modifier,
    summon,
)
from domain.effects.base import EffectContext
from domain.effects.special.minions import (
    GrantControlledGroupMembershipEffect,
    ScaledSkillBuffEffect,
)


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _elementalist_level(character) -> int:
    return character.get_progression_level("adventure", "Elementalist", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


def _get_affinities(source) -> list[str]:
    states = getattr(source, "states", {})
    affinities = states.get("elemental_affinities")
    if isinstance(affinities, list) and affinities:
        return affinities
    if isinstance(affinities, tuple) and affinities:
        return list(affinities)
    return ["chosen_affinity"]


def _primary_affinity(source) -> str:
    return _get_affinities(source)[0]


def _matching_elemental_affinity(ctx: EffectContext, target) -> bool:
    target_states = getattr(target, "states", {})
    target_affinity = target_states.get("elemental_affinity")
    if target_affinity is None:
        return False
    return target_affinity in _get_affinities(ctx.source)


def _is_controlled_elemental(ctx: EffectContext, target) -> bool:
    tags = getattr(target, "tags", set())
    return "controlled_elemental" in tags and _matching_elemental_affinity(ctx, target)


def _call_element_factory(source):
    affinity = _primary_affinity(source)
    return {
        "name": f"{affinity.title()} Element",
        "description": "A quantity of called elemental material.",
        "element": affinity,
        "volume_cubic_feet": _ability_level(source, "Call Element"),
        "created_by": "Call Element",
        "temporary": True,
    }


def _elemental_factory(rank_name: str, class_rank: int):
    def factory(source):
        affinity = _primary_affinity(source)
        return {
            "name": f"{rank_name} {affinity.title()} Elemental",
            "description": f"A Class {class_rank} elemental summoned by an Elementalist.",
            "entity_type": "elemental",
            "element": affinity,
            "class_rank": class_rank,
            "level": _elementalist_level(source),
            "loyal_to_summoner": True,
            "follows_commands": True,
            "duration_hours": _elementalist_level(source),
            "created_by": rank_name,
        }
    return factory


# Passive helpers

def _elemental_affinity_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    current = states.get("elemental_affinities", [])
    if not current:
        current = ["chosen_affinity"]

    states["elemental_affinities"] = list(current)
    states["elemental_affinity_resistance"] = {
        "active": True,
        "affinities": list(current),
        "percent_reduction": 80,
        "source_ability": "Elemental Affinity",
    }


def _elemental_affinity_ii_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    current = list(states.get("elemental_affinities", []))
    if not current:
        current = ["chosen_affinity"]

    if len(current) < 2:
        current.append("chosen_second_affinity")

    states["elemental_affinities"] = current
    states["elemental_affinity_ii_resistance"] = {
        "active": True,
        "affinities": list(current),
        "percent_reduction": 80,
        "source_ability": "Elemental Affinity II",
    }


build_job("Elementalist", [

    # Level 1

    {
        "name": "Call Element",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Creates an amount of your chosen element equal to one cubic foot per level of this skill."
        ),
        "duration": "1 Action",
        "effects": create_item(_call_element_factory),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "unoccupied area",
        "type": "skill",
    },

    {
        "name": "Elemental Affinity",
        "description": (
            "Choose one element and gain 80% resistance to damage from that element."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_elemental_affinity_modifier),
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Endure Element",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Gives yourself or an ally resistance to one of your affinities equal to this skill's level as a percentage."
        ),
        "duration": "1 Hour",
        "effects": apply_state(
            "endure_element_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": 1,
                "choose_from_affinities": _get_affinities(source),
                "elemental_resistance_percent": _ability_level(source, "Endure Element"),
                "stacks_with_elemental_affinity": True,
                "source_ability": "Endure Element",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Least Elemental",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "Summons a Class One elemental of your affinity. It is loyal and follows commands. Only one may be active at a time."
        ),
        "duration": "1 Hour per Caster Level",
        "effects": composite(
            summon(_elemental_factory("Least Elemental", 1)),
            GrantControlledGroupMembershipEffect(
                tag="controlled_elemental",
                condition=lambda ctx, target: True,
                controller_state_key="controller",
                duration_state_key="duration_hours",
                duration_fn=lambda ctx, target: _elementalist_level(ctx.source),
                extra_state={
                    "elemental_affinity": "match_summoner_affinity",
                    "elemental_rank": 1,
                    "loyal_to_summoner": True,
                    "follows_commands": True,
                    "summoned_by": "Least Elemental",
                },
            ),
            apply_state(
                "least_elemental_summoning",
                value_fn=lambda source: {
                    "active": True,
                    "contest": {
                        "caster_stat": "willpower",
                        "caster_skill": "Least Elemental",
                        "target_stat": "willpower",
                    },
                    "only_one_active": True,
                    "source_ability": "Least Elemental",
                },
            ),
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Manipulate Element",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Manipulates a matching element. It can be used as an attack with Dexterity plus Manipulate Element, "
            "and critical hits inflict a one-turn elemental condition based on affinity."
        ),
        "duration": "1 Minute",
        "effects": apply_state(
            "manipulate_element_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": 1,
                "requires_matching_element": True,
                "can_attack_with_element": True,
                "attack_stat": "dexterity",
                "attack_skill": "Manipulate Element",
                "critical_effects_by_element": {
                    "fire": "burning",
                    "water": "slowed",
                    "earth": "hobbled",
                    "air": "stunned",
                },
                "critical_condition_duration_turns": 1,
                "source_ability": "Manipulate Element",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Destroy Element",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Destroys up to one cubic foot per skill level of your element. Against matching elementals or creatures, "
            "it acts as an attack that bypasses armor and defenses."
        ),
        "duration": "1 Attack",
        "effects": apply_state(
            "destroy_element_active",
            value_fn=lambda source: {
                "active": True,
                "destroy_volume_cubic_feet": _ability_level(source, "Destroy Element"),
                "matching_affinity_required": True,
                "attack_stat": "intelligence",
                "attack_skill": "Destroy Element",
                "defense_stat": "agility",
                "bypasses_armor": True,
                "bypasses_other_defenses": True,
                "source_ability": "Destroy Element",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    {"grant": "Mana Focus", "required_level": 5},

    {
        "name": "Shape Element",
        "cost": 15,
        "cost_pool": "sanity",
        "description": (
            "Shapes one cubic foot per skill level of your element. The shaped element may deal damage "
            "equal to twice your Elementalist level and bypass defenses."
        ),
        "duration": "1 Turn per Elementalist Level",
        "effects": apply_state(
            "shape_element_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": _elementalist_level(source),
                "shape_volume_cubic_feet": _ability_level(source, "Shape Element"),
                "matching_affinity_required": True,
                "contact_damage": _elementalist_level(source) * 2,
                "contact_damage_pool": "hp",
                "bypasses_defenses": True,
                "source_ability": "Shape Element",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": True,
        "target": "unoccupied area",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Elemental Cohorts",
        "description": (
            "All elementals in your party that share your affinity gain a bonus to attack rolls equal to your Elementalist level."
        ),
        "duration": "Passive Constant",
        "effects": ScaledSkillBuffEffect(
            scale_fn=_elementalist_level,
            skills=("attack",),
            condition=_is_controlled_elemental,
        ),
        "is_spell": False,
        "required_level": 10,
        "scales_with_level": False,
        "target": "party",
        "type": "passive",
    },

    {
        "name": "Summon Minor Elemental",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "Summons a Class Two elemental of your affinity. It is loyal and follows commands. Only one may be active at a time."
        ),
        "duration": "1 Hour per Caster Level",
        "effects": composite(
            summon(_elemental_factory("Minor Elemental", 2)),
            GrantControlledGroupMembershipEffect(
                tag="controlled_elemental",
                condition=lambda ctx, target: True,
                controller_state_key="controller",
                duration_state_key="duration_hours",
                duration_fn=lambda ctx, target: _elementalist_level(ctx.source),
                extra_state={
                    "elemental_affinity": "match_summoner_affinity",
                    "elemental_rank": 2,
                    "loyal_to_summoner": True,
                    "follows_commands": True,
                    "summoned_by": "Summon Minor Elemental",
                },
            ),
            apply_state(
                "minor_elemental_summoning",
                value_fn=lambda source: {
                    "active": True,
                    "contest": {
                        "caster_stat": "willpower",
                        "caster_skill": "Summon Minor Elemental",
                        "target_stat": "willpower",
                    },
                    "only_one_active": True,
                    "source_ability": "Summon Minor Elemental",
                },
            ),
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Dismiss Elemental",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "Attempts to dismiss an elemental back to its own plane."
        ),
        "duration": "Instant",
        "effects": apply_state(
            "dismiss_elemental_active",
            value_fn=lambda source: {
                "active": True,
                "contest": {
                    "caster_stat": "willpower",
                    "caster_skill": "Dismiss Elemental",
                    "target_stat": "willpower",
                },
                "on_success": "dismiss_target_elemental",
                "source_ability": "Dismiss Elemental",
            },
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Elemental Jaunt",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "Travel between sizeable representations of your element at a range of one mile per Elementalist level."
        ),
        "duration": "1 Turn",
        "effects": apply_state(
            "elemental_jaunt_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": 1,
                "requires_matching_entry_element": True,
                "requires_matching_exit_element": True,
                "max_range_miles": _elementalist_level(source),
                "valid_affinities": _get_affinities(source),
                "source_ability": "Elemental Jaunt",
            },
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Consume Element",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "While active, successfully using Destroy Element heals all your pools by your Elementalist level."
        ),
        "duration": "1 Minute",
        "effects": composite(
            apply_state(
                "consume_element_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_minutes": 1,
                    "trigger_ability": "Destroy Element",
                    "heal_all_pools_on_success": _elementalist_level(source),
                    "matching_affinity_required": True,
                    "source_ability": "Consume Element",
                },
            ),
            heal_hp(scale_fn=_elementalist_level),
            heal_sanity(scale_fn=_elementalist_level),
            heal_stamina(scale_fn=_elementalist_level),
            heal_moxie(scale_fn=_elementalist_level),
            heal_fortune(scale_fn=_elementalist_level),
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Summon Lesser Elemental",
        "cost": 100,
        "cost_pool": "sanity",
        "description": (
            "Summons a Class Three elemental of your affinity. It is loyal and follows commands. Only one may be active at a time."
        ),
        "duration": "1 Hour per Caster Level",
        "effects": composite(
            summon(_elemental_factory("Lesser Elemental", 3)),
            GrantControlledGroupMembershipEffect(
                tag="controlled_elemental",
                condition=lambda ctx, target: True,
                controller_state_key="controller",
                duration_state_key="duration_hours",
                duration_fn=lambda ctx, target: _elementalist_level(ctx.source),
                extra_state={
                    "elemental_affinity": "match_summoner_affinity",
                    "elemental_rank": 3,
                    "loyal_to_summoner": True,
                    "follows_commands": True,
                    "summoned_by": "Summon Lesser Elemental",
                },
            ),
            apply_state(
                "lesser_elemental_summoning",
                value_fn=lambda source: {
                    "active": True,
                    "contest": {
                        "caster_stat": "willpower",
                        "caster_skill": "Summon Lesser Elemental",
                        "target_stat": "willpower",
                    },
                    "only_one_active": True,
                    "source_ability": "Summon Lesser Elemental",
                },
            ),
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Elemental Affinity II",
        "description": (
            "Choose a second element and gain affinity with it as well, including the usual 80% resistance."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_elemental_affinity_ii_modifier),
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Summon Greater Elemental",
        "cost": 200,
        "cost_pool": "sanity",
        "description": (
            "Summons a Class Four elemental of your affinity. It is loyal and follows commands. Only one may be active at a time."
        ),
        "duration": "1 Hour per Caster Level",
        "effects": composite(
            summon(_elemental_factory("Greater Elemental", 4)),
            GrantControlledGroupMembershipEffect(
                tag="controlled_elemental",
                condition=lambda ctx, target: True,
                controller_state_key="controller",
                duration_state_key="duration_hours",
                duration_fn=lambda ctx, target: _elementalist_level(ctx.source),
                extra_state={
                    "elemental_affinity": "match_summoner_affinity",
                    "elemental_rank": 4,
                    "loyal_to_summoner": True,
                    "follows_commands": True,
                    "summoned_by": "Summon Greater Elemental",
                },
            ),
            apply_state(
                "greater_elemental_summoning",
                value_fn=lambda source: {
                    "active": True,
                    "contest": {
                        "caster_stat": "willpower",
                        "caster_skill": "Summon Greater Elemental",
                        "target_stat": "willpower",
                    },
                    "only_one_active": True,
                    "source_ability": "Summon Greater Elemental",
                },
            ),
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

], source_type="adventure")