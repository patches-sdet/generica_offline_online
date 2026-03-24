import pytest
from application.character_creation import create_character

@pytest.fixture
def base_character():
    return create_character("Test", "Human", "Archer", "Farmer")
