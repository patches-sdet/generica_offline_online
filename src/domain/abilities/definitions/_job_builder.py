from domain.abilities.factory import make_ability
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

def build_job(job_name: str, definitions: list) -> None:
    """
    Register all abilities for a job using a compact definition format,
    and record which progression grants which abilities.
    """
    for ability_def in definitions:
        name = ability_def["name"]
        kind = ability_def.get("type", "active")  # active | passive | skill

        source_type = ability_def.get("source_type", "adventure")
        required_level = ability_def.get("level", 1)

        def default_unlock(c, st=source_type, lvl=required_level, progression_name=job_name):
            return c.get_progression_level(st, progression_name, 0) >= lvl

        unlock_condition = ability_def.get("unlock", default_unlock)

        if kind == "passive":
            def make_effect_generator(fn, ability_name=name):
                def effect_generator(character):
                    ctx = EffectContext(source=character, targets=[character])
                    result = fn(ctx)
                    return _normalize_effect_result(
                        result,
                        f"{job_name}.{ability_name}.effect_generator",
                    )
                return effect_generator

            make_ability(
                name=name,
                unlock_condition=unlock_condition,
                effect_generator=make_effect_generator(ability_def["effects"]),
                duration=ability_def.get("duration", "Passive Constant"),
                description=ability_def.get("description", ""),
                is_passive=True,
                is_skill=False,
                target_type=ability_def.get("target", "self"),
                scales_with_level=ability_def.get("scales_with_level", True),
            )

        else:
            def make_execute(fn, ability_name=name):
                def execute(caster, targets):
                    ctx = EffectContext(source=caster, targets=targets)
                    result = fn(ctx)
                    return _normalize_effect_result(
                        result,
                        f"{job_name}.{ability_name}.execute",
                    )
                return execute

            make_ability(
                name=name,
                unlock_condition=unlock_condition,
                execute=make_execute(ability_def["effects"]),
                cost=ability_def.get("cost", 0),
                cost_pool=ability_def.get("cost_pool"),
                duration=ability_def.get("duration"),
                description=ability_def.get("description", ""),
                is_passive=False,
                is_skill=(kind == "skill"),
                target_type=ability_def.get("target", "self"),
                scales_with_level=ability_def.get("scales_with_level", True),
            )

        register_progression_ability_grant(source_type, job_name, name)