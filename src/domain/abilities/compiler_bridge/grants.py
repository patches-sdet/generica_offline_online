from domain.abilities.definitions.definitions import AbilityDefinition, GrantSpec, JobDefinition
from domain.content_registry import register_progression_ability_grant


def compile_grants(job_def: JobDefinition) -> tuple[GrantSpec, ...]:
    implicit_grants = tuple(
        GrantSpec(name=ability.name, required_level=ability.required_level)
        for ability in job_def.abilities
    )

    return implicit_grants + job_def.grants


def register_job_grants(job_def: JobDefinition, grants: tuple[GrantSpec, ...]) -> None:
    for grant in grants:
        register_progression_ability_grant(
            job_def.owner_type,
            job_def.owner_name,
            grant.name,
            required_level=grant.required_level,
        )


def register_compiled_job(job_def: JobDefinition, compiled_abilities) -> tuple[GrantSpec, ...]:
    """Register typed compiler output using the same implicit-grant behavior as build_job."""
    del compiled_abilities
    grants = compile_grants(job_def)
    register_job_grants(job_def, grants)
    return grants
