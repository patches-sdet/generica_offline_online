from domain.abilities.builders._job_builder import build_shared_ability
from domain.abilities.patterns import action_override, buff, heal, skill_check
from src.domain.effects.resource_effects import Heal

ADORABLE = {
    "name": "Adorable",
    "type": "skill",
    "description": "When you do something cute in front of an audience, or onlookers blame you for something that isn't your fault, this can improve their attitude towards you. Roll Charisma plus your level in this skill against the willpower of all affected.",
    "effects": lambda ctx: [
        skill_check(
            ability="Charisma",
            stat="willpower",
            difficulty=lambda ctx, target: target.roll_willpower(),
            on_success=lambda ctx, target: ctx.modify_attitude_towards(target, "friendly"),)
    ],
    "scales_with_level": True,
}

ANIMALISTIC_INTERFACE = {
    "name": "Animalistic Interface",
    "type": "passive",
    "description": "Allows the beast to use their racial skills without vocalization. All racial job skills that are not passives may be activated as the situation and instinct require.",
    "effects": [],
    "scales_with_level": False,
}

BEAST = {
    "name": "Beast",
    "type": "passive",
    "description": "You may not spend grind tokens to raise your Intelligence, and it can not exceed 19. This skill is removed if you acquire a racial job that doesn't have the Beast skill.",
    "effects": lambda ctx: [
        action_override(
            lambda ctx: ctx.modify_intelligence(maximum=19, prevent_grind_token_spending=True)
            ),
        ],
        "scales_with_level": False,
},

BEAST_BLOOD = {
    "name": "Beast Blood",
    "type": "passive",
    "description": "Choose 1 level 1 skill from the Beast racial job. You gain that skill and replace this skill with it.",
    "effects": [], # need to figure out how to implement this skill swap thing. For this, godspell, darkspell, etc. maybe also need to be refactored to use this system instead of granting skills directly.
    "scales_with_level": False,
},

CLAW_SWIPES= {
    "name": "Claw Swipes",
    "type": "skill",
    "cost": 5,
    "cost_pool": "stamina",
    "description": "For the next two turns, all of your brawling attacks inflict bonus damage equal to your level in this skill divided by two.",
    "effects": lambda ctx: [
        action_override(
            lambda ctx: ctx.modify_next_n_attacks(
                2,
                lambda attack: attack.add_bonus("damage", ctx.source.ability_levels["Claw Swipes"] // 2),
                condition=lambda attack: attack.type == "brawling"
                )
            ),
        ],
        "scales_with_level": True,
},

FORAGE = {
    "name": "Forage",
    "type": "skill",
    "cost": 10,
    "cost_pool": "stamina",
    "description": "This skill adds its level to your Perception when searching for food, water, or other natural resources. At higher levels, it may be used to locate specific resources.",
    "effects": lambda ctx: [
        buff (
            scale_fn=lambda ctx: ctx.source.ability_levels["Forage"],
            stats={"perception": 1},
            condition=lambda ctx: ctx.action_type in ("forage", "search_nature"),
        ),
    ],
    "scales_with_level": True,
},

HAUNTING_SPIRIT_UNDEAD = {
    "name": "Haunting Spirit (Undead)",
    "type": "passive",
    "description": "You are undead. You are affected by spells that affect undead, are healed by shadow damage, and harmed by healing effects. You are also immune to the following: Bleeding, Dehydrated, Diseased, Drowning, Drunk, Hungover, Hungry, Poisoned, and Thirsty.",
    "effects": [],
    "scales_with_level": False,
},

HUMAN_BLOOD = {
    "name": "Human Blood",
    "type": "passive",
    "description": "Choose 1 level 1 skill from the Human racial job. You gain that skill and replace this skill with it.",
    "effects": [], # need to figure out how to implement this skill swap thing. For this, godspell, darkspell, etc. maybe also need to be refactored to use this system instead of granting skills directly.
    "scales_with_level": False,
},

GROOM = {
    "name": "Groom",
    "type": "skill",
    "cost": 5,
    "cost_pool": "sanity",
    "description": "Groom yourself or a nearby ally, restoring 5 HP per turn. You must remain stationary while using this skill, and cannot engage in any other actions.",
    "effects": lambda ctx: [
        heal (
            scale_fn=lambda ctx: 5,
            condition=lambda ctx: ctx.action_type == "groom",
            ),
        ],
        "scales_with_level": False,
},

NINE_LIVES = {
    "name": "Nine Lives",
    "type": "passive",
    "description": "When you would be reduced to 0 HP, you can choose to lose an amount of Fortune equal to your Cat job level, and instantly heal to 1 HP, and your Nine Lives skill increases by 1. Once it reaches level 10, it disappears from your skill list.",
    "effects": [], # Complicated resolution, might need a custom pattern or effect.
    "scales_with_level": False,
},

SCENTS_AND_SENSIBILITY = {
    "name": "Scents and Sensibility",
    "type": "passive",
    "description": "This skill adds its level to your Perception, but only when using your nose. It also allows you to identify creatures by scent, so long as you've encountered them before.",
    "effects": lambda ctx: [
        buff (
            scale_fn=lambda ctx: ctx.source.ability_levels["Scents and Sensibility"],
            stats={"perception": 1},
            condition=lambda ctx: ctx.action_type == "use_scent",
        ),
    ],
},

TOUGHNESS = {
    "name": "Toughness",
    "type": "passive",
    "description": "Can increase whenever you take serious damage. Increases your Maximum HP by two for each level this skill has.",
    "effects": lambda ctx: [
        buff (
            scale_fn=lambda ctx: ctx.source.ability_levels["Toughness"] * 2,
            stats={"max_hp": 1},
            condition=lambda ctx: ctx.damage_taken >= {"constitution" + "toughness"},
        ),
    ],
}

build_shared_ability("shared.utility", ANIMALISTIC_INTERFACE)