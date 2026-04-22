from domain.abilities.builders._job_builder import build_job
from domain.abilities import ability_level, ctx_ability_level, progression_level, ctx_progression_level
from domain.abilities.patterns import (
    apply_state,
    extra_attacks,
    modify_next_attack,
    passive_modifier,
)

RANGED_SKILL_GROUPS = {
    "archery",
    "magic bolts",
    "throwing",
    "guns",
    "siege engines",
}

def _highest_ranged_skill(character) -> int:
    """
    Best-effort runtime helper.

    Current runtime support for weapon skill lookup may still evolve, so this
    remains intentionally defensive and metadata-friendly.
    """
    ranged_skills = getattr(character, "ranged_skills", {})
    return max(ranged_skills.values(), default=0)

def _set_attack_attr(attack, key: str, value) -> None:
    setattr(attack, key, value)

def _append_attack_list_attr(attack, key: str, value) -> None:
    current = getattr(attack, key, None)
    if current is None:
        current = []
        setattr(attack, key, current)
    current.append(value)

def _scaled_bonus_damage(ctx, ability_name: str) -> int:
    return ability_level(ctx, ability_name)

# Attack modifiers

def _aim_modifier(ctx, attack) -> None:
    attack.add_bonus("accuracy", ctx_ability_level(ctx, "Aim"))

def _ricochet_shot_modifier(ctx, attack) -> None:
    attack.reduce_penalty(ctx_ability_level(ctx, "Ricochet Shot"))
    _set_attack_attr(attack, "ricochet_shot", True)

def _demoralizing_shot_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "target_stat", "willpower")
    _set_attack_attr(attack, "damage_pool", "moxie")
    _set_attack_attr(attack, "defense_stat", "cool")
    _set_attack_attr(attack, "demoralizing_shot", True)

def _far_shot_modifier(ctx, attack) -> None:
    attack.reduce_penalty(1)
    _set_attack_attr(attack, "far_shot", True)

def _razor_arrow_modifier(ctx, attack) -> None:
    _set_attack_attr(
        attack,
        "ignore_armor",
        ctx_ability_level(ctx, "Razor Arrow"),
    )

def _crippling_shot_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "crippling_shot", True)
    _set_attack_attr(
        attack,
        "crippling_penalty",
        ctx_ability_level(ctx, "Crippling Shot"),
    )
    _set_attack_attr(attack, "crippling_remove_dc", 120)
    _set_attack_attr(attack, "crippling_check_stat", "constitution")

def _elemental_arrow_modifier(
    ctx,
    attack,
    *,
    ability_name: str,
    damage_type: str,
    on_hit_saving_effects: list[dict] | None = None,
    critical_conditions: list[dict] | None = None,
    ignore_all_defenses: bool = False,
) -> None:
    _set_attack_attr(attack, "damage_type", damage_type)
    _set_attack_attr(attack, "bonus_damage", _scaled_bonus_damage(ctx, ability_name))

    if ignore_all_defenses:
        _set_attack_attr(attack, "ignore_all_defenses", True)

    for effect in on_hit_saving_effects or []:
        _append_attack_list_attr(attack, "on_hit_saving_effects", effect)

    for condition in critical_conditions or []:
        _append_attack_list_attr(attack, "critical_conditions", condition)

def _flame_arrow_modifier(ctx, attack) -> None:
    _elemental_arrow_modifier(
        ctx,
        attack,
        ability_name="Flame Arrow",
        damage_type="fire",
        critical_conditions=[
            {"condition": "burning"},
        ],
    )

def _freeze_arrow_modifier(ctx, attack) -> None:
    _elemental_arrow_modifier(
        ctx,
        attack,
        ability_name="Freeze Arrow",
        damage_type="frost",
        on_hit_saving_effects=[
            {
                "check_stat": "constitution",
                "condition": "numbed",
                "remove_dc": 120,
            },
        ],
        critical_conditions=[
            {
                "condition": "slowed",
                "remove_dc": 120,
            },
        ],
    )

def _acid_arrow_modifier(ctx, attack) -> None:
    _elemental_arrow_modifier(
        ctx,
        attack,
        ability_name="Acid Arrow",
        damage_type="acid",
        on_hit_saving_effects=[
            {
                "check_stat": "constitution",
                "condition": "poisoned",
                "damage_per_turn": 20,
                "remove_dc": 180,
            },
        ],
    )

def _scatter_shot_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "scatter_shot", True)
    _set_attack_attr(attack, "radius_yards", 5)
    _set_attack_attr(attack, "single_roll_multi_target", True)

def _arrow_of_light_modifier(ctx, attack) -> None:
    _elemental_arrow_modifier(
        ctx,
        attack,
        ability_name="Arrow of Light",
        damage_type="light",
        ignore_all_defenses=True,
        critical_conditions=[
            {
                "condition": "blinded",
                "remove_dc": 180,
            },
        ],
    )

# Passive runtime hooks

def _missile_mastery_modifier(ctx) -> None:
    """
    Runtime-facing passive hook.

    When attacking with ranged weapons, the user may substitute half of their
    highest ranged weapon skill instead of the usual skill. The replaced skill
    still remains the one that receives training/experience.
    """
    if hasattr(ctx, "modify_attack_skill"):
        ctx.modify_attack_skill(
            replacement=lambda character: _highest_ranged_skill(character) // 2,
            applies_to=lambda attack: getattr(attack, "weapon_group", None) in RANGED_SKILL_GROUPS,
            preserve_training_skill=True,
        )
        return

    if hasattr(ctx.source, "states"):
        ctx.source.states["missile_mastery_active"] = True

def _nimblejack_modifier(ctx) -> None:
    """
    Runtime-facing passive hook.

    Acrobatics and agility-style maneuvers may substitute Dexterity.
    """
    if hasattr(ctx, "modify_check_stat"):
        ctx.modify_check_stat(
            applies_to=lambda check: getattr(check, "category", None) in {
                "acrobatics",
                "agility_maneuver",
            },
            replacement_stat="dexterity",
        )
        return

    if hasattr(ctx.source, "states"):
        ctx.source.states["nimblejack_active"] = True

# Archer

build_job(
    "Archer",
    [
        # Level 1
        {
            "name": "Aim",
            "type": "skill",
            "cost": 10,
            "cost_pool": "fortune",
            "duration": "1 turn",
            "target": "self",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "The Archer takes careful aim and adds their Aim skill rating to "
                "the next shot they take."
            ),
            "effects": modify_next_attack(_aim_modifier),
        },
        {
            "name": "Missile Mastery",
            "type": "passive",
            "target": "self",
            "required_level": 1,
            "scales_with_level": False,
            "description": (
                "When attacking with ranged weapons, the Archer may substitute half "
                "of their highest ranged weapon skill instead of the skill they would "
                "normally use. The experience roll still goes off the replaced skill. "
                "This skill has no levels."
            ),
            "effects": passive_modifier(_missile_mastery_modifier),
        },
        {
            "grant": "Quickdraw",
            "required_level": 1,
        },
        {
            "name": "Rapid Fire",
            "type": "skill",
            "cost": 10,
            "cost_pool": "stamina",
            "duration": "Instant",
            "target": "self",
            "required_level": 1,
            "scales_with_level": False,
            "description": (
                "The Archer may take two shots in the next ranged attack instead of "
                "one. All costs must still be paid as normal. This skill can only be "
                "used once per turn. This skill has no levels."
            ),
            "effects": extra_attacks(1),
        },
        {
            "name": "Ricochet Shot",
            "type": "skill",
            "cost": 5,
            "cost_pool": "fortune",
            "duration": "1 attack",
            "target": "self",
            "required_level": 1,
            "scales_with_level": True,
            "description": (
                "The Archer can bounce a shot off a hard surface to strike a target "
                "behind cover, around a corner, or otherwise not easily targeted. "
                "Activating this skill reduces the penalties required to make the shot "
                "on a one-for-one basis."
            ),
            "effects": modify_next_attack(_ricochet_shot_modifier),
        },

        # Level 5
        {
            "name": "Demoralizing Shot",
            "type": "skill",
            "cost": 10,
            "cost_pool": "stamina",
            "duration": "1 attack",
            "target": "self",
            "required_level": 5,
            "scales_with_level": False,
            "description": (
                "The Archer fires a warning shot designed to break the target's will "
                "rather than cause physical damage. The attack targets Willpower "
                "instead of Agility and inflicts Moxie damage instead of HP. Cool "
                "reduces the damage."
            ),
            "effects": modify_next_attack(_demoralizing_shot_modifier),
        },
        {
            "name": "Far Shot",
            "type": "skill",
            "cost": 15,
            "cost_pool": "stamina",
            "duration": "1 attack",
            "target": "self",
            "required_level": 5,
            "scales_with_level": False,
            "description": (
                "The Archer strains to throw or shoot as far as possible. Activating "
                "this skill reduces the penalties required to make the shot on a "
                "one-for-one basis."
            ),
            "effects": modify_next_attack(_far_shot_modifier),
        },
        {
            "name": "Razor Arrow",
            "type": "skill",
            "cost": 10,
            "cost_pool": "fortune",
            "duration": "1 attack",
            "target": "self",
            "required_level": 5,
            "scales_with_level": True,
            "description": (
                "The Archer fires a supernaturally sharp shot that bores through "
                "armor. Activating this skill lets the attack ignore one point of the "
                "target's armor for every level of this skill."
            ),
            "effects": modify_next_attack(_razor_arrow_modifier),
        },

        # Level 10
        {
            "name": "Crippling Shot",
            "type": "skill",
            "cost": 20,
            "cost_pool": "stamina",
            "duration": "1 attack",
            "target": "self",
            "required_level": 10,
            "scales_with_level": True,
            "description": (
                "The Archer's attack strikes an important muscle group or joint, "
                "hindering mobility. When struck, the target must make a Constitution "
                "check using the Archer's total attack roll as the difficulty. On "
                "failure, Agility is debuffed by this skill level. The penalty can be "
                "removed as a condition with difficulty 120."
            ),
            "effects": modify_next_attack(_crippling_shot_modifier),
        },
        {
            "name": "Flame Arrow",
            "type": "skill",
            "cost": 20,
            "cost_pool": "fortune",
            "duration": "1 attack",
            "target": "self",
            "required_level": 10,
            "scales_with_level": True,
            "description": (
                "The Archer briefly imbues their weapon with fire. This converts all "
                "of the attack's damage to fire and inflicts an extra point of damage "
                "for every level in Flame Arrow. Critical hits may inflict burning."
            ),
            "effects": modify_next_attack(_flame_arrow_modifier),
        },

        # Level 15
        {
            "name": "Freeze Arrow",
            "type": "skill",
            "cost": 30,
            "cost_pool": "fortune",
            "duration": "1 attack",
            "target": "self",
            "required_level": 15,
            "scales_with_level": True,
            "description": (
                "The Archer briefly imbues their weapon with cold. This converts all "
                "of the attack's damage to frost and inflicts an extra point of damage "
                "for every level in Freeze Arrow. The target may be numbed on a failed "
                "Constitution check; critical hits may also inflict slowed."
            ),
            "effects": modify_next_attack(_freeze_arrow_modifier),
        },
        {
            "name": "One More Arrow",
            "type": "skill",
            "cost": 10,
            "cost_pool": "fortune",
            "duration": "10 minutes",
            "target": "self",
            "required_level": 15,
            "scales_with_level": False,
            "description": (
                "The Archer produces one piece of missile ammunition out of nothing. "
                "The ammunition lasts for ten minutes, then fades away. This skill has "
                "no levels."
            ),
            "effects": apply_state(
                "one_more_arrow",
                value_fn=lambda source: {
                    "ammo_count": 1,
                    "duration_minutes": 10,
                },
            ),
        },

        # Level 20
        {
            "name": "Acid Arrow",
            "type": "skill",
            "cost": 40,
            "cost_pool": "fortune",
            "duration": "1 attack",
            "target": "self",
            "required_level": 20,
            "scales_with_level": True,
            "description": (
                "The Archer briefly imbues their weapon with acidic chemicals. This "
                "converts all of the attack's damage to acid and inflicts an extra "
                "point of damage for every level in Acid Arrow. It may also inflict "
                "poisoned."
            ),
            "effects": modify_next_attack(_acid_arrow_modifier),
        },
        {
            "name": "Scatter Shot",
            "type": "skill",
            "cost": 50,
            "cost_pool": "fortune",
            "duration": "1 attack",
            "target": "self",
            "required_level": 20,
            "scales_with_level": False,
            "description": (
                "The Archer causes the missile weapon's attack to magically duplicate "
                "in flight, hitting all foes within a five-yard radius of the target. "
                "One attack roll is applied against all targets. This skill has no "
                "levels."
            ),
            "effects": modify_next_attack(_scatter_shot_modifier),
        },

        # Level 25
        {
            "name": "Arrow of Light",
            "type": "skill",
            "cost": 100,
            "cost_pool": "fortune",
            "duration": "1 attack",
            "target": "self",
            "required_level": 25,
            "scales_with_level": True,
            "description": (
                "The Archer briefly imbues their weapon with pure light, converts all "
                "damage to light, inflicts an extra point of damage for every level in "
                "Arrow of Light, and ignores all defenses. Critical hits may blind the "
                "target."
            ),
            "effects": modify_next_attack(_arrow_of_light_modifier),
        },
        {
            "name": "Nimblejack",
            "type": "passive",
            "target": "self",
            "required_level": 25,
            "scales_with_level": False,
            "description": (
                "Whenever the Archer attempts an acrobatic maneuver or feat of agility, "
                "they may substitute Dexterity instead. This skill has no levels."
            ),
            "effects": passive_modifier(_nimblejack_modifier),
        },
    ],
    source_type="adventure",
)