from domain.abilities import ability_level, progression_level
from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    composite,
    inspect,
    modify_next_attack,
    scaled_derived_buff,
    skill_check,
)

def _set_attack_attr(attack, key: str, value) -> None:
    setattr(attack, key, value)

def _dark_chant_damage_pool(source) -> str:
    """
    Daemon -> moxie
    Djinn -> fortune
    Old One -> sanity
    Falls back to sanity if no patron/faction is yet resolved.
    """
    states = getattr(source, "states", {}) or {}

    patron = None
    darkspell = states.get("darkspell_access", {})
    if isinstance(darkspell, dict):
        patron = darkspell.get("patron_type") or darkspell.get("patron")

    patron = (patron or "").lower()

    if "daemon" in patron:
        return "moxie"
    if "djinn" in patron:
        return "fortune"
    if "old one" in patron or "old_one" in patron:
        return "sanity"

    return "sanity"

# Attack modifiers

def _unholy_smite_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "bonus_damage", ability_level(ctx.source, "Unholy Smite"))
    _set_attack_attr(attack, "damage_type", "dark")
    _set_attack_attr(attack, "unholy_smite", True)

# Cultist

build_job(
    "Cultist",
    [
        # Level 1
        {
            "name": "Conceal Status",
            "type": "skill",
            "cost": 5,
            "cost_pool": "moxie",
            "target": "self",
            "required_level": 1,
            "scales_with_level": True,
            "is_spell": False,
            "description": (
                "While active, the Cultist presents a false status to outside investigators. "
                "Any attempt to inspect them must overcome the Cultist's Charisma plus Conceal Status. "
                "This is not a spell."
            ),
            "duration": "1 Hour",
            "effects": apply_state(
                "conceal_status_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_hours": 1,
                    "false_status": True,
                    "inspect_resist_stat": "charisma",
                    "inspect_resist_bonus": ability_level(source, "Conceal Status"),
                    "source_ability": "Conceal Status",
                },
            ),
        },
        {
            "name": "Curses",
            "type": "skill",
            "cost": 1,
            "cost_pool": "fortune",
            "target": "enemy",
            "required_level": 1,
            "scales_with_level": False,
            "is_spell": True,
            "description": (
                "The Cultist spends Fortune to inflict a curse on a target, decreasing one chosen attribute "
                "by one point per Fortune invested. The target resists with Willpower against the Cultist's "
                "Luck plus Curses. The effect lasts until cancelled, and a Cultist may only maintain one curse "
                "at a time. This skill is a spell."
            ),
            "duration": "Until Cancelled",
            "effects": skill_check(
                ability="Curses",
                stat="luck",
                difficulty=lambda ctx, target: getattr(
                    getattr(target, "attributes", None),
                    "willpower",
                    0,
                ),
                on_success=apply_state(
                    "cursed",
                    value_fn=lambda source: {
                        "source": source,
                        "chosen_stat": None,
                        "selection_required": True,
                        "penalty": "from_spent_amount_min_1",
                        "duration": "until_cancelled",
                        "single_curse_per_target": True,
                        "one_active_curse_from_source": True,
                        "source_ability": "Curses",
                    },
                ),
            ),
        },
        {
            "name": "Darkspell",
            "type": "skill",
            "target": "self",
            "required_level": 1,
            "scales_with_level": False,
            "is_spell": False,
            "description": (
                "The Cultist gains access to the unique Darkspell of their chosen patron. "
                "This is a structured placeholder until patron selection and darkspell binding are implemented."
            ),
            "duration": "Varies",
            "effects": apply_state(
                "darkspell_access",
                value_fn=lambda source: {
                    "active": True,
                    "selection_required": True,
                    "patron": getattr(source, "states", {}).get("darkspell_access", {}).get("patron"),
                    "chosen_darkspell": getattr(source, "states", {}).get("darkspell_access", {}).get("chosen_darkspell"),
                    "source_ability": "Darkspell",
                },
            ),
        },
        {
            "name": "Enhance Pain",
            "type": "skill",
            "cost": 10,
            "cost_pool": "sanity",
            "target": "enemy",
            "required_level": 1,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Cultist rolls Intelligence plus Enhance Pain against the target's Wisdom. "
                "If successful, any damage the target suffers while afflicted is increased by the Cultist's level. "
                "This skill is a spell."
            ),
            "duration": "1 Turn per Level",
            "effects": skill_check(
                ability="Enhance Pain",
                stat="intelligence",
                difficulty=lambda ctx, target: getattr(
                    getattr(target, "attributes", None),
                    "wisdom",
                    0,
                ),
                on_success=apply_state(
                    "enhance_pain",
                    value_fn=lambda source: {
                        "source": source,
                        "duration_turns": ability_level(source, "Enhance Pain"),
                        "bonus_damage_taken": progression_level(source, "adventure", "Cultist"),
                        "source_ability": "Enhance Pain",
                    },
                ),
            ),
        },
        {
            "name": "Occult Eye",
            "type": "skill",
            "cost": 10,
            "cost_pool": "sanity",
            "target": "object_area_or_being",
            "required_level": 1,
            "scales_with_level": False,
            "is_spell": True,
            "description": (
                "The Cultist examines an object, area, or being for traces of occult contamination, "
                "and may safely read blasphemous texts without risking damage. This skill is a spell."
            ),
            "duration": "1 Minute",
            "effects": inspect(
                reveal_fn=lambda ctx, target: {
                    "occult_traces": getattr(target, "occult_traces", None),
                    "contamination_level": getattr(target, "contamination_level", None),
                    "blasphemous_text": getattr(target, "blasphemous_text", None),
                    "safe_to_read_with_occult_eye": True,
                }
            ),
        },
        {
            "name": "Transfer Wounds",
            "type": "skill",
            "cost": 10,
            "cost_pool": "fortune",
            "target": "enemy",
            "required_level": 1,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Cultist makes an unarmed attack on a living foe. On a successful hit, normal damage is not dealt. "
                "Instead, the target takes damage equal to Transfer Wounds level, bypassing all defenses, and the Cultist "
                "heals the same amount. This skill is a spell."
            ),
            "duration": "1 Attack",
            "effects": apply_state(
                "transfer_wounds_ready",
                value_fn=lambda source: {
                    "active": True,
                    "attack_type": "unarmed",
                    "living_targets_only": True,
                    "damage_amount": ability_level(source, "Transfer Wounds"),
                    "healing_amount": ability_level(source, "Transfer Wounds"),
                    "bypass_all_defenses": True,
                    "replace_normal_damage": True,
                    "source_ability": "Transfer Wounds",
                },
            ),
        },

        # Level 5
        {
            "name": "Dark Chant",
            "type": "skill",
            "cost": 10,
            "cost_pool": "moxie",
            "target": "everyone_in_earshot",
            "required_level": 5,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Cultist intones blasphemous words that damage the minds of those who hear them. "
                "Cultists are immune. The damage pool depends on patron faction: daemon deals Moxie, djinn deals Fortune, "
                "and old one deals Sanity. When multiple Dark Chants are active, only the most skilled one actually deals damage. "
                "This skill is a spell."
            ),
            "duration": "Until Cancelled",
            "effects": apply_state(
                "dark_chant_active",
                value_fn=lambda source: {
                    "active": True,
                    "damage_pool": _dark_chant_damage_pool(source),
                    "damage_amount": ability_level(source, "Dark Chant"),
                    "cost_moxie_per_turn": 10,
                    "cultists_immune": True,
                    "resist_roll": {
                        "attack_stat": "intelligence",
                        "skill_name": "Dark Chant",
                        "target_stat": "willpower",
                        "success_halves_damage": True,
                    },
                    "reduced_by_relevant_defense": True,
                    "highest_skill_dark_chant_only": True,
                    "source_ability": "Dark Chant",
                },
            ),
        },
        {
            "name": "Servant of Darkness",
            "type": "passive",
            "target": "self",
            "required_level": 5,
            "scales_with_level": False,
            "is_spell": False,
            "description": (
                "The Cultist gains a bonus to Fate equal to their Cultist level. "
                "This skill has no levels."
            ),
            "duration": "Passive Constant",
            "effects": scaled_derived_buff(
                scale_fn=lambda source: progression_level(source, "adventure", "Cultist"),
                stat="fate",
            ),
        },
        {
            "name": "Unhinged Mind",
            "type": "skill",
            "cost": 1,
            "cost_pool": "fortune",
            "target": "self",
            "required_level": 5,
            "scales_with_level": False,
            "is_spell": False,
            "description": (
                "The Cultist commits Fortune to increase maximum Sanity on a one-for-one basis. "
                "Committed Fortune lowers maximum Fortune and acts as a Sanity buff until cancelled. "
                "Once cancelled, the Fortune must recharge normally. This skill has no levels."
            ),
            "duration": "Until Cancelled",
            "effects": apply_state(
                "unhinged_mind_active",
                value_fn=lambda source: {
                    "active": True,
                    "committed_fortune": "from_spent_amount",
                    "bonus_max_sanity": "from_spent_amount",
                    "reduces_max_fortune": True,
                    "fortune_returns_normally_after_cancel": True,
                    "source_ability": "Unhinged Mind",
                },
            ),
        },

        # Level 10
        {
            "name": "Fevered Zeal",
            "type": "skill",
            "cost": 25,
            "cost_pool": "stamina",
            "target": "self",
            "required_level": 10,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "While active, the Cultist's Strength is buffed by the level of this skill, but they do not gain HP from it. "
                "Whenever the Cultist attacks, they take HP damage equal to Cultist level, bypassing all defenses. "
                "This skill is a spell."
            ),
            "duration": "1 Turn per Level",
            "effects": apply_state(
                "fevered_zeal_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_turns": ability_level(source, "Fevered Zeal"),
                    "strength_bonus": ability_level(source, "Fevered Zeal"),
                    "no_hp_from_strength_buff": True,
                    "self_damage_on_attack": progression_level(source, "adventure", "Cultist"),
                    "self_damage_pool": "hp",
                    "self_damage_bypasses_defenses": True,
                    "source_ability": "Fevered Zeal",
                },
            ),
        },
        {
            "name": "First Pact",
            "type": "skill",
            "cost": 100,
            "cost_pool": "sanity",
            "target": "ritual_space",
            "required_level": 10,
            "scales_with_level": False,
            "is_spell": True,
            "description": (
                "The Cultist sacrifices a small creature to call a permanent level 1 class one dark being "
                "of their patron's faction. Success is determined secretly by Intelligence plus First Pact "
                "against the being's Willpower. Critical success yields a loyal servant; a botch produces a "
                "subtle traitor. This skill is a spell."
            ),
            "duration": "Permanent",
            "effects": apply_state(
                "first_pact_cast",
                value_fn=lambda source: {
                    "active": True,
                    "sacrifice_requirement": "animal_or_equivalent",
                    "summon_level": 1,
                    "summon_class": 1,
                    "faction_matches_patron": True,
                    "secret_resolution": {
                        "stat": "intelligence",
                        "skill_name": "First Pact",
                        "target_stat": "willpower",
                        "critical_success_loyal": True,
                        "botch_subtle_traitor": True,
                    },
                    "permanent_service_until_destroyed": True,
                    "source_ability": "First Pact",
                },
            ),
        },

        # Level 15
        {
            "name": "Dark Bolt",
            "type": "skill",
            "cost": 30,
            "cost_pool": "sanity",
            "target": "enemy",
            "required_level": 15,
            "scales_with_level": False,
            "is_spell": True,
            "description": (
                "The Cultist blasts a target with dark energy using Intelligence plus Dark Bolt against Agility. "
                "This is dark-based damage, Armor applies, and its range is about thirty feet. This skill is a spell."
            ),
            "duration": "1 Attack",
            "effects": apply_state(
                "dark_bolt_ready",
                value_fn=lambda source: {
                    "active": True,
                    "attack_stat": "intelligence",
                    "skill_name": "Dark Bolt",
                    "target_stat": "agility",
                    "damage_type": "dark",
                    "range_feet": 30,
                    "armor_applies": True,
                    "source_ability": "Dark Bolt",
                },
            ),
        },
        {
            "name": "Unholy Smite",
            "type": "skill",
            "cost": 10,
            "cost_pool": "fortune",
            "target": "enemy",
            "required_level": 15,
            "scales_with_level": True,
            "is_spell": True,
            "description": (
                "The Cultist surrounds their weapon with a dark aura, increasing melee attack damage by one "
                "per level of this skill. This skill is a spell."
            ),
            "duration": "1 Minute per Level",
            "effects": modify_next_attack(_unholy_smite_modifier),
        },

        # Level 20
        {
            "name": "Heart of Darkness",
            "type": "passive",
            "target": "self",
            "required_level": 20,
            "scales_with_level": False,
            "is_spell": False,
            "description": (
                "The Cultist's Mental Fortitude and Cool are increased by their Cultist level, and "
                "unintelligent dark creatures of their patron's faction see them as one of their own. "
                "This skill has no levels."
            ),
            "duration": "Passive Constant",
            "effects": composite(
                scaled_derived_buff(
                    scale_fn=lambda source: progression_level(source, "adventure", "Cultist"),
                    stat="mental_fortitude",
                ),
                scaled_derived_buff(
                    scale_fn=lambda source: progression_level(source, "adventure", "Cultist"),
                    stat="cool",
                ),
                apply_state(
                    "heart_of_darkness_active",
                    value_fn=lambda source: {
                        "active": True,
                        "treated_as_dark_faction_creature": True,
                        "applies_to_unintelligent_dark_creatures": True,
                        "source_ability": "Heart of Darkness",
                    },
                ),
            ),
        },
        {
            "name": "Second Pact",
            "type": "skill",
            "cost": 200,
            "cost_pool": "sanity",
            "target": "ritual_space",
            "required_level": 20,
            "scales_with_level": False,
            "is_spell": True,
            "description": (
                "The Cultist sacrifices a sapient being to call a permanent level 1 class two or class three "
                "dark being of their patron's faction. Aside from the stronger offering and servant, it works "
                "like First Pact. This skill is a spell."
            ),
            "duration": "Permanent",
            "effects": apply_state(
                "second_pact_cast",
                value_fn=lambda source: {
                    "active": True,
                    "sacrifice_requirement": "sapient_being",
                    "summon_level": 1,
                    "summon_class_options": [2, 3],
                    "faction_matches_patron": True,
                    "secret_resolution": {
                        "stat": "intelligence",
                        "skill_name": "Second Pact",
                        "target_stat": "willpower",
                        "critical_success_loyal": True,
                        "botch_subtle_traitor": True,
                    },
                    "permanent_service_until_destroyed": True,
                    "source_ability": "Second Pact",
                },
            ),
        },

        # Level 25
        {
            "name": "Dark Augury",
            "type": "skill",
            "cost": 100,
            "cost_pool": "fortune",
            "target": "topic",
            "required_level": 25,
            "scales_with_level": False,
            "is_spell": True,
            "description": (
                "The Cultist sacrifices a sapient being and peers into its dying eyes to gain a glimpse of possible futures. "
                "The Cultist rolls Luck plus Dark Augury against a difficulty determined by the topic. "
                "This skill is a spell."
            ),
            "duration": "1 Minute",
            "effects": apply_state(
                "dark_augury_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_minutes": 1,
                    "sacrifice_requirement": "sapient_being",
                    "resolution": {
                        "stat": "luck",
                        "skill_name": "Dark Augury",
                        "difficulty_by_topic": True,
                        "simple_topic": 120,
                        "moderate_topic": 180,
                        "major_vision": 250,
                    },
                    "source_ability": "Dark Augury",
                },
            ),
        },
        {
            "name": "Rite of Reclamation",
            "type": "skill",
            "cost": 100,
            "cost_pool": "sanity",
            "target": "sapient_target",
            "required_level": 25,
            "scales_with_level": False,
            "is_spell": True,
            "description": (
                "The Cultist sacrifices an individual and strips them of their jobs, adding those unlocks to the Cultist. "
                "If the victim is in a party, the unlocks may instead go to a party member of the victim's choice. "
                "If another living sapient is closer than the Cultist, that being may receive the unlocks instead. "
                "This skill has no levels. This skill is a spell."
            ),
            "duration": "10 Minutes",
            "effects": apply_state(
                "rite_of_reclamation_active",
                value_fn=lambda source: {
                    "active": True,
                    "duration_minutes": 10,
                    "strips_target_jobs": True,
                    "adds_unlocks_to_cultist": True,
                    "redirect_to_victim_party_choice_if_in_party": True,
                    "redirect_to_nearest_living_sapient_if_closer": True,
                    "source_ability": "Rite of Reclamation",
                },
            ),
        },
    ],
    source_type="adventure",
)