from domain.abilities.factory import make_ability
from domain.content_registry import register_ability, register_progression_ability_grant

def build_job(job_name: str, entries: list[dict], progression_type: str):
    for entry in entries:
        if "grant" in entry:
            register_progression_ability_grant(progression_type, job_name, entry["grant"])
            continue

        ability = make_ability(
            name=entry["name"],
            unlock_condition=entry.get("unlock_condition", lambda c: True),
            execute=entry.get("execute"),
            effect_generator=entry.get("effect_generator"),
            cost=entry.get("cost", 0),
            cost_pool=entry.get("cost_pool"),
            duration=entry.get("duration"),
            description=entry.get("description", ""),
            is_passive=entry.get("is_passive", False),
            is_skill=entry.get("is_skill", False),
            target_type=entry.get("target_type", "self"),
        )
        register_ability(ability)
        register_progression_ability_grant(progression_type, job_name, ability.name)

def build_adventure_job(job_name: str, entries: list[dict]):
    build_job(job_name, entries, progression_type="adventure")