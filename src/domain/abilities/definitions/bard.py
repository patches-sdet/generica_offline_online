from domain.abilities import ability_level, progression_level
from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    aura,
    composite,
    heal_hp,
    heal_stamina,
    scaled_derived_buff,
    scaled_stat_buff,
)
from domain.conditions import IS_ALLY, IS_ENEMY

def _per_ten(ability_name: str):
    """
    For songs that heal / pulse by 'every full ten points'
    in the skill. Intentionally rounds down.
    """
    return lambda source: ability_level(source, ability_name) // 10


def _active_song_payload(source, song_name: str, extra: dict | None = None) -> dict:
    payload = {
        "song_name": song_name,
        "aura_id": "bard_song",
        "allow_multiple_songs": bool(
            getattr(source, "states", {}).get("band_practice_active", {}).get("active", False)
        ),
    }
    if extra:
        payload.update(extra)
    return payload


def _borrowed_skill_state(slot_name: str, tier: int, required_job_level: int):
    return apply_state(
        slot_name,
        value_fn=lambda source: {
            "slot_name": slot_name,
            "tier": tier,
            "required_job_level": required_job_level,
            "chosen_skill": getattr(source, "states", {}).get(slot_name, {}).get("chosen_skill"),
            "forbid_tags": {"godspell", "darkspell"},
            "source_ability": slot_name.replace("_", " ").title(),
        },
    )


build_job(
    "Bard",
    [
        # Level 1
        {
            "name": "Borrowed Skill I",
            "type": "passive",
            "target": "self",
            "required_level": 1,
            "scales_with_level": False,
            "description": (
                "The Bard may permanently slot any Tier One, level 1 adventuring job skill "
                "into this borrowed-skill slot. Godspells and darkspells may not be chosen. "
                "This is currently stored as a structured placeholder until borrowed-skill "
                "selection and validation are implemented."
            ),
            "duration": "Permanent",
            "effects": _borrowed_skill_state(
                slot_name="borrowed_skill_1",
                tier=1,
                required_job_level=1,
            ),
        },
        {
            "name": "Distracting Song",
            "type": "skill",
            "cost": 5,
            "cost_pool": "moxie",
            "target": "enemy",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "Costs 5 moxie per minute of use. Enemies within earshot suffer a debuff to "
                "Charisma, Perception, and Willpower equal to the level of this skill. "
                "A Bard can only ever have one song active at a time unless Band Practice is active."
            ),
            "duration": "Until Ceased",
            "effects": aura(
                scaled_stat_buff(
                    scale_fn=lambda source: ability_level(source, "Distracting Song"),
                    stats={
                        "charisma": -1,
                        "perception": -1,
                        "willpower": -1,
                    },
                    condition=IS_ENEMY,
                ),
                aura_id="bard_song",
            ),
        },
        {
            "name": "Heartening Song",
            "type": "skill",
            "cost": 5,
            "cost_pool": "moxie",
            "target": "ally",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "Costs 5 moxie per minute of use. Allies within earshot gain a bonus to Strength "
                "and attack rolls equal to the level of this skill. A Bard can only ever have one "
                "song active at a time unless Band Practice is active."
            ),
            "duration": "Until Ceased",
            "effects": aura(
                composite(
                    scaled_stat_buff(
                        scale_fn=lambda source: ability_level(source, "Heartening Song"),
                        stats={"strength": 1},
                        condition=IS_ALLY,
                    ),
                    apply_state(
                        "heartening_song",
                        value_fn=lambda source: _active_song_payload(
                            source,
                            "Heartening Song",
                            {
                                "targets": "allies_in_earshot",
                                "attack_bonus": ability_level(source, "Heartening Song"),
                                "cost_per_minute": 5,
                            },
                        ),
                    ),
                ),
                aura_id="bard_song",
            ),
        },
        {
            "name": "Just That Cool",
            "type": "passive",
            "target": "self",
            "required_level": 1,
            "scales_with_level": False,
            "description": (
                "Bards are so cool that they gain a bonus to their Cool equal to their Bard level. "
                "This skill has no levels."
            ),
            "duration": "Passive Constant",
            "effects": scaled_derived_buff(
                scale_fn=lambda source: progression_level(source, "adventure", "Bard"),
                stat="cool",
            ),
        },
        {
            "name": "Rejuvenating Song",
            "type": "skill",
            "cost": 5,
            "cost_pool": "moxie",
            "target": "ally",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "Costs 5 moxie per minute of use. Allies within earshot heal HP and stamina each turn. "
                "The healing rate is equal to one point of each per full ten levels in this skill. "
                "A Bard can only ever have one song active at a time unless Band Practice is active."
            ),
            "duration": "Until Ceased",
            "effects": aura(
                composite(
                    heal_hp(
                        scale_fn=_per_ten("Rejuvenating Song"),
                        condition=IS_ALLY,
                    ),
                    heal_stamina(
                        scale_fn=_per_ten("Rejuvenating Song"),
                        condition=IS_ALLY,
                    ),
                ),
                aura_id="bard_song",
            ),
        },

        # Level 5
        {
            "name": "Borrowed Skill V",
            "type": "passive",
            "target": "self",
            "required_level": 5,
            "scales_with_level": False,
            "description": (
                "The Bard may permanently slot any Tier One, level 5 adventuring job skill "
                "into this borrowed-skill slot. Godspells and darkspells may not be chosen. "
                "This is currently stored as a structured placeholder until borrowed-skill "
                "selection and validation are implemented."
            ),
            "duration": "Permanent",
            "effects": _borrowed_skill_state(
                slot_name="borrowed_skill_5",
                tier=1,
                required_job_level=5,
            ),
        },
        {
            "name": "Fortune's Fool",
            "type": "passive",
            "target": "self",
            "required_level": 5,
            "scales_with_level": False,
            "description": (
                "The Bard's luck becomes absurdly reliable. They gain a bonus to Fortune equal "
                "to their Bard level. This skill has no levels."
            ),
            "duration": "Passive Constant",
            "effects": scaled_derived_buff(
                scale_fn=lambda source: progression_level(source, "adventure", "Bard"),
                stat="fortune",
            ),
        },
        {
            "name": "Salty Song",
            "type": "skill",
            "cost": 10,
            "cost_pool": "moxie",
            "target": "everyone_in_earshot",
            "required_level": 5,
            "scales_with_level": True,
            "description": (
                "Costs 10 moxie per minute of use. Everyone within earshot takes ongoing moxie damage "
                "equal to this skill minus Cool, minimum 1. A Bard can only ever have one song active "
                "at a time unless Band Practice is active."
            ),
            "duration": "Until Ceased",
            "effects": apply_state(
                "salty_song_active",
                value_fn=lambda source: _active_song_payload(
                    source,
                    "Salty Song",
                    {
                        "targets": "everyone_in_earshot",
                        "damage_pool": "moxie",
                        "damage_formula": {
                            "base": ability_level(source, "Salty Song"),
                            "minus_defense": "cool",
                            "minimum": 1,
                        },
                        "cost_per_minute": 10,
                    },
                ),
            ),
        },

        # Level 10
        {
            "name": "Borrowed Skill X",
            "type": "passive",
            "target": "self",
            "required_level": 10,
            "scales_with_level": False,
            "description": (
                "The Bard may permanently slot any Tier One, level 10 adventuring job skill "
                "into this borrowed-skill slot. Godspells and darkspells may not be chosen. "
                "This is currently stored as a structured placeholder until borrowed-skill "
                "selection and validation are implemented."
            ),
            "duration": "Permanent",
            "effects": _borrowed_skill_state(
                slot_name="borrowed_skill_10",
                tier=1,
                required_job_level=10,
            ),
        },
        {
            "name": "Song of Clarity",
            "type": "skill",
            "cost": 20,
            "cost_pool": "moxie",
            "target": "ally",
            "required_level": 10,
            "scales_with_level": True,
            "description": (
                "Costs 20 moxie per minute of use. Allies within earshot heal sanity and moxie each turn. "
                "The healing rate is two points of each per full ten levels in this skill. A Bard can only "
                "ever have one song active at a time unless Band Practice is active."
            ),
            "duration": "Until Ceased",
            "effects": apply_state(
                "song_of_clarity_active",
                value_fn=lambda source: _active_song_payload(
                    source,
                    "Song of Clarity",
                    {
                        "targets": "allies_in_earshot",
                        "heal_sanity_per_tick": _per_ten("Song of Clarity")(source) * 2,
                        "heal_moxie_per_tick": _per_ten("Song of Clarity")(source) * 2,
                        "cost_per_minute": 20,
                    },
                ),
            ),
        },

        # Level 15
        {
            "name": "Borrowed Skill XV",
            "type": "passive",
            "target": "self",
            "required_level": 15,
            "scales_with_level": False,
            "description": (
                "The Bard may permanently slot any Tier One, level 15 adventuring job skill "
                "into this borrowed-skill slot. Godspells and darkspells may not be chosen. "
                "This is currently stored as a structured placeholder until borrowed-skill "
                "selection and validation are implemented."
            ),
            "duration": "Permanent",
            "effects": _borrowed_skill_state(
                slot_name="borrowed_skill_15",
                tier=1,
                required_job_level=15,
            ),
        },
        {
            "name": "Painful Song",
            "type": "skill",
            "cost": 25,
            "cost_pool": "moxie",
            "target": "everyone_in_earshot",
            "required_level": 15,
            "scales_with_level": True,
            "description": (
                "Costs 25 moxie per minute of use. Everyone within earshot takes ongoing HP damage "
                "equal to this skill minus Armor, minimum 1. A Bard can only ever have one song active "
                "at a time unless Band Practice is active."
            ),
            "duration": "Until Ceased",
            "effects": apply_state(
                "painful_song_active",
                value_fn=lambda source: _active_song_payload(
                    source,
                    "Painful Song",
                    {
                        "targets": "everyone_in_earshot",
                        "damage_pool": "hp",
                        "damage_formula": {
                            "base": ability_level(source, "Painful Song"),
                            "minus_defense": "armor",
                            "minimum": 1,
                        },
                        "cost_per_minute": 25,
                    },
                ),
            ),
        },

        # Level 20
        {
            "name": "Borrowed Skill XX",
            "type": "passive",
            "target": "self",
            "required_level": 20,
            "scales_with_level": False,
            "description": (
                "The Bard may permanently slot any Tier One, level 20 adventuring job skill "
                "into this borrowed-skill slot. Godspells and darkspells may not be chosen. "
                "This is currently stored as a structured placeholder until borrowed-skill "
                "selection and validation are implemented."
            ),
            "duration": "Permanent",
            "effects": _borrowed_skill_state(
                slot_name="borrowed_skill_20",
                tier=1,
                required_job_level=20,
            ),
        },
        {
            "name": "Sick Riff",
            "type": "skill",
            "cost": 30,
            "cost_pool": "stamina",
            "target": "enemy",
            "required_level": 20,
            "scales_with_level": True,
            "description": (
                "The Bard unleashes a sonic attack. This is a Charisma + Sick Riff attack against "
                "the target's Willpower, inflicting moxie damage on success. Stored as a structured "
                "attack placeholder until full contested roll and damage resolution are implemented."
            ),
            "duration": "1 attack",
            "effects": apply_state(
                "sick_riff_ready",
                value_fn=lambda source: {
                    "active": True,
                    "attack_stat": "charisma",
                    "skill_name": "Sick Riff",
                    "target_stat": "willpower",
                    "damage_pool": "moxie",
                    "source_ability": "Sick Riff",
                },
            ),
        },

        # Level 25
        {
            "name": "Band Practice",
            "type": "skill",
            "cost": 200,
            "cost_pool": "moxie",
            "target": "self",
            "required_level": 25,
            "scales_with_level": True,
            "description": (
                "The Bard may activate all song skills at once, ignoring the normal one-song limit. "
                "While Band Practice is active, the Bard may take no action other than movement."
            ),
            "duration": "1 minute per skill level",
            "effects": apply_state(
                "band_practice_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_turns": ability_level(source, "Band Practice"),
                    "allow_multiple_bard_songs": True,
                    "restrict_actions_to_move_only": True,
                    "source_ability": "Band Practice",
                },
            ),
        },
        {
            "name": "Celebrity",
            "type": "passive",
            "target": "self",
            "required_level": 25,
            "scales_with_level": False,
            "description": (
                "While undisguised, the Bard may be recognized even by people who logically should not know them. "
                "Recognition is generally luck-based and GM-triggered. Those who recognize the Bard usually "
                "treat them more favorably. This skill has no levels."
            ),
            "duration": "Passive Constant",
            "effects": apply_state(
                "celebrity_status",
                value_fn=lambda source: {
                    "active": True,
                    "requires_undisguised": True,
                    "recognition_check_stat": "luck",
                    "gm_triggered": True,
                    "default_reaction_bias": "friendlier",
                    "source_ability": "Celebrity",
                },
            ),
        },
    ],
    source_type="adventure",
)