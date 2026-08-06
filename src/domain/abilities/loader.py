from pathlib import Path

from domain.abilities.builders._job_builder import build_ability
from domain.abilities.factory import Ability


def load_abilities_from_yaml(directory: str) -> list[Ability]:
    """Load all ability definitions from YAML files."""
    abilities = []
    for yaml_file in Path(directory).glob("*.yaml"):
        with open(yaml_file) as f:
            definition = yaml.safe_load(f)
        ability = build_ability(definition, owner_name=yaml_file.stem)
        abilities.append(ability)
    return abilities