import os, sys

TEMPLATE = """from domain.abilities.job_builder import build_job
from domain.abilities.patterns import buff, scaled_derived_buff
from domain.conditions import IS_ALLY

build_job("{job}", [

    # -------------------------
    # Passive
    # -------------------------
    {{
        "name": "Faith",
        "type": "passive",
        "effects": lambda c: scaled_derived_buff(
            stat="fate",
            scale_fn=lambda c: c.get_progression_level("{source_type}", "{job}", 0),
        )(c),
        "description": "Your Fate increases with {job} level.",
        "source_type": "{source_type}",
        "level": 1,
    }},

    # -------------------------
    # Example Skill
    # -------------------------
    {{
        "name": "Example Skill",
        "type": "skill",
        "cost": 1,
        "cost_pool": "fortune",
        "target": "ally",
        "effects": lambda caster, targets: [
            buff(
                scale_fn=lambda c: c.get_progression_level("{source_type}", "{job}", 0),
                stats={{"strength": 1}},
                condition=IS_ALLY,
            )
        ],
        "description": "Example scaling buff skill.",
        "source_type": "{source_type}",
        "level": 1,
    }},

])
"""
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python job_generator.py <JobName> [job|profession|advanced]")
        return

    job_name = sys.argv[1]
    job_type = sys.argv[2].lower() if len(sys.argv) > 2 else "job"
    filename = job_name.lower().replace(" ", "_") + ".py"

    base_path = ["src", "domain", "abilities"]

    if job_type == "profession":
        subfolder = "professions"
        source_type = "profession"
    elif job_type == "advanced":
        subfolder = "advanced"
        source_type = "advanced"
    else:
        subfolder = "definitions"
        source_type = "adventure"

    output_dir = os.path.join(*base_path, subfolder)
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, filename)

    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        return

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(job=job_name, source_type=source_type))

    print(f"Created: {filepath}")

if __name__ == "__main__":
    main()