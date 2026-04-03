from domain.abilities.factory import make_ability
from domain.effects import EffectContext
from domain.content_registry import register_progression_ability_grant


def _normalize_effect_result(result, source_name: str) -> list:
    if result is None:
        return []

    if not isinstance(result, list):
        result = [result]

    normalized = []
    for item in result:
        if isinstance(item, list):
            raise TypeError(f"{source_name} returned nested list of effects")
        normalized.append(item)

    return normalized

def build_shared_ability(namespace: str, definition: dict):
    definition = dict(definition)
    definition.setdefault("unlock", lambda character: True)
    return build_ability(
        definition,
        owner_name=namespace,
        source_type="shared",
    )

def build_ability(definition: dict, owner_name: str, source_type: str = "adventure"):
    name = definition["name"]
    kind = definition.get("type", "active")
    required_level = definition.get("level", 1)

    def default_unlock(c, st=source_type, lvl=required_level, progression_name=owner_name):
        return c.get_progression_level(st, progression_name, 0) >= lvl

    unlock_condition = definition.get("unlock", default_unlock)

    if kind == "passive":
        def make_effect_generator(fn, ability_name=name):
            def effect_generator(character):
                ctx = EffectContext(source=character, targets=[character])
                result = fn(ctx)
                return _normalize_effect_result(
                    result,
                    f"{owner_name}.{ability_name}.effect_generator",
                )
            return effect_generator

        return make_ability(
            name=name,
            unlock_condition=unlock_condition,
            effect_generator=make_effect_generator(definition["effects"]),
            duration=definition.get("duration", "Passive Constant"),
            description=definition.get("description", ""),
            is_passive=True,
            is_skill=False,
            target_type=definition.get("target", "self"),
            scales_with_level=definition.get("scales_with_level", True),
        )

    else:
        def make_execute(fn, ability_name=name):
            def execute(caster, targets):
                ctx = EffectContext(source=caster, targets=targets)
                result = fn(ctx)
                return _normalize_effect_result(
                    result,
                    f"{owner_name}.{ability_name}.execute",
                )
            return execute

        return make_ability(
            name=name,
            unlock_condition=unlock_condition,
            execute=make_execute(definition["effects"]),
            cost=definition.get("cost", 0),
            cost_pool=definition.get("cost_pool"),
            duration=definition.get("duration"),
            description=definition.get("description", ""),
            is_passive=False,
            is_skill=(kind == "skill"),
            target_type=definition.get("target", "self"),
            scales_with_level=definition.get("scales_with_level", True),
        )


def build_job(job_name: str, definitions: list) -> None:
    for ability_def in definitions:
        source_type = ability_def.get("source_type", "adventure")

        if "grant" in ability_def:
            register_progression_ability_grant(
                source_type,
                job_name,
                ability_def["grant"],
            )
            continue
        
        ability = build_ability(
            ability_def,
            owner_name=job_name,
            source_type=source_type,
        )
        register_progression_ability_grant(source_type, job_name, ability.name)