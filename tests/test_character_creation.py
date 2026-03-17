from application.character_creation import create_character

def test_create_character_with_job():
    character = create_character("Test", "Human", "Archer")

    assert character.job.name == "Archer"
    assert character.attributes.strength > 28  # baseline 25 + job 3 + roll (2-20)

# def create_character(name, race_name, job_name=None):
#    if job_name is None:
#        raise ValueError("job_name must be provided")
