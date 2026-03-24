```python
from application.character_creation import create_character


def test_create_character_with_job_and_profession():
    character = create_character(
        "Test",
        "Human",
        "Archer",
        "Farmer"  # or any valid profession
    )

    assert character.job.name == "Archer"
    assert character.profession.name == "Farmer"

    # Ensure attributes were modified (not just base values)
    assert character.attributes.strength > 25
```

