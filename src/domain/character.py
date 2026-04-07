from dataclasses import dataclass, field
from typing import Any, DefaultDict, Optional, TYPE_CHECKING
from collections import defaultdict
from domain.attributes import Attributes, Defenses
from domain.progression import Progression
from domain.effects.base import Effect
from domain.content_registry import get_progression_ability_names

if TYPE_CHECKING:
    from domain.abilities.factory import Ability


@dataclass(slots=True)
class Character:
    name: str
    # PROGRESSION-DRIVEN IDENTITY

    # Single source of truth for all character growth/content membership
    # key: (ptype, name)  e.g. ("race", "Human"), ("adventure", "Cultist")
    progressions: dict[tuple[str, str], Progression] = field(default_factory=dict)

    race_bases: list[str] = field(default_factory=list)
    race_template: Optional[str] = None
    race_material: Optional[str] = None

    # Optional character-creation choices for advanced race systems
    selected_racial_skills: dict[str, str] = field(default_factory=dict)

    # CORE STATS

    attributes: Attributes = field(default_factory=Attributes)
    defenses: Defenses = field(default_factory=Defenses)
    attribute_effects: list[Effect] = field(default_factory=list)

    # Snapshot / debugging
    _base_attributes: dict[str, int] = field(default_factory=dict, init=False)
    _attribute_sources: DefaultDict[str, DefaultDict[str, int]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(int)),
        init=False,
    )

    # RUNTIME SYSTEMS

    states: dict[str, Any] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)
    event_listeners: list[Any] = field(default_factory=list)

    roll_modifiers: list[Any] = field(default_factory=list)
    next_attack_modifiers: list[Any] = field(default_factory=list)
    extra_attacks: int = 0
    bonus_damage: int = 0
    damage_conversion: Any = None

    inventory: list[Any] = field(default_factory=list)
    equipment: list[Any] = field(default_factory=list)
    active_effects: list[Effect] = field(default_factory=list)

    # RESOURCES

    current_hp: int = 0
    current_sanity: int = 0
    current_stamina: int = 0
    current_moxie: int = 0
    current_fortune: int = 0

    # Optional max values if your pool calculators set them
    max_hp: int = 0
    max_sanity: int = 0
    max_stamina: int = 0
    max_moxie: int = 0
    max_fortune: int = 0

    # SKILLS & ABILITIES

    skills: dict[str, int] = field(default_factory=dict)

    # Transitional: still useful while ability rebuild/runtime settles
    abilities: list["Ability"] = field(default_factory=list)
    ability_levels: dict[str, int] = field(default_factory=dict)

    # DERIVED STAT TRACKING

    _derived_bonuses: defaultdict[str, int] = field(
        default_factory=lambda: defaultdict(int),
        init=False,
    )
    _derived_overrides: dict[str, int] = field(default_factory=dict, init=False)

    # ATTRIBUTE API

    def add_stat(self, stat: str, value: int, source: str | None = None) -> None:
        self.attributes.add(stat, value)
        if source:
            self._attribute_sources[stat][source] += value

    def set_stat(self, stat: str, value: int) -> None:
        self.attributes.set(stat, value)

    def get_stat(self, stat: str) -> int:
        return self.attributes.get(stat)

    # RESOURCE API

    def modify_resource(self, pool: str, amount: int) -> bool:
        attr = f"current_{pool}"

        if not hasattr(self, attr):
            raise ValueError(f"Invalid resource pool: {pool}")

        current = getattr(self, attr)
        new_value = current + amount

        if new_value < 0:
            return False

        max_attr = f"max_{pool}"
        if hasattr(self, max_attr):
            new_value = min(new_value, getattr(self, max_attr))

        setattr(self, attr, new_value)
        return True

    def spend_resource(self, pool: str, amount: int) -> bool:
        return self.modify_resource(pool, -amount)

    # PROGRESSION API

    def add_progression(self, ptype: str, name: str, level: int = 1) -> None:
        self.progressions[(ptype, name)] = Progression(name=name, type=ptype, level=level)

    def set_progression_level(self, ptype: str, name: str, level: int) -> None:
        self.progressions[(ptype, name)] = Progression(name=name, type=ptype, level=level)

    def get_progression(self, ptype: str, name: str) -> Optional[Progression]:
        return self.progressions.get((ptype, name))

    def get_progression_level(self, ptype: str, name: str, default: int = 0) -> int:
        progression = self.get_progression(ptype, name)
        return progression.level if progression else default

    def has_progression(self, ptype: str, name: str) -> bool:
        return (ptype, name) in self.progressions

    def get_progressions_by_type(self, ptype: str) -> list[Progression]:
        return [p for (kind, _), p in self.progressions.items() if kind == ptype]

    # Convenience wrappers
    def get_race_level(self, race_name: str, default: int = 0) -> int:
        return self.get_progression_level("race", race_name, default)

    def get_adventure_level(self, job_name: str, default: int = 0) -> int:
        return self.get_progression_level("adventure", job_name, default)

    def get_profession_level(self, job_name: str, default: int = 0) -> int:
        return self.get_progression_level("profession", job_name, default)

    def get_advanced_level(self, job_name: str, default: int = 0) -> int:
        return self.get_progression_level("advanced", job_name, default)

    def has_adventure_job(self, job_name: str) -> bool:
        return self.has_progression("adventure", job_name)

    def get_skill(self, name: str) -> int:
        return self.skills.get(name, 0)

    # SERIALIZATION

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "progressions": [
                {"type": p.type, "name": p.name, "level": p.level}
                for p in self.progressions.values()
            ],
            "race_bases": self.race_bases,
            "race_template": self.race_template,
            "race_material": self.race_material,
            "attributes": self.attributes.to_dict(),
            "skills": self.skills,
            "resources": {
                "hp": self.current_hp,
                "sanity": self.current_sanity,
                "stamina": self.current_stamina,
                "moxie": self.current_moxie,
                "fortune": self.current_fortune,
            },
        }