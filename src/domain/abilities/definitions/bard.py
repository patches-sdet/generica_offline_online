from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    aura,
    heal_hp,
    heal_stamina,
    scaled_derived_buff,
    scaled_stat_buff,
)
from domain.conditions import IS_ALLY, IS_ENEMY
from domain.effects.base import Effect, EffectContext
from domain.effects.conditional import CompositeEffect
from domain.effects.special.roll import RollModifierEffect


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _bard_level(character) -> int:
    return character.get_progression_level("adventure", "Bard", 0)


def _per_ten(ability_name: str):
    """
    For songs that heal / pulse by 'every fraction of ten points'
    in the skill. Intentionally rounds down.
    """
    return lambda c: _ability_level(c, ability_name) // 10


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


# Custom effects / placeholders

class BorrowedSkillPlaceholderEffect(Effect):
    """
    Placeholder for bardic borrowed-skill slotting.
    Stores the slot requirements and later-selected skill without pretending
    the selection UI / validation / registry lookup already exists.
    """

    def __init__(self, slot_name: str, tier: int, required_job_level: int):
        self.slot_name = slot_name
        self.tier = tier
        self.required_job_level = required_job_level

    def apply(self, context: EffectContext) -> None:
        states = getattr(context.source, "states", None)
        if states is None:
            context.source.states = {}
            states = context.source.states

        states[self.slot_name] = {
            "slot_name": self.slot_name,
            "tier": self.tier,
            "required_job_level": self.required_job_level,
            "chosen_skill": states.get(self.slot_name, {}).get("chosen_skill"),
            "forbid_tags": {"godspell", "darkspell"},
            "source_ability": self.slot_name.replace("_", " ").title(),
        }


class SongOfClarityPlaceholderEffect(Effect):
    """
    Runtime-facing placeholder for sanity / moxie restoration aura.
    Uses explicit state because the existing demonstrated helper set only
    confirms HP and stamina healing wrappers.
    """

    def apply(self, context: EffectContext) -> None:
        states = getattr(context.source, "states", None)
        if states is None:
            context.source.states = {}
            states = context.source.states

        states["song_of_clarity_active"] = _active_song_payload(
            context.source,
            "Song of Clarity",
            {
                "targets": "allies_in_earshot",
                "heal_sanity_per_tick": _ability_level(context.source, "Song of Clarity") // 10 * 2,
                "heal_moxie_per_tick": _ability_level(context.source, "Song of Clarity") // 10 * 2,
                "cost_per_minute": 20,
            },
        )


class SaltySongPlaceholderEffect(Effect):
    """
    Runtime-facing placeholder for ongoing moxie damage aura.
    """

    def apply(self, context: EffectContext) -> None:
        states = getattr(context.source, "states", None)
        if states is None:
            context.source.states = {}
            states = context.source.states

        states["salty_song_active"] = _active_song_payload(
            context.source,
            "Salty Song",
            {
                "targets": "everyone_in_earshot",
                "damage_pool": "moxie",
                "damage_formula": {
                    "base": _ability_level(context.source, "Salty Song"),
                    "minus_defense": "cool",
                    "minimum": 1,
                },
                "cost_per_minute": 10,
            },
        )


class PainfulSongPlaceholderEffect(Effect):
    """
    Runtime-facing placeholder for ongoing HP damage aura.
    """

    def apply(self, context: EffectContext) -> None:
        states = getattr(context.source, "states", None)
        if states is None:
            context.source.states = {}
            states = context.source.states

        states["painful_song_active"] = _active_song_payload(
            context.source,
            "Painful Song",
            {
                "targets": "everyone_in_earshot",
                "damage_pool": "hp",
                "damage_formula": {
                    "base": _ability_level(context.source, "Painful Song"),
                    "minus_defense": "armor",
                    "minimum": 1,
                },
                "cost_per_minute": 25,
            },
        )


class SickRiffPlaceholderEffect(Effect):
    """
    Runtime-facing placeholder for the Bard's sonic attack.
    """

    def apply(self, context: EffectContext) -> None:
        states = getattr(context.source, "states", None)
        if states is None:
            context.source.states = {}
            states = context.source.states

        states["sick_riff_ready"] = {
            "active": True,
            "attack_stat": "charisma",
            "skill_name": "Sick Riff",
            "target_stat": "willpower",
            "damage_pool": "moxie",
            "source_ability": "Sick Riff",
        }


class BandPracticeEffect(Effect):
    """
    Enables simultaneous use of multiple bard songs for a limited duration.
    """

    def apply(self, context: EffectContext) -> None:
        states = getattr(context.source, "states", None)
        if states is None:
            context.source.states = {}
            states = context.source.states

        states["band_practice_active"] = {
            "active": True,
            "duration_turns": _ability_level(context.source, "Band Practice"),
            "allow_multiple_bard_songs": True,
            "restrict_actions_to_move_only": True,
            "source_ability": "Band Practice",
        }


class CelebrityEffect(Effect):
    """
    Passive recognition-state placeholder for social / GM-facing handling.
    """

    def apply(self, context: EffectContext) -> None:
        states = getattr(context.source, "states", None)
        if states is None:
            context.source.states = {}
            states = context.source.states

        states["celebrity_status"] = {
            "active": True,
            "requires_undisguised": True,
            "recognition_check_stat": "luck",
            "gm_triggered": True,
            "default_reaction_bias": "friendlier",
            "source_ability": "Celebrity",
        }


# Bard

build_job("Bard", [

    # Level 1

    {
        "name": "Borrowed Skill I",
        "description": (
            "The Bard may permanently slot any Tier One, level 1 adventuring job skill "
            "into this borrowed-skill slot. Godspells and darkspells may not be chosen. "
            "This is currently stored as a structured placeholder until borrowed-skill "
            "selection and validation are implemented."
        ),
        "duration": "Permanent",
        "effects": BorrowedSkillPlaceholderEffect(
            slot_name="borrowed_skill_1",
            tier=1,
            required_job_level=1,
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Distracting Song",
        "cost": 5,
        "cost_pool": "moxie",
        "description": (
            "Costs 5 moxie per minute of use. Enemies within earshot suffer a debuff to "
            "Charisma, Perception, and Willpower equal to the level of this skill. "
            "A Bard can only ever have one song active at a time unless Band Practice is active."
        ),
        "duration": "Until Ceased",
        "effects": aura(
            scaled_stat_buff(
                scale_fn=lambda c: c.get_ability_effective_level("Distracting Song"),
                stats={
                    "charisma": -1,
                    "perception": -1,
                    "willpower": -1,
                },
                condition=IS_ENEMY,
            ),
            aura_id="bard_song",
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Heartening Song",
        "cost": 5,
        "cost_pool": "moxie",
        "description": (
            "Costs 5 moxie per minute of use. Allies within earshot gain a bonus to Strength "
            "and attack rolls equal to the level of this skill. A Bard can only ever have one "
            "song active at a time unless Band Practice is active."
        ),
        "duration": "Until Ceased",
        "effects": aura(
            CompositeEffect([
                scaled_stat_buff(
                    scale_fn=lambda c: c.get_ability_effective_level("Heartening Song"),
                    stats={"strength": 1},
                    condition=IS_ALLY,
                ),
                RollModifierEffect(
                    scale_fn=lambda c: c.get_ability_effective_level("Heartening Song"),
                    source_tag="heartening_song",
                    condition=IS_ALLY,
                ),
            ]),
            aura_id="bard_song",
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    {
        "name": "Just That Cool",
        "description": (
            "Bards are so cool that they gain a bonus to their Cool equal to their Bard level. "
            "This skill has no levels."
        ),
        "duration": "Passive Constant",
        "effects": scaled_derived_buff(
            scale_fn=lambda c: c.get_progression_level("adventure", "Bard", 0),
            stat="cool",
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Rejuvenating Song",
        "cost": 5,
        "cost_pool": "moxie",
        "description": (
            "Costs 5 moxie per minute of use. Allies within earshot heal HP and stamina each turn. "
            "The healing rate is equal to one point of each per full ten levels in this skill. "
            "A Bard can only ever have one song active at a time unless Band Practice is active."
        ),
        "duration": "Until Ceased",
        "effects": aura(
            CompositeEffect([
                heal_hp(
                    scale_fn=_per_ten("Rejuvenating Song"),
                    condition=IS_ALLY,
                ),
                heal_stamina(
                    scale_fn=_per_ten("Rejuvenating Song"),
                    condition=IS_ALLY,
                ),
            ]),
            aura_id="bard_song",
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Borrowed Skill V",
        "description": (
            "The Bard may permanently slot any Tier One, level 5 adventuring job skill "
            "into this borrowed-skill slot. Godspells and darkspells may not be chosen. "
            "This is currently stored as a structured placeholder until borrowed-skill "
            "selection and validation are implemented."
        ),
        "duration": "Permanent",
        "effects": BorrowedSkillPlaceholderEffect(
            slot_name="borrowed_skill_5",
            tier=1,
            required_job_level=5,
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Fortune's Fool",
        "description": (
            "The Bard's luck becomes absurdly reliable. They gain a bonus to Fortune equal "
            "to their Bard level. This skill has no levels."
        ),
        "duration": "Passive Constant",
        "effects": scaled_derived_buff(
            scale_fn=lambda c: c.get_progression_level("adventure", "Bard", 0),
            stat="fortune",
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Salty Song",
        "cost": 10,
        "cost_pool": "moxie",
        "description": (
            "Costs 10 moxie per minute of use. Everyone within earshot takes ongoing moxie damage "
            "equal to this skill minus Cool, minimum 1. A Bard can only ever have one song active "
            "at a time unless Band Practice is active."
        ),
        "duration": "Until Ceased",
        "effects": SaltySongPlaceholderEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": True,
        "target": "everyone_in_earshot",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Borrowed Skill X",
        "description": (
            "The Bard may permanently slot any Tier One, level 10 adventuring job skill "
            "into this borrowed-skill slot. Godspells and darkspells may not be chosen. "
            "This is currently stored as a structured placeholder until borrowed-skill "
            "selection and validation are implemented."
        ),
        "duration": "Permanent",
        "effects": BorrowedSkillPlaceholderEffect(
            slot_name="borrowed_skill_10",
            tier=1,
            required_job_level=10,
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 10,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Song of Clarity",
        "cost": 20,
        "cost_pool": "moxie",
        "description": (
            "Costs 20 moxie per minute of use. Allies within earshot heal sanity and moxie each turn. "
            "The healing rate is two points of each per full ten levels in this skill. A Bard can only "
            "ever have one song active at a time unless Band Practice is active."
        ),
        "duration": "Until Ceased",
        "effects": SongOfClarityPlaceholderEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 10,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Borrowed Skill XV",
        "description": (
            "The Bard may permanently slot any Tier One, level 15 adventuring job skill "
            "into this borrowed-skill slot. Godspells and darkspells may not be chosen. "
            "This is currently stored as a structured placeholder until borrowed-skill "
            "selection and validation are implemented."
        ),
        "duration": "Permanent",
        "effects": BorrowedSkillPlaceholderEffect(
            slot_name="borrowed_skill_15",
            tier=1,
            required_job_level=15,
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 15,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Painful Song",
        "cost": 25,
        "cost_pool": "moxie",
        "description": (
            "Costs 25 moxie per minute of use. Everyone within earshot takes ongoing HP damage "
            "equal to this skill minus Armor, minimum 1. A Bard can only ever have one song active "
            "at a time unless Band Practice is active."
        ),
        "duration": "Until Ceased",
        "effects": PainfulSongPlaceholderEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 15,
        "scales_with_level": True,
        "target": "everyone_in_earshot",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Borrowed Skill XX",
        "description": (
            "The Bard may permanently slot any Tier One, level 20 adventuring job skill "
            "into this borrowed-skill slot. Godspells and darkspells may not be chosen. "
            "This is currently stored as a structured placeholder until borrowed-skill "
            "selection and validation are implemented."
        ),
        "duration": "Permanent",
        "effects": BorrowedSkillPlaceholderEffect(
            slot_name="borrowed_skill_20",
            tier=1,
            required_job_level=20,
        ),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Sick Riff",
        "cost": 30,
        "cost_pool": "stamina",
        "description": (
            "The Bard unleashes a sonic attack. This is a Charisma + Sick Riff attack against "
            "the target's Willpower, inflicting moxie damage on success. Stored as a structured "
            "attack placeholder until full contested roll and damage resolution are implemented."
        ),
        "duration": "1 attack",
        "effects": SickRiffPlaceholderEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 20,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Band Practice",
        "cost": 200,
        "cost_pool": "moxie",
        "description": (
            "The Bard may activate all song skills at once, ignoring the normal one-song limit. "
            "While Band Practice is active, the Bard may take no action other than movement."
        ),
        "duration": "1 minute per skill level",
        "effects": BandPracticeEffect(),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Celebrity",
        "description": (
            "While undisguised, the Bard may be recognized even by people who logically should not know them. "
            "Recognition is generally luck-based and GM-triggered. Those who recognize the Bard usually "
            "treat them more favorably. This skill has no levels."
        ),
        "duration": "Passive Constant",
        "effects": CelebrityEffect(),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

], source_type="adventure")