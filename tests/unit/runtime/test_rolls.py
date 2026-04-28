from dataclasses import dataclass
from domain import rolls
from domain.rolls import main_roll

@dataclass
class DummyCharacter:
    def __init__(self):
        self.roll_modifiers = []
        self._stats = {"strength": 40}
        self.skill_levels = {"Lockpicking": 23}

    def get_stat(self, stat: str) -> int:
        return self._stats[stat]

    def get_skill_level(self, skill_name: str, default: int = 0) -> int:
        return self.skill_levels.get(skill_name, default)

@dataclass
class DummyModifier:
    def __init__(self, value: int):
        self.value = value

def test_main_roll_uses_character_stat_and_skill(monkeypatch):

    monkeypatch.setattr(rolls, "roll_1d100", lambda: 50)

    c = DummyCharacter()
    result = main_roll(c, "strength", "Lockpicking")

    assert result["roll"] == 50
    assert result["modified_roll"] == 50
    assert result["attribute"] == 40
    assert result["skill"] == 23
    assert result["total"] == 113
    assert result["critical_success"] is False
    assert result["automatic_failure"] is False

def test_main_roll_applies_roll_modifiers(monkeypatch):

    monkeypatch.setattr(rolls, "roll_1d100", lambda: 50)

    c = DummyCharacter()
    c.roll_modifiers = [DummyModifier(7), DummyModifier(3)]

    result = main_roll(c, "strength", "Lockpicking")

    assert result["roll"] == 50
    assert result["modified_roll"] == 60
    assert result["total"] == 123

def test_main_roll_marks_critical_success(monkeypatch):

    monkeypatch.setattr(rolls, "roll_1d100", lambda: 95)

    c = DummyCharacter()
    result = main_roll(c, "strength", None)

    assert result["critical_success"] is True
    assert result["automatic_failure"] is False

def test_main_roll_marks_automatic_failure(monkeypatch):

    monkeypatch.setattr(rolls, "roll_1d100", lambda: 7)

    c = DummyCharacter()
    result = main_roll(c, "strength", None)

    assert result["critical_success"] is False
    assert result["automatic_failure"] is True