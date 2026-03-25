from domain.race import resolve_race
from domain.adventure import resolve_job
from domain.profession import resolve_profession

def make_base_character():
    return create_character(
            name="Test", race=resolve_race("Human"), 
            job=resolve_job("Archer"), 
            profession=resolve_profession("Farmer")
            )


def make_golem_character():
    return create_character(
        name=("Test"),
        race=resolve_race("toy Golem"),
        job=resolve_job("aNimator"),
        profession=resolve_profession("Farmer"),
        base_race=resolve_race("Human"),
        material="metal",
    )
