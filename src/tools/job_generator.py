import os
import sys

TEMPLATE = """from domain.abilities.job_builder import build_job
from domain.abilities.patterns import buff, heal, scaled_derived_buff
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
            scale_fn=lambda c: c.get_adventure_level_by_name("{job}", 0),
        )(c),
        "description": "Your Fate increases with {job} level.",
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
                scale_fn=lambda c: c.pools.get("fortune", 0),
                stats={{"any": 1}},
                condition=IS_ALLY,
            )
        ],
    }},

])
"""

def main():
    if len(sys.argv) < 2:
        print("Usage: python job_generator.py <JobName> [job|profession]")
        return

    job_name = sys.argv[1]
    job_type = sys.argv[2] if len(sys.argv) > 2 else "job"
    filename = job_name.lower().replace(" ", "_") + ".py"

    BASE_PATH = ["src", "domain", "abilities"]

    if job_type == "profession":
        subfolder = "professions"
    elif job_type == "advanced":
        subfolder = "advanced"
    else:
        subfolder = "definitions"
    
    output_dir = os.path.join(*BASE_PATH, subfolder)

    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, filename)

    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        return

    with open(filepath, "w") as f:
        f.write(TEMPLATE.format(job=job_name))

    print(f"Created: {filepath}")


if __name__ == "__main__":
    main()