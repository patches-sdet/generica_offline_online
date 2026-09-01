from __future__ import annotations

import argparse
import copy
import json
import sys
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean, median
from time import perf_counter_ns
from typing import Callable, Iterator

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application import character_creation
from application.character_creation import (
    apply_generic_skill_allocation,
    apply_job_skill_allocation,
    apply_manual_attribute_allocation,
    create_character,
)
from domain.calculations import recalculate
from domain.character import Character
from domain.content_registry import clear_content_registries, initialize_content_registries


FixtureBuilder = Callable[[], Character]


@dataclass(frozen=True, slots=True)
class BenchmarkScenario:
    name: str
    description: str
    build_character: FixtureBuilder


@dataclass(frozen=True, slots=True)
class BenchmarkStats:
    iterations: int
    min_ms: float
    median_ms: float
    mean_ms: float
    max_ms: float


@dataclass(frozen=True, slots=True)
class ScenarioBenchmarkResult:
    scenario: str
    description: str
    cold_ms: float
    warm: BenchmarkStats


@contextmanager
def deterministic_creation_rolls() -> Iterator[None]:
    original = character_creation.roll_attributes
    character_creation.roll_attributes = lambda: []
    try:
        yield
    finally:
        character_creation.roll_attributes = original


def _create_character(
    *,
    name: str,
    base_race_names: list[str],
    adventure_job_names: list[str],
    profession_job_names: list[str],
    race_template_name: str | None = None,
    material: str | None = None,
    manual_attribute_allocations: dict[str, int] | None = None,
) -> Character:
    with deterministic_creation_rolls():
        return create_character(
            name=name,
            base_race_names=base_race_names,
            adventure_job_names=adventure_job_names,
            profession_job_names=profession_job_names,
            race_template_name=race_template_name,
            material=material,
            manual_attribute_allocations=manual_attribute_allocations,
        )


def build_human_baseline() -> Character:
    return _create_character(
        name="Benchmark Human Baseline",
        base_race_names=["Human"],
        adventure_job_names=[],
        profession_job_names=[],
    )


def build_bear_berserker_brewer() -> Character:
    character = _create_character(
        name="Benchmark Bear Berserker Brewer",
        base_race_names=["Bear"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer"],
        manual_attribute_allocations={
            "strength": 5,
            "constitution": 5,
            "willpower": 5,
        },
    )
    apply_generic_skill_allocation(
        character,
        {
            "Brawling": 10,
            "Climb": 5,
            "Lockpicking": 5,
        },
    )
    apply_job_skill_allocation(
        character,
        {
            "Berserker": {"Growl": 10, "Toughness": 5},
        },
    )
    return character


def build_crossbreed_multi_progression() -> Character:
    character = _create_character(
        name="Benchmark Crossbreed Multi Progression",
        base_race_names=["Human", "Elf"],
        adventure_job_names=["Berserker"],
        profession_job_names=["Brewer", "Smith"],
        race_template_name="Crossbreed",
        manual_attribute_allocations={
            "strength": 5,
            "agility": 5,
            "intelligence": 5,
            "luck": 5,
        },
    )
    apply_generic_skill_allocation(
        character,
        {
            "Climb": 10,
            "Dodge": 10,
            "Lockpicking": 10,
            "Riding": 10,
        },
    )
    apply_job_skill_allocation(
        character,
        {
            "Berserker": {"Growl": 10, "Toughness": 10},
        },
    )
    apply_manual_attribute_allocation(
        character,
        {
            "wisdom": 5,
            "perception": 5,
        },
        source="benchmark:tuning",
    )
    return character


def build_scenarios() -> list[BenchmarkScenario]:
    return [
        BenchmarkScenario(
            name="human_baseline",
            description="Single-base-race character created through create_character() with no jobs or manual allocations.",
            build_character=build_human_baseline,
        ),
        BenchmarkScenario(
            name="bear_berserker_brewer",
            description="Representative application-flow fixture using create_character(), manual attribute allocation, generic skill allocation, and job skill allocation.",
            build_character=build_bear_berserker_brewer,
        ),
        BenchmarkScenario(
            name="crossbreed_multi_progression",
            description="Heavier rebuild fixture using Crossbreed plus one adventure and two profession progressions with layered allocations.",
            build_character=build_crossbreed_multi_progression,
        ),
    ]


def _measure_once_ns(func: Callable[[], None]) -> int:
    started = perf_counter_ns()
    func()
    return perf_counter_ns() - started


def _ns_to_ms(duration_ns: int) -> float:
    return duration_ns / 1_000_000


def _summarize_warm(durations_ns: list[int]) -> BenchmarkStats:
    durations_ms = [_ns_to_ms(value) for value in durations_ns]
    return BenchmarkStats(
        iterations=len(durations_ms),
        min_ms=min(durations_ms),
        median_ms=median(durations_ms),
        mean_ms=mean(durations_ms),
        max_ms=max(durations_ms),
    )


def benchmark_scenario(
    scenario: BenchmarkScenario,
    *,
    warm_iterations: int,
) -> ScenarioBenchmarkResult:
    clear_content_registries()
    initialize_content_registries(force=True)
    cold_character = scenario.build_character()
    cold_ns = _measure_once_ns(lambda: recalculate(cold_character))

    clear_content_registries()
    initialize_content_registries(force=True)
    warm_seed = scenario.build_character()
    warm_character = copy.deepcopy(warm_seed)
    warm_runs_ns = [_measure_once_ns(lambda: recalculate(warm_character)) for _ in range(warm_iterations)]

    return ScenarioBenchmarkResult(
        scenario=scenario.name,
        description=scenario.description,
        cold_ms=_ns_to_ms(cold_ns),
        warm=_summarize_warm(warm_runs_ns),
    )


def run_benchmarks(*, warm_iterations: int) -> list[ScenarioBenchmarkResult]:
    return [
        benchmark_scenario(scenario, warm_iterations=warm_iterations)
        for scenario in build_scenarios()
    ]


def _format_ms(value: float) -> str:
    return f"{value:.3f}"


def render_markdown(results: list[ScenarioBenchmarkResult]) -> str:
    lines = [
        "# recalculate() benchmark report",
        "",
        "Cold run = first standalone recalculate() call on a freshly created scenario after forced content initialization.",
        "Warm run = repeated recalculate() calls on an already-built scenario with registries already initialized.",
        "",
        "| Scenario | Cold ms | Warm min ms | Warm median ms | Warm mean ms | Warm max ms | Warm iterations |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for result in results:
        lines.append(
            "| "
            f"{result.scenario} | {_format_ms(result.cold_ms)} | {_format_ms(result.warm.min_ms)} | "
            f"{_format_ms(result.warm.median_ms)} | {_format_ms(result.warm.mean_ms)} | "
            f"{_format_ms(result.warm.max_ms)} | {result.warm.iterations} |"
        )

    lines.extend([
        "",
        "## Scenario notes",
        "",
    ])

    for result in results:
        lines.append(f"- **{result.scenario}**: {result.description}")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the narrow reproducible benchmark track around recalculate().",
    )
    parser.add_argument(
        "--warm-iterations",
        type=int,
        default=25,
        help="Number of repeated warm recalculate() runs per scenario.",
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Emit the benchmark report as JSON instead of markdown.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.warm_iterations < 1:
        raise ValueError("--warm-iterations must be >= 1")

    results = run_benchmarks(warm_iterations=args.warm_iterations)

    if args.output_json:
        print(json.dumps([asdict(result) for result in results], indent=2))
        return

    print(render_markdown(results))


if __name__ == "__main__":
    main()
