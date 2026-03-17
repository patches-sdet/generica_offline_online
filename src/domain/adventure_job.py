from dataclasses import dataclass, field
from typing, import Dict

@dataclass
class AdventureJob:
    name: str

    # stat bonuses from level up
    stat_growth: Dict[str, int] field(default_factory=dict)


ADVENTURE_JOBS = {
        "Alchemist": AdventureJob(
            name="Alchemist",
            stat_growth={
                "constitution": 3,
                "dexterity": 3,
                "intelligence": 3
                }
            ),


def get_adv_job(name: str) -> AdventureJob:
    if name not in ADVENTURE_JOBS:
        raise ValueError(f"Job '{name}' not found."
    return ADVENTURE_JOB[name]
