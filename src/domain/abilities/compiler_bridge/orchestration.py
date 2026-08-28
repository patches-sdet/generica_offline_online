from domain.abilities.compiler_bridge.common import make_default_unlock
from domain.abilities.compiler_bridge.dispatch import dispatch_effect_compiler
from domain.abilities.compiler_bridge.grants import compile_grants
from domain.abilities.definitions.definitions import AbilityDefinition, JobDefinition
from domain.abilities.factory import make_ability


def compile_job(job_def: JobDefinition):
    compiled_abilities = tuple(
        compile_ability(
            ability_def,
            owner_name=job_def.owner_name,
            source_type=job_def.owner_type,
        )
        for ability_def in job_def.abilities
    )

    return compiled_abilities, compile_grants(job_def)


def compile_ability(defn: AbilityDefinition, owner_name: str, source_type: str):
    unlock_condition = make_default_unlock(source_type, owner_name, defn.required_level)
    effect_compiler = dispatch_effect_compiler(defn, owner_name)

    if defn.kind == "passive":
        effect_generator = effect_compiler(defn.effects)
        execute = None
    else:
        effect_generator = None
        execute = effect_compiler(defn.effects)

    return make_ability(
        name=defn.name,
        unlock_condition=unlock_condition,
        execute=execute,
        effect_generator=effect_generator,
        cost=defn.activation.cost,
        cost_pool=defn.activation.cost_pool,
        duration=defn.activation.duration,
        description=defn.description,
        target_type=defn.activation.target,
        scales_with_level=defn.scales_with_level,
        is_passive=(defn.kind == "passive"),
        is_skill=(defn.kind == "skill"),
        is_spell=defn.is_spell,
    )
