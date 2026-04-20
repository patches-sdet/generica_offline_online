from domain.abilities.builders._job_builder import build_job
from domain.abilities.patterns import (
    apply_state,
    create_item,
    passive_modifier,
    scaled_derived_buff,
)


# Local helpers

def _ability_level(character, ability_name: str) -> int:
    return character.get_ability_effective_level(ability_name)


def _explorer_level(character) -> int:
    return character.get_progression_level("adventure", "Explorer", 0)


def _ensure_states(target) -> dict:
    states = getattr(target, "states", None)
    if states is None:
        states = {}
        setattr(target, "states", states)
    return states


def _make_magical_map(source):
    return {
        "name": "Magical Map",
        "description": "A map showing everywhere the Explorer has been.",
        "created_by": "Magical Mapping",
        "visible_only_while_held": True,
        "exists_only_in_explorer_hand": True,
        "duration_hours": _explorer_level(source),
        "shows_visited_areas": True,
        "scalable_area_display": True,
    }


def _make_waystone(source):
    return {
        "name": "Waystone",
        "description": "A one-use teleportation stone linked to the Explorer's active waymark.",
        "created_by": "Create Waystone",
        "duration_hours": _explorer_level(source),
        "linked_to_active_waymark": True,
        "one_use": True,
        "breaks_after_use": True,
        "teleports_touching_user_to_waymark": True,
    }


def _make_greater_waystone(source):
    return {
        "name": "Greater Waystone",
        "description": "A permanent reusable waystone attuned to a greater waymark.",
        "created_by": "Create Greater Waystone",
        "permanent": True,
        "attunes_to_touched_greater_waymark": True,
        "reuse_cooldown_hours": 1,
        "requires_green_reagent": 1,
    }


# Passive helpers

def _direction_sense_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["direction_sense"] = {
        "active": True,
        "always_knows_direction": True,
        "no_roll_required": True,
        "source_ability": "Direction Sense",
    }


def _resist_nature_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["resist_nature"] = {
        "active": True,
        "natural_hazard_defense_bonus": _explorer_level(ctx.source),
        "applies_to": (
            "storms",
            "forest_fires",
            "rushing_currents",
            "other_nonanimal_natural_sources",
        ),
        "source_ability": "Resist Nature",
    }


def _expedition_leader_modifier(ctx) -> None:
    states = _ensure_states(ctx.source)
    states["expedition_leader"] = {
        "active": True,
        "explorer_buffs_extend_to_party": True,
        "party_roll_bonus": _explorer_level(ctx.source),
        "party_bonus_applies_to": (
            "traveling",
            "foraging",
            "climbing",
            "jumping",
        ),
        "source_ability": "Expedition Leader",
    }


build_job("Explorer", [

    # Level 1

    {
        "name": "All-Terrain Boots",
        "cost": 5,
        "cost_pool": "stamina",
        "description": (
            "Ignore terrain penalties and movement reductions. Gain a bonus equal to this skill's level "
            "to jumping or climbing rolls over difficult terrain."
        ),
        "duration": "1 Hour",
        "effects": apply_state(
            "all_terrain_boots_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": 1,
                "ignore_terrain_penalties": True,
                "ignore_movement_reductions": True,
                "jumping_bonus_over_difficult_terrain": _ability_level(source, "All-Terrain Boots"),
                "climbing_bonus_over_difficult_terrain": _ability_level(source, "All-Terrain Boots"),
                "source_ability": "All-Terrain Boots",
            },
        ),
        "required_level": 1,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Direction Sense",
        "description": (
            "Always know the direction of your choice without rolling."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_direction_sense_modifier),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    {"grant": "Forage", "required_level": 1},

    {
        "name": "Magical Mapping",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "Create a magical map showing everywhere you have been. The map exists only while in your hand."
        ),
        "duration": "1 Hour per Explorer Level",
        "effects": create_item(_make_magical_map),
        "is_spell": True,
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Resist Nature",
        "description": (
            "Gain a defense bonus equal to Explorer level against natural nonanimal hazards."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_resist_nature_modifier),
        "required_level": 1,
        "scales_with_level": False,
        "target": "self",
        "type": "passive",
    },

    # Level 5

    {
        "name": "Create Waystone",
        "cost": 10,
        "cost_pool": "fortune",
        "description": (
            "Create a one-use waystone linked to your active waymark. Touching it teleports the user to that waymark."
        ),
        "duration": "1 Hour per Explorer Level",
        "effects": create_item(_make_waystone),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

    {"grant": "Knack for Languages", "required_level": 5},

    {
        "name": "Set Waymark",
        "cost": 20,
        "cost_pool": "fortune",
        "description": (
            "Set a magical teleportation point. Later-created waystones link to it. It can be dispelled by magic."
        ),
        "duration": "1 Hour per Explorer Level",
        "effects": apply_state(
            "set_waymark_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": _explorer_level(source),
                "requires_touched_location": True,
                "linked_waystones_created_after_establishment": True,
                "detectable_only_by_magic": True,
                "can_be_dispelled": True,
                "dispel_difficulty": {
                    "stat": "willpower",
                    "skill": "Set Waymark",
                },
                "linked_waystones_break_if_waymark_ends": True,
                "source_ability": "Set Waymark",
            },
        ),
        "is_spell": True,
        "required_level": 5,
        "scales_with_level": False,
        "target": "area",
        "type": "skill",
    },

    # Level 10

    {
        "name": "Deep Breath",
        "cost": 10,
        "cost_pool": "stamina",
        "description": (
            "You do not need air while this skill is active."
        ),
        "duration": "1 Minute per Level",
        "effects": apply_state(
            "deep_breath_active",
            value_fn=lambda source: {
                "active": True,
                "duration_minutes": _ability_level(source, "Deep Breath"),
                "no_need_for_air": True,
                "source_ability": "Deep Breath",
            },
        ),
        "required_level": 10,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    {"grant": "Wakeful Wandering", "required_level": 10},

    # Level 15

    {
        "name": "Endure and Explore",
        "cost": 50,
        "cost_pool": "stamina",
        "description": (
            "Instantly throw off any condition that prevents stamina replenishment or holds you in place. "
            "Physical bindings slide off."
        ),
        "duration": "Instant",
        "effects": apply_state(
            "endure_and_explore_active",
            value_fn=lambda source: {
                "active": True,
                "remove_conditions_blocking_stamina_recovery": True,
                "remove_conditions_preventing_movement": True,
                "shed_physical_bindings": True,
                "self_only": True,
                "source_ability": "Endure and Explore",
            },
        ),
        "required_level": 15,
        "scales_with_level": False,
        "target": "self",
        "type": "skill",
    },

    {
        "name": "Fair Winds",
        "cost": 50,
        "cost_pool": "fortune",
        "description": (
            "Guide the winds in your favor, improving the speed and maneuverability of wind-powered craft."
        ),
        "duration": "1 Hour per Explorer Level",
        "effects": apply_state(
            "fair_winds_active",
            value_fn=lambda source: {
                "active": True,
                "duration_hours": _explorer_level(source),
                "applies_to_windpowered_craft": True,
                "speed_roll_bonus": _ability_level(source, "Fair Winds"),
                "maneuver_roll_bonus": _ability_level(source, "Fair Winds"),
                "cannot_create_hurricane_conditions": True,
                "source_ability": "Fair Winds",
            },
        ),
        "required_level": 15,
        "scales_with_level": True,
        "target": "ally",
        "type": "skill",
    },

    # Level 20

    {
        "name": "Expedition Leader",
        "description": (
            "Your buffs affect your whole party, and your party adds your Explorer level to traveling, "
            "foraging, climbing, and jumping rolls."
        ),
        "duration": "Passive Constant",
        "effects": passive_modifier(_expedition_leader_modifier),
        "required_level": 20,
        "scales_with_level": False,
        "target": "party",
        "type": "passive",
    },

    {
        "name": "Run, run away!",
        "cost": 50,
        "cost_pool": "stamina",
        "description": (
            "Add this skill's level to all chase rolls."
        ),
        "duration": "1 Chase",
        "effects": apply_state(
            "run_run_away_active",
            value_fn=lambda source: {
                "active": True,
                "duration": "1_chase",
                "chase_roll_bonus": _ability_level(source, "Run, run away!"),
                "applies_regardless_of_chase_side": True,
                "source_ability": "Run, run away!",
            },
        ),
        "required_level": 20,
        "scales_with_level": True,
        "target": "self",
        "type": "skill",
    },

    # Level 25

    {
        "name": "Craft Greater Waymark",
        "cost": 200,
        "cost_pool": "fortune",
        "description": (
            "Create a permanent Greater Waymark on a durable landmark. It cannot be dispelled, only destroyed with its host object."
        ),
        "duration": "Permanent",
        "effects": apply_state(
            "greater_waymark_active",
            value_fn=lambda source: {
                "active": True,
                "permanent": True,
                "requires_landmark_or_monument": True,
                "cannot_be_dispelled": True,
                "destroyed_only_if_host_object_destroyed": True,
                "requires_reagents": {
                    "violet": 1,
                },
                "supports_greater_waystones": True,
                "source_ability": "Craft Greater Waymark",
            },
        ),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "area",
        "type": "skill",
    },

    {
        "name": "Create Greater Waystone",
        "cost": 100,
        "cost_pool": "fortune",
        "description": (
            "Create a permanent Greater Waystone attuned to a touched Greater Waymark. It may be used once per hour."
        ),
        "duration": "Permanent",
        "effects": create_item(_make_greater_waystone),
        "is_spell": True,
        "required_level": 25,
        "scales_with_level": False,
        "target": "item",
        "type": "skill",
    },

], source_type="adventure")