from domain.abilities.builders._job_builder import build_job
from domain.abilities import ability_level, ctx_ability_level, progression_level, ctx_progression_level
from domain.abilities.patterns import (
    apply_state,
    heal_hp,
    inspect,
    passive_modifier,
)
from domain.effects.special.minions import (
    GrantControlledGroupMembershipEffect,
)
from domain.conditions import IS_ENEMY


# Local helpers

def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


def _animated_undead_state(source, undead_type: str, *, intelligent: bool) -> dict:
    return {
        "undead_type": undead_type,
        "creator": source,
        "requires_spirit_present": True,
        "created_by_necromancy": True,
        "intelligent": intelligent,
        "source_job": "Necromancer",
    }


# Passive helpers

def _undead_experimentation_modifier(source) -> None:
    states = _ensure_states(source)
    states["undead_experimentation"] = {
        "active": True,
        "experimental_skill_capacity": progression_level(source, "adventure", "Necromancer") // 10,
        "unequipped_experimental_skills_stored_in_spellbooks": True,
        "source_ability": "Undead Experimentation",
    }


build_job("Necromancer", [

    # Level 1

    {
        "name": "Assess Corpse",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Examine an undead creature or corpse, revealing undead status or animation potential and sanity cost."
        ),
        "duration": "1 Minute",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "assess_corpse",
                "reveals": (
                    "undead_status",
                    "animation_potential",
                    "animation_sanity_cost",
                ),
                "contest_if_target_is_undead": {
                    "caster_stat": "intelligence",
                    "caster_skill": "Assess Corpse",
                    "target_stat": "willpower",
                },
                "failure_on_undead_contest_blocks_read": True,
                "source_ability": "Assess Corpse",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "corpse or enemy",
        "type": "skill",
    },

    {
        "name": "Command the Dead",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Issue a command to a single undead creature. Unintelligent undead may also be invited into your party."
        ),
        "duration": "1 Minute per Necromancer Level",
        "effects": apply_state(
            "command_the_dead_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": progression_level(source, "adventure", "Necromancer"),
                "contest": {
                    "caster_stat": "willpower",
                    "caster_skill": "Command the Dead",
                    "target_stat": "willpower",
                },
                "reasonable_commands_must_be_followed_on_success": True,
                "intelligent_undead_may_refuse_certain_destruction": True,
                "unintelligent_undead_ignore_self_preservation": True,
                "can_invite_unintelligent_undead_into_party": True,
                "party_command_mode": "verbal_indefinite",
                "source_ability": "Command the Dead",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "undead",
        "type": "skill",
    },

    {
        "name": "Soulstone",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "Create a level 1 soulstone that may house a newly dead spirit or existing incorporeal undead."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "soulstone_active",
            value_fn=lambda source: {
                "active": True,
                "creates_soulstone": True,
                "soulstone_level": 1,
                "can_house": (
                    "newly_deceased_spirit",
                    "existing_incorporeal_undead",
                ),
                "housed_spirit_level": (ability_level(source, "Soulstone") + 9) // 10,
                "spirit_can_be_conversed_with": True,
                "spirit_can_be_used_for_undead_creation": True,
                "spirit_can_be_released": True,
                "usable_in_crafting_only_if_spirit_present": True,
                "source_ability": "Soulstone",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "item",
        "type": "skill",
    },

    {
        "name": "Speak with Dead",
        "cost": 5,
        "cost_pool": "sanity",
        "description": (
            "Converse with corpses, spirits, or incoherent undead. Strong spirit areas may reveal conversable spirits."
        ),
        "duration": "1 Minute per Skill Level",
        "effects": apply_state(
            "speak_with_dead_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": ability_level(source, "Speak with Dead"),
                "valid_targets": (
                    "corpses",
                    "spirits",
                    "normally_incoherent_undead",
                ),
                "may_notify_of_strong_local_spirits": True,
                "can_force_conversation": {
                    "caster_stat": "willpower",
                    "caster_skill": "Speak with Dead",
                },
                "source_ability": "Speak with Dead",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "corpse or undead",
        "type": "skill",
    },

    {
        "name": "Zombies",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Turn a corpse into a zombie. Requires a spirit present in the area."
        ),
        "duration": "Permanent",
        "effects": GrantControlledGroupMembershipEffect(
            tag="controlled_undead",
            condition=lambda ctx, target: True,
            controller_state_key="controller",
            extra_state={
                "animation_profile": "zombie",
                "racial_job_level": "original_race_level_1",
                "additional_zombie_job_levels": "skill_level // 10",
                "cannot_use_non_passive_racial_skills": True,
                "requires_spirit_present": True,
                "source_ability": "Zombies",
            },
        ),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "corpse",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Deathsight",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Automatically reveal the hit points of any creature you look at."
        ),
        "duration": "5 Minutes per Necromancer Level",
        "effects": inspect(
            reveal_fn=lambda source: {
                "effect": "deathsight",
                "duration_minutes": progression_level(source, "adventure", "Necromancer") * 5,
                "reveals": "current_hit_points",
                "may_fail_on_unknown_extreme_level_targets": True,
                "source_ability": "Deathsight",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Invite Undead",
        "cost": 10,
        "cost_pool": "sanity",
        "description": (
            "Invite an undead target into your party."
        ),
        "duration": "1 Hour per Necromancer Level",
        "effects": GrantControlledGroupMembershipEffect(
            tag="controlled_undead",
            condition=lambda source, target: True,
            controller_state_key="controller",
            duration_state_key="invited_duration_hours",
            duration_fn=lambda source, target: progression_level(source, "adventure", "Necromancer"),
            extra_state={
                "invited_by_necromancer": True,
                "nonsapient_auto_joins_if_lower_level_and_unpartied": True,
                "sapient_may_refuse": True,
                "source_ability": "Invite Undead",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "undead",
        "type": "skill",
    },

    {
        "name": "Skeletons",
        "cost": 15,
        "cost_pool": "sanity",
        "description": (
            "Turn a corpse into a skeleton. Requires a spirit present in the area."
        ),
        "duration": "Permanent",
        "effects": GrantControlledGroupMembershipEffect(
            tag="controlled_undead",
            condition=lambda ctx, target: True,
            controller_state_key="controller",
            extra_state={
                "animation_profile": "skeleton",
                "racial_job_level": "original_race_level_1",
                "additional_skeleton_job_levels": "skill_level // 10",
                "cannot_use_non_passive_racial_skills": True,
                "requires_spirit_present": True,
                "source_ability": "Skeletons",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "corpse",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Drain Life",
        "cost": 20,
        "cost_pool": "sanity",
        "description": (
            "Drain life from a nearby foe and heal yourself."
        ),
        "duration": "1 Attack",
        "effects": apply_state(
            "drain_life_active",
            value_fn=lambda source: {
                "active": True,
                "attack_stat": "intelligence",
                "attack_skill": "Drain Life",
                "target_stat": "constitution",
                "damage_type": "shadow",
                "does_not_affect": ("constructs",),
                "self_heal_amount": "floor(margin_of_success / 2)",
                "heals_regardless_of_physical_form": True,
                "source_ability": "Drain Life",
            },
        ),
        "is_spell": True,
        "required_level": 10,
        "scales_with_level": False,
        "target": "enemy",
        "type": "skill",
    },

    {"grant": "Mana Focus", "required_level": 10},

    # Level 15

    {
        "name": "Ghouls",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "Turn a corpse into an intelligent ghoul. Requires a spirit present in the area."
        ),
        "duration": "Permanent",
        "effects": GrantControlledGroupMembershipEffect(
            tag="controlled_undead",
            condition=lambda ctx, target: True,
            controller_state_key="controller",
            extra_state={
                "animation_profile": "ghoul",
                "intelligent": True,
                "racial_job_level": "half_original_target_level",
                "can_use_all_granted_skills": True,
                "additional_ghoul_job_levels": "skill_level // 10",
                "requires_spirit_present": True,
                "source_ability": "Ghouls",
            },
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": False,
        "target": "corpse",
        "type": "skill",
    },

    {
        "name": "Repair Undead",
        "cost": 30,
        "cost_pool": "sanity",
        "description": (
            "Heal an undead or dark creature."
        ),
        "duration": "Instant",
        "effects": heal_hp(
            scale_fn=lambda c: c.get_stat("wisdom", 0) + ability_level(c, "Repair Undead"),
        ),
        "is_spell": True,
        "required_level": 15,
        "scales_with_level": True,
        "target": "ally or enemy",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Death Ward",
        "cost": 40,
        "cost_pool": "sanity",
        "description": (
            "Become immune to drain life and other shadow-based attacks, and ward off undead contact."
        ),
        "duration": "1 Turn per Skill Level",
        "effects": apply_state(
            "death_ward_active",
            value_fn=lambda source: {
                "active": True,
                "duration_turns": ability_level(source, "Death Ward"),
                "immune_to_shadow_attacks": True,
                "immune_to_drain_life": True,
                "defense_bonus_vs_undead_damage": progression_level(source, "adventure", "Necromancer"),
                "undead_touch_check": {
                    "attacker_stat": "willpower",
                    "defender_stat": "willpower",
                },
                "source_ability": "Death Ward",
            },
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Wights",
        "cost": 40,
        "cost_pool": "sanity",
        "description": (
            "Turn a corpse into an intelligent wight. Requires a spirit present in the area."
        ),
        "duration": "Permanent",
        "effects": GrantControlledGroupMembershipEffect(
            tag="controlled_undead",
            condition=lambda ctx, target: True,
            controller_state_key="controller",
            extra_state={
                "animation_profile": "wight",
                "intelligent": True,
                "racial_job_level": "half_original_target_level",
                "one_job_level_from_highest_life_job": True,
                "can_use_all_granted_skills": True,
                "additional_wight_job_levels": "skill_level // 10",
                "requires_spirit_present": True,
                "source_ability": "Wights",
            },
        ),
        "is_spell": True,
        "required_level": 20,
        "scales_with_level": False,
        "target": "corpse",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Mummy",
        "cost": 50,
        "cost_pool": "sanity",
        "description": (
            "Turn a corpse into an intelligent mummy. Requires a spirit, canopic jars, surgical tools, and bandages."
        ),
        "duration": "Permanent",
        "effects": GrantControlledGroupMembershipEffect(
            tag="controlled_undead",
            condition=lambda ctx, target: True,
            controller_state_key="controller",
            extra_state={
                "animation_profile": "mummy",
                "intelligent": True,
                "racial_job_level": "original_target_level",
                "adventure_or_crafting_job_levels": "half_highest_life_level",
                "can_use_all_granted_skills": True,
                "additional_mummy_job_levels": "skill_level // 10",
                "requires_spirit_present": True,
                "requires_materials": (
                    "canopic_jars",
                    "surgical_tools",
                    "bandages",
                ),
                "source_ability": "Mummy",
            },
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "corpse",
        "type": "skill",
    },

    {
        "name": "Undead Experimentation",
        "description": (
            "Research and produce new Necromancer skills."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_undead_experimentation_modifier),
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

], source_type="adventure")