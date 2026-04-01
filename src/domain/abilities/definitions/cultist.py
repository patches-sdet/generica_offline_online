from domain.abilities.definitions._job_builder import build_job
from domain.abilities.patterns import buff, conditional_damage, transfer_stat, scaled_derived_buff
from domain.conditions import IS_ALLY, IS_ENEMY
from domain.effects.special.damage import TransferEffect

build_job("Cultist", [

    # Passive
#    {
#        "name": "Faith",
#        "type": "passive",
#        "effects": lambda c: scaled_derived_buff(
#            stat="fate",
#            scale_fn=lambda c: c.get_adventure_level_by_name("Cultist", 0),
#        )(c),
#        "description": "Your Fate increases with Cultist level.",
#    },

    # Skills
    {
        "name": "Conceal Status",
        "type": "skill",
        "cost": 5,
        "cost_pool": "moxie",
        "target": "self",
        "effects": lambda caster, targets: [
            buff(
                scale_fn=lambda c: c.get_adventure_level_by_name("Cultist", 0),
                stats={"any": 1},
#                duration="1 Hour",
                )
            ],
        "description": "While this skill is active, you are considered to have a job of your choice if someone investigates your stats.\n     This is a Charisma plus the level of this skill versus an investigation roll."
        },
    {
    "name": "Curses",
    "type": "skill",
    "cost": "variable",
    "cost_pool": "fortune",
    "target": "enemy",
    "effects": lambda caster, targets, context: [
        scaled_derived_buff(
            stat=context.chosen_stat,
            scale_fn=lambda c, ctx: ctx.spent_amount,
            condition=IS_ENEMY,
#            duration="Until Canceled or Dispelled",
        )
    ],
},

    {
        "name": "Enhance Pain",
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "target": "enemy",
        "effects": lambda caster, targets: [
            conditional_damage(
                scale_fn=lambda c: c.get_adventure_level_by_name("Cultist", 0),
#                duration="1 Turn/level",
            )
        ],
        "description": "Enemies afflicted by this debuff take additional damage equal to your Cultist level. This is a Intelligence plus\n     the level of this skill versus their wisdom roll. Lasts until canceled or dispelled.\n     This skill is a spell.",
    },

    {
        "name": "Occult Eye",
        "type": "skill",
        "cost": 10,
        "cost_pool": "sanity",
        "target": "self",
        "effects": lambda caster, targets: []    # TODO: This may need a new pattern that would allow "This skill allows them
                                                # to examine an object, area, or being for traces of occult contamination.
                                                # This also allows them to read blasphemous tomes, scrolls, and inscriptions
                                                # without risking damage."
    },

    {
    "name": "Transfer Wounds",
    "type": "skill",
    "cost": 10,
    "cost_pool": "fortune",
    "target": "enemy",
    "effects": lambda caster, targets: [
        transfer_stat(
            amount_fn=lambda c, ctx: c.get_skill_level_by_name("Transfer Wounds", 0),
            condition=IS_ENEMY,
        )
    ],
    "description": "Transfer wounds from yourself to an enemy. The damage and healing are equal to your level in this skill. This skill is a spell.",
},
    ]
)
