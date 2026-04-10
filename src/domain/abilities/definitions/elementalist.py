from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import create_item, scaled_derived_buff, skill_check, hp_damage, conditional_effect
from domain.conditions import IS_ALLY

def create_element(element_type, amount_fn):
    def effect(ctx):
        amount = amount_fn(ctx)
        element = element_type.format(**ctx.source.attributes)
        return [
            create_item(
                name=f"{element} Element",
                description=f"A chunk of {element} energy created by Call Element.",
                element=element,
                amount=amount,
                ),
        ]
    return effect

def summon_elemental(level):
    def effect(ctx):
        elemental = create_item(
            name=f"Level {level} Elemental",
            description=f"A level {level} elemental summoned by Least Elemental.",
            level=level,
        )
        return [elemental]
    return effect

build_job("Elementalist", [

    {
        "name": "Call Element",
        "cost": 10,
        "cost_pool": "sanity",
        "description": "This allows you to create an amount of an element that matches your Elemental Affinity. You can create one cubic foot per level of this skill. This skill is a spell.",
        "effects": create_element(
                element_type="{elemental_affinity}",
                amount_fn=lambda c: c.ability_levels.get("Call Element", 0)
            ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "unoccupied area",
        "type": "skill",
    },

    {
        "name": "Elemental Affinity",
        "description": "You have an affinity to one of the four classic elements: Earth, Fire, Air, or Water. You must choose one when selecting this job, and it cannot be changed later. You gain damage resistance to that element at 80%. This skill has no levels.",
        "effects": [], # TODO: Need to work out how damage reduction works
        "is_passive": True,
        "is_skill": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {
        "name": "Endure Element",
        "cost": 5,
        "cost_pool": "sanity",
        "description": "You can give yourself or an ally resistance to an element chosen from your Elemental Affinity(ies). The resistance granted is equal to the level of this skill as a percentage. This DOES stack with the resistance granted by Elemental Affinity. This skill is a spell.",
        "effects": scaled_derived_buff(
                scale_fn=lambda c: c.ability_levels.get("Endure Element", 0) * 0.1,
                stat="armor",
                condition=IS_ALLY, # TODO: Need to get this to work on either an ally or self.
            ),
        "is_passive": False,
        "is_skill": True,
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
        "description": "You summon a Class One elemental. This is a Willpower plus Least Elemental roll against the elemental's Willpower. The level of the Elemental is equal to your Elementalist level. This skill is a spell.",
        "effects": skill_check(
                ability="Least Elemental",
                stat="willpower",
                difficulty=lambda target: target.roll_willpower(),
                on_success=summon_elemental(level=lambda c: c.get_progression_level("Elementalist")),
            ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",
    },

    {
        "name": "Manipulate Element",
        "cost": 10,
        "cost_pool": "sanity",
        "description": ("You can manipulate an element you have created with Call Element. You can move it or throw it. You can use this as an attack; it is a Dexterity plus Manipulate Element roll. If you get a critical hit, an additional effect is applied based on your element and last for one turn. This skill is a spell. ",
                        "Fire: Burning\n",
                        "Water: Slowed\n",
                        "Earth: Hobbled\n",
                        "Air: Stunned\n",
        ),
        "effects": skill_check(
                ability="Manipulate Element",
                stat="dexterity",
                difficulty=lambda target: target.roll_agility(),
                on_success=lambda target: [
                    hp_damage(
                        scale_fn=lambda c: (c.ability_levels.get("Manipulate Element", 0) * 2),
                        condition=lambda ctx, t: t == target,
                    ),
                    conditional_effect(
                        effect=scaled_derived_buff(
                            scale_fn=lambda c: 1, # TODO: It's now a scaled_derived_buff penalizing attack, but it needs to match to both the element and the level of Manipulate Element
                            stats={"attack": -1},
                        ),
                        condition=lambda c: c.roll_result.get("is_critical_hit", False) and c.target == target,
                    )
                ], # TODO: Implement damage based on difference between rolls.
            ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": True,
        "target": "enemy",
        "type": "skill",

    }
],
source_type="adventure"
)