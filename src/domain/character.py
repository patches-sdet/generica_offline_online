from dataclasses import dataclass, field
from typing import Any, DefaultDict, Optional, TYPE_CHECKING
from collections import defaultdict
from domain.attributes import Attributes, Defenses
from domain.progression import Progression
from domain.effects.base import Effect
from domain.content_registry import get_progression_ability_names
from domain.skill_ownership import get_total_skill_levels

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

    # Persistent non-progression attribute gains that must survive rebuild.
    # Example:
    # {
    #   "strength": {
    #       "creation:manual": 5,
    #       "runtime:experience_die": 2,
    #       "level_up:adventure:Berserker": 1,
    #   }
    # }
    manual_attribute_increases: dict[str, dict[str, int]] = field(default_factory=dict)

    # CORE STATS

    attributes: Attributes = field(default_factory=Attributes)
    defenses: Defenses = field(default_factory=Defenses)

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
    
    level_points: int = 0
    grind_points: int = 0

    # Optional max values if your pool calculators set them
    max_hp: int = 0
    max_sanity: int = 0
    max_stamina: int = 0
    max_moxie: int = 0
    max_fortune: int = 0

    # SKILLS & ABILITIES

    skill_sources: dict[str, dict[str, int]] = field(default_factory=dict)
    skill_levels: dict[str, int] = field(default_factory=dict)
    skill_use_ranks: dict[str, int] = field(default_factory=dict)

    # Transitional: still useful while ability rebuild/runtime settles
    abilities: list["Ability"] = field(default_factory=list)

    # Derived summary that should be what gets rebuilt
    ability_levels: dict[str, int] = field(default_factory=dict)

    # TRUTH
    ability_provenance: dict[str, dict[str, Any]] = field(default_factory=dict)
    ability_use_ranks: dict[str, int] = field(default_factory=dict)

    # DERIVED STAT TRACKING

    _derived_bonuses: defaultdict[str, int] = field(
        default_factory=lambda: defaultdict(int),
        init=False,
    )
    _derived_overrides: dict[str, int] = field(default_factory=dict, init=False)

    # CONVENIENCE / LOOKUP

    # Derived Effective Ability/Skill level helper, this is to keep things
    # working until I refactor how levels are derived.
    def get_ability_effective_level(self, ability_name: str) -> int:
        return self.ability_levels.get(ability_name, 0)

    # ATTRIBUTE API

    def add_stat(self, stat: str, value: int, source: str | None = None) -> None:
        self.attributes.add(stat, value)
        if source:
            self._attribute_sources[stat][source] += value

    def set_stat(self, stat: str, value: int) -> None:
        self.attributes.set(stat, value)

    def get_stat(self, stat: str) -> int:
        return self.attributes.get(stat)

    def add_manual_attribute_increase(self, stat: str, amount: int, source: str) -> None:
        if amount <= 0:
            raise ValueError(f"Manual attribute increase must be positive: {stat} -> {amount}")

        self.manual_attribute_increases.setdefault(stat, {})
        current = self.manual_attribute_increases[stat].get(source, 0)
        self.manual_attribute_increases[stat][source] = current + amount

    def set_manual_attribute_increase(self, stat: str, amount: int, source: str) -> None:
        if amount < 0:
            raise ValueError(f"Manual attribute increase cannot be negative: {stat} -> {amount}")

        self.manual_attribute_increases.setdefault(stat, {})

        if amount == 0:
            self.manual_attribute_increases[stat].pop(source, None)
            if not self.manual_attribute_increases[stat]:
                self.manual_attribute_increases.pop(stat, None)
            return

        self.manual_attribute_increases[stat][source] = amount

    def get_total_manual_attribute_increase(self, stat: str) -> int:
        return sum(self.manual_attribute_increases.get(stat, {}).values())

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
        max_value = getattr(self, max_attr, None)

        if max_value is not None and max_value > 0:
            new_value = min(new_value, max_value)

        setattr(self, attr, new_value)
        return True

    def spend_resource(self, pool: str, amount: int) -> bool:
        return self.modify_resource(pool, -amount)

    # PROGRESSION API

    def add_progression(self, ptype: str, name: str, level: int = 1) -> None:
        self.set_progression_level(ptype, name, level)

    def set_progression_level(self, ptype: str, name: str, level: int) -> None:
        if level < 1:
            raise ValueError(f"Progression levels must be >= 1: {(ptype, name)} -> {level}")

        self.progressions[(ptype, name)] = Progression(
            name=name,
            type=ptype,
            level=level,
        )

    def get_progression(self, ptype: str, name: str) -> Optional[Progression]:
        return self.progressions.get((ptype, name))

    def get_progression_level(self, ptype: str, name: str, default: int = 0) -> int:
        progression = self.get_progression(ptype, name)
        return progression.level if progression else default

    def has_progression(self, ptype: str, name: str) -> bool:
        return self.get_progression_level(ptype, name, 0) > 0

    def get_progressions_by_type(self, ptype: str) -> list[Progression]:
        return [p for (kind, _), p in self.progressions.items() if kind == ptype]

    # Level up

    def increment_progression(self, ptype: str, name: str, amount: int = 1) -> None:
        if amount <= 0:
            raise ValueError(f"Progression increment must be positive: {amount}")

        current = self.get_progression_level(ptype, name)
        if current <= 0:
            raise ValueError(f"Cannot increment missing progression {(ptype, name)}")

        self.set_progression_level(ptype, name, current + amount)

    def get_progression_level_for_ability(
        self,
        ptype: str,
        ability_name: str,
        default: int = 0,
    ) -> int:
        best = default

        for (current_type, progression_name), progression in self.progressions.items():
            if current_type != ptype:
                continue

            granted = get_progression_ability_names(current_type, progression_name)
            if ability_name in granted:
                best = max(best, progression.level)

        return best

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
        return sum(self.skill_sources.get(name, {}).values())

    def get_skill_level(self, skill_name: str, default: int = 0) -> int:
        return self.skill_levels.get(skill_name, default)

    def has_skill(self, skill_name: str) -> bool:
        return get_total_skill_levels(self, skill_name) > 0

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
            "manual_attribute_increases": self.manual_attribute_increases,
            "attributes": self.attributes.to_dict(),
            "skills": self.skill_sources,
            "resources": {
                "hp": self.current_hp,
                "sanity": self.current_sanity,
                "stamina": self.current_stamina,
                "moxie": self.current_moxie,
                "fortune": self.current_fortune,
            },
        }