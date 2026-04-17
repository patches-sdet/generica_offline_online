from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    extra_attacks,
    modify_next_attack,
    passive_modifier,
    apply_state,
)
from domain.effects.special.roll import RollModifierEffect

# Local helpers

RANGED_SKILL_GROUPS = {
    "archery",
    "magic bolts",
    "throwing",
    "guns",
    "siege engines",
}


def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name, 0)


def _highest_ranged_skill(character) -> int:
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

# Attack modifier helpers

def _aim_modifier(ctx, attack) -> None:
    attack.add_bonus(
        "accuracy",
        _ability_level(ctx.source, "Aim"),
    )


def _ricochet_shot_modifier(ctx, attack) -> None:
    attack.reduce_penalty(
        _ability_level(ctx.source, "Ricochet Shot")
    )
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
        _ability_level(ctx.source, "Razor Arrow"),
    )


def _crippling_shot_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "crippling_shot", True)
    _set_attack_attr(
        attack,
        "crippling_penalty",
        _ability_level(ctx.source, "Crippling Shot"),
    )
    _set_attack_attr(attack, "crippling_remove_dc", 120)
    _set_attack_attr(attack, "crippling_check_stat", "constitution")


def _flame_arrow_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "damage_type", "fire")
    _set_attack_attr(
        attack,
        "bonus_damage",
        _ability_level(ctx.source, "Flame Arrow"),
    )
    _append_attack_list_attr(
        attack,
        "critical_conditions",
        {"condition": "burning"},
    )


def _freeze_arrow_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "damage_type", "frost")
    _set_attack_attr(
        attack,
        "bonus_damage",
        _ability_level(ctx.source, "Freeze Arrow"),
    )
    _append_attack_list_attr(
        attack,
        "on_hit_saving_effects",
        {
            "check_stat": "constitution",
            "condition": "numbed",
            "remove_dc": 120,
        },
    )
    _append_attack_list_attr(
        attack,
        "critical_conditions",
        {
            "condition": "slowed",
            "remove_dc": 120,
        },
    )


def _acid_arrow_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "damage_type", "acid")
    _set_attack_attr(
        attack,
        "bonus_damage",
        _ability_level(ctx.source, "Acid Arrow"),
    )
    _append_attack_list_attr(
        attack,
        "on_hit_saving_effects",
        {
            "check_stat": "constitution",
            "condition": "poisoned",
            "damage_per_turn": 20,
            "remove_dc": 180,
        },
    )


def _scatter_shot_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "scatter_shot", True)
    _set_attack_attr(attack, "radius_yards", 5)
    _set_attack_attr(attack, "single_roll_multi_target", True)


def _arrow_of_light_modifier(ctx, attack) -> None:
    _set_attack_attr(attack, "damage_type", "light")
    _set_attack_attr(
        attack,
        "bonus_damage",
        _ability_level(ctx.source, "Arrow of Light"),
    )
    _set_attack_attr(attack, "ignore_all_defenses", True)
    _append_attack_list_attr(
        attack,
        "critical_conditions",
        {
            "condition": "blinded",
            "remove_dc": 180,
        },
    )

# Passive modifier helpers

def _missile_mastery_modifier(ctx) -> None:
    """
    Runtime-facing passive hook.

    When attacking with ranged weapons, may substitute half of the
    highest ranged weapon skill instead of the normal one. Training
    still applies to the replaced skill, not the substituted one.
    """
    if hasattr(ctx, "modify_attack_skill"):
        ctx.modify_attack_skill(
            replacement=lambda character: _highest_ranged_skill(character) // 2,
            applies_to=lambda attack: getattr(attack, "weapon_group", None) in RANGED_SKILL_GROUPS,
            preserve_training_skill=True,
        )
        return

    # Fallback placeholder for current engine stage
    if hasattr(ctx.source, "states"):
        ctx.source.states["missile_mastery_active"] = True


def _nimblejack_modifier(ctx) -> None:
    """
    Runtime-facing passive hook.

    Acrobatics/agility maneuvers may substitute Dexterity instead.
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

    # Fallback placeholder for current engine stage
    if hasattr(ctx.source, "states"):
        ctx.source.states["nimblejack_active"] = True

# Archer

build_job("Archer", [

    # Level 1

    {
        "name": "Aim",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "The Archer takes careful aim, and adds their Aim skill rating to the next shot they take."
        ),
        "duration": "1 turn",
        "effects": modify_next_attack(_aim_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Missile Mastery",
        "description": (
            "When attacking with ranged weapons, Archers may substitute half of their highest "
            "ranged weapon skill instead of the skill they would normally use. The experience roll "
            "still goes off of the replaced skill. This skill has no levels."
        ),
        "effects": passive_modifier(_missile_mastery_modifier),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {"grant": "Quickdraw", "required_level": 1},

    {
        "name": "Rapid Fire",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "The Archer may take two shots in the next ranged attack instead of one. "
            "All costs must be paid as normal. This skill can only be used once per turn. "
            "This skill has no levels."
        ),
        "duration": "Instant",
        "effects": extra_attacks(1),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Ricochet Shot",
        "cost": 5,
        "cost_pool": "fortune",
        "description": (
            "The Archer can bounce a shot off a hard surface to strike a target behind cover, "
            "around a corner, or otherwise not easily targeted. Activating this skill reduces "
            "the penalties required to make the shot on a one-for-one basis."
        ),
        "duration": "1 attack",
        "effects": modify_next_attack(_ricochet_shot_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 5

    {
        "name": "Demoralizing Shot",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "The Archer fires a warning shot designed to break the target's will rather than "
            "cause physical damage. The attack targets Willpower instead of Agility and inflicts "
            "Moxie damage instead of HP. Cool reduces the damage."
        ),
        "duration": "1 attack",
        "effects": modify_next_attack(_demoralizing_shot_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Far Shot",
        "cost": 15,
        "cost_pool": "stamina",
        "description": (
            "The Archer strains to throw or shoot as far as possible. Activating this skill "
            "reduces the penalties required to make the shot on a one-for-one basis."
        ),
        "duration": "1 attack",
        "effects": modify_next_attack(_far_shot_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Razor Arrow",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "The Archer fires a supernaturally sharp shot that bores through armor. "
            "Activating this skill lets the attack ignore one point of the target's armor "
            "for every level of this skill."
        ),
        "duration": "1 attack",
        "effects": modify_next_attack(_razor_arrow_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 5,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Crippling Shot",
        "cost": 20,
        "cost_pool": "stamina",
        "description": (
            "The Archer's attack strikes an important muscle group or joint, hindering mobility. "
            "When struck, the target must make a Constitution check using the Archer's total attack "
            "roll as the difficulty. On failure, Agility is debuffed by this skill level. "
            "The penalty can be removed as a condition with difficulty 120."
        ),
        "duration": "1 attack",
        "effects": modify_next_attack(_crippling_shot_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 10,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Flame Arrow",
        "cost": 20,
        "cost_pool": "fortune",
        "description": (
            "The Archer briefly imbues their weapon with fire. This converts all of the attack's "
            "damage to fire and inflicts an extra point of damage for every level in Flame Arrow. "
            "Critical hits can inflict burning."
        ),
        "duration": "1 attack",
        "effects": modify_next_attack(_flame_arrow_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 10,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 15

    {
        "name": "Freeze Arrow",
        "cost": 30,
        "cost_pool": "fortune",
        "description": (
            "The Archer briefly imbues their weapon with cold. This converts all of the attack's "
            "damage to frost and inflicts an extra point of damage for every level in Freeze Arrow. "
            "The target may be numbed on a failed Constitution check; critical hits may also inflict slowed."
        ),
        "duration": "1 attack",
        "effects": modify_next_attack(_freeze_arrow_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 15,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "One More Arrow",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "The Archer produces one piece of missile ammunition out of nothing. "
            "The ammo lasts for ten minutes, then fades away. This skill has no levels."
        ),
        "duration": "10 minutes",
        "effects": apply_state(
            "one_more_arrow",
            value_fn=lambda source: {
                "ammo_count": 1,
                "duration_minutes": 10,
            },
        ),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 15,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Acid Arrow",
        "cost": 40,
        "cost_pool": "fortune",
        "description": (
            "The Archer briefly imbues their weapon with acidic chemicals. "
            "This converts all of the attack's damage to acid and inflicts an extra point "
            "of damage for every level in Acid Arrow. It may also inflict poisoned."
        ),
        "duration": "1 attack",
        "effects": modify_next_attack(_acid_arrow_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 20,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Scatter Shot",
        "cost": 50,
        "cost_pool": "fortune",
        "description": (
            "The Archer causes the missile weapon's attack to magically duplicate in flight, "
            "hitting all foes within a five-yard radius of the target. One attack roll is applied "
            "against all targets. This skill has no levels."
        ),
        "duration": "1 attack",
        "effects": modify_next_attack(_scatter_shot_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 20,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Arrow of Light",
        "cost": 100,
        "cost_pool": "fortune",
        "description": (
            "The Archer briefly imbues their weapon with pure light, converts all damage to light, "
            "inflicts an extra point of damage for every level in Arrow of Light, and ignores all defenses. "
            "Critical hits may blind the target."
        ),
        "duration": "1 attack",
        "effects": modify_next_attack(_arrow_of_light_modifier),
        "is_passive": False,
        "is_skill": True,
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Nimblejack",
        "description": (
            "Whenever the Archer attempts an acrobatic maneuver or feat of agility, "
            "they may substitute Dexterity instead. This skill has no levels."
        ),
        "effects": passive_modifier(_nimblejack_modifier),
        "is_passive": True,
        "is_skill": False,
        "is_spell": False,
        "required_level": 25,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

], source_type="adventure")