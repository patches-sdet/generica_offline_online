from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import action_override, scaled_derived_buff, scaled_stat_buff, conditional_effect, heal_hp, skill_check
from domain.effects.conditional import CompositeEffect

ADORABLE = {
    "name": "Adorable",
    "type": "skill",
    "description": "When you do something cute in front of an audience, or onlookers blame you for something that isn't your fault, this can improve their attitude towards you. Roll Charisma plus your level in this skill against the willpower of all affected.",
    "effects": skill_check(
            ability="Charisma",
            stat="willpower",
            difficulty=lambda target: target.roll_willpower(),
            on_success=lambda ctx, target: ctx.modify_attitude_towards(target, "friendly"),
            ),
    "scales_with_level": True,
}

ANIMALISTIC_INTERFACE = {
    "name": "Animalistic Interface",
    "required_level": 1,
    "type": "passive",
    "description": "Allows the beast to use their racial skills without vocalization. All racial job skills that are not passives may be activated as the situation and instinct require.",
    "effects": [],
    "scales_with_level": False,
}

BEAST = {
    "name": "Beast",
    "required_level": 1,
    "type": "passive",
    "description": "You may not spend grind tokens to raise your Intelligence, and it can not exceed 19. This skill is removed if you acquire a racial job that doesn't have the Beast skill.",
    "effects": action_override(
            lambda ctx: ctx.modify_intelligence(maximum=19, prevent_grind_token_spending=True)
            ),
        "scales_with_level": False,
}

BEAST_BLOOD = {
    "name": "Beast Blood",
    "required_level": 1,
    "type": "passive",
    "description": "Choose 1 level 1 skill from the Beast racial job. You gain that skill and replace this skill with it.",
    "effects": [], # need to figure out how to implement this skill swap thing for this, godspell, darkspell, etc. Maybe also need to be refactored to use this system instead of granting skills directly.
    "scales_with_level": False,
}

CLAW_SWIPES= {
    "name": "Claw Swipes",
    "type": "skill",
    "cost": 5,
    "cost_pool": "stamina",
    "description": "For the next two turns, all of your brawling attacks inflict bonus damage equal to your level in this skill divided by two.",
    "effects": action_override(
            lambda ctx: ctx.modify_next_n_attacks(
                2,
                lambda attack: attack.add_bonus("damage", ctx.source.ability_levels["Claw Swipes"] // 2),
                condition=lambda attack: attack.type == "brawling",
                )
            ),
    "scales_with_level": True,
}

DARKSPAWN= {
    "name": "Darkspawn",
    "description": "You gain a buff to all attributes equal to two times your race job level while in darkness, and can see in normal darkness. This buff does not increase the maximums of the associated pools.",
    "effects": conditional_effect(
            effect=scaled_stat_buff(
                scale_fn=lambda c: c.get_progression_level_for_ability("race","Darkspawn"),
                stats={"strength": 2, "constitution": 2, "intelligence": 2, "wisdom": 2, "dexterity": 2, "agility": 2, "charisma": 2, "willpower": 2, "perception": 2, "luck": 2},
            ),
            condition=lambda ctx, target: ctx.source.is_in_darkness(),
        ),
    "is_skill": True,
    "scales_with_level": True,
    "type": "skill",
}

FORAGE = {
    "name": "Forage",
    "type": "skill",
    "cost": 10,
    "cost_pool": "stamina",
    "description": "This skill adds its level to your Perception when searching for food, water, or other natural resources. At higher levels, it may be used to locate specific resources.",
    "effects": scaled_stat_buff (
            scale_fn=lambda ctx: ctx.source.ability_levels["Forage"],
            stats={"perception": 1},
            condition=lambda ctx: ctx.action_type in ("forage", "search_nature"),
        ),
    "scales_with_level": True,
}

HAUNTING_SPIRIT_UNDEAD = {
    "name": "Haunting Spirit (Undead)",
    "required_level": 1,
    "type": "passive",
    "description": "You are undead. You are affected by spells that affect undead, are healed by shadow damage, and harmed by healing effects. You are also immune to the following: Bleeding, Dehydrated, Diseased, Drowning, Drunk, Hungover, Hungry, Poisoned, and Thirsty.",
    "effects": [],
    "scales_with_level": False,
}

HUMAN_BLOOD = {
    "name": "Human Blood",
    "required_level": 1,
    "type": "passive",
    "description": "Choose 1 level 1 skill from the Human racial job. You gain that skill and replace this skill with it.",
    "effects": [], # need to figure out how to implement this skill swap thing. For this, godspell, darkspell, etc. maybe also need to be refactored to use this system instead of granting skills directly.
    "scales_with_level": False,
}

GOLEM_BODY = {
    "name": "Golem Body",
    "required_level": 1,
    "type": "passive",
    "description": "Your body has no organs and is made from inorganic or once-organic material infused with magic. You ignore the following conditions: Bleeding, Dehydrated, Diseased, Drunk, Gassy, Hungover, Hungry, Nauseated, Poisoned, Starving, Thirsty. You have a chance to ignore the following condtions with a Constitution plus Golem Body skill roll against a difficuulty of 120: Blinded, Deafened, Hobblede, Numb, Paralyzed, Slowed, and Stunned. You are unaffected by light and shadow-based damage and healing. You cannot eat, drink, or sleep. You require skills or items to sleep to recover your pools.",
    "effects": CompositeEffect([
            lambda ctx: ctx.modify_condition_immunities({"Bleeding", "Dehydrated", "Diseased", "Drunk", "Gassy", "Hungover", "Hungry", "Nauseated", "Poisoned", "Starving", "Thirsty"}),
            lambda ctx: ctx.on_event(
                "gain_condition",
                lambda event_ctx: event_ctx.prevent_condition() if event_ctx.condition in {"Blinded", "Deafened", "Hobblede", "Numb", "Paralyzed", "Slowed", "Stunned"} and event_ctx.source.roll_constitution_plus_skill("Golem Body") >= 120 else None
            ),
            lambda ctx: ctx.modify_light_and_shadow_immunity(True),
            lambda ctx: ctx.modify_sleep_requirements(increase=True),
        ]),
    "is_skill": True,
    "scales_with_level": True,
}

GROOM = {
    "name": "Groom",
    "type": "skill",
    "cost": 5,
    "cost_pool": "sanity",
    "description": "Groom yourself or a nearby ally, restoring 5 HP per turn. You must remain stationary while using this skill, and cannot engage in any other actions.",
    "effects": heal_hp (
            scale_fn=lambda ctx: 5,
            condition=lambda ctx: ctx.action_type == "groom",
            ),
    "scales_with_level": False,
}

MAGIC_RESISTANCE = {
    "name": "Magic Resistance",
    "type": "passive",
    "description": " You have a chance of negating non-beneficial magic cast on you. When anyone attempts such a spell, you may add your level in this skill to whichever attribute they're rolling against. This is a buff that only affects individual rolls.",
    "effects": scaled_stat_buff(
            scale_fn=lambda ctx: ctx.source.ability_levels["Magic Resistance"],
            stats={"willpower": 1},
            condition=lambda ctx: ctx.action_type == "targeted_by_non_beneficial_magic",
        ),
    "is_skill": True,
    "scales_with_level": True,
}

NINE_LIVES = {
    "name": "Nine Lives",
    "type": "passive",
    "description": "When you would be reduced to 0 HP, you can choose to lose an amount of Fortune equal to your Cat job level, and instantly heal to 1 HP, and your Nine Lives skill increases by 1. Once it reaches level 10, it disappears from your skill list.",
    "effects": [], # Complicated resolution, might need a custom pattern or effect.
    "scales_with_level": False,
}

SCENTS_AND_SENSIBILITY = {
    "name": "Scents and Sensibility",
    "type": "passive",
    "description": "This skill adds its level to your Perception, but only when using your nose. It also allows you to identify creatures by scent, so long as you've encountered them before.",
    "effects": scaled_stat_buff(
            scale_fn=lambda ctx: ctx.source.ability_levels["Scents and Sensibility"],
            stats={"perception": 1},
            condition=lambda ctx: ctx.action_type == "use_scent",
        ),
        "is_skill": True,
    "scales_with_level": True,
}

STURDY = {
    "name": "Sturdy",
    "type": "skill",
    "cost": 20,
    "cost_pool": "stamina",
    "description": "Activate this skill when you would lose more HP than you currently have. Roll Constitution plus your level in this skill. If the roll exceeds the amount of HP you would lose, you instead lose all but 1 HP. You can only use Sturdy once per turn.",
    "effects": [], 
    "scales_with_level": True,
}





SHARED_RACIAL_ABILITIES = [
    ADORABLE,
    ANIMALISTIC_INTERFACE,
    BEAST,
    BEAST_BLOOD,
    CLAW_SWIPES,
    DARKSPAWN,
    FORAGE,
    HAUNTING_SPIRIT_UNDEAD,
    HUMAN_BLOOD,
    GOLEM_BODY,
    GROOM,
    MAGIC_RESISTANCE,
    NINE_LIVES,
    SCENTS_AND_SENSIBILITY,
    STURDY,
]

for definition in SHARED_RACIAL_ABILITIES:
    build_shared_ability("shared.utility", definition, source_type="race")