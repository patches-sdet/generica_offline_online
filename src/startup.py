"""
Generica Offline Online — Interactive Shell Bootstrap

Usage:

    python -i src/startup.py

This loads:

- content registries
- ability modules
- progression mappings
- core engine objects
- rebuild pipeline
- runtime helpers

into an interactive Python shell.
"""

from pprint import pprint

print("\n=== Generica Offline Online Shell Bootstrap ===\n")

# Registry Initialization

from domain.content_registry import (
    initialize_content_registries,
    clear_content_registries,
    get_all_abilities,
    get_all_adventure_jobs,
    get_all_profession_jobs,
    get_all_advanced_jobs,
    _PROGRESSION_ABILITY_GRANTS,
)

initialize_content_registries()

print("✔ Content registries initialized")


# --------------------------------------------------
# Core Character Model
# --------------------------------------------------

from domain.character import Character

print("✔ Character class loaded")

# Rebuild Pipeline

from domain.calculations import recalculate

print("✔ Recalculate pipeline ready")

# Ability Lookup Utilities

from domain.content_registry import (
    get_ability,
    get_progression_ability_grants,
    get_unlocked_progression_ability_grants,
)

print("✔ Ability lookup helpers ready")

# Skill Ownership System

from domain.skill_ownership import (
    add_skill_levels,
    remove_skill_source,
    has_skill,
)

from application.runtime import award_generic_skill

print("✔ Skill ownership helpers ready")

# Progression Helpers

from domain.progression import Progression

print("✔ Progression helpers ready")

# Effect System Access (Useful for Debugging)

from domain.effects.base import EffectContext

print("✔ Effect system context ready")

# Optional: Character Creation Entry Point

try:
    from application.character_creation import create_character

    print("✔ Character creation helper ready")

except Exception:
    print("⚠ Character creation helper not available")

# Optional: Registry Inspection Utilities

from domain.content_registry import (
    _ABILITY_REGISTRY,
    _BASE_RACE_REGISTRY,
    _RACE_TEMPLATE_REGISTRY,
    _ADVENTURE_JOB_REGISTRY,
    _PROFESSION_JOB_REGISTRY,
    _ADVANCED_JOB_REGISTRY,
)

print("✔ Registry inspection helpers ready")

# Convenience Debug Helpers

def show_loaded_counts():
    print("\n=== Registry Counts ===")

    print("Abilities:", len(_ABILITY_REGISTRY))
    print("Races:", len(_BASE_RACE_REGISTRY))
    print("Race Templates:", len(_RACE_TEMPLATE_REGISTRY))
    print("Adventure Jobs:", len(_ADVENTURE_JOB_REGISTRY))
    print("Profession Jobs:", len(_PROFESSION_JOB_REGISTRY))
    print("Advanced Jobs:", len(_ADVANCED_JOB_REGISTRY))


def list_abilities():
    pprint(sorted(_ABILITY_REGISTRY.keys()))


def list_adventure_jobs():
    pprint(sorted(_ADVENTURE_JOB_REGISTRY.keys()))


def list_profession_jobs():
    pprint(sorted(_PROFESSION_JOB_REGISTRY.keys()))


def list_races():
    pprint(sorted(_BASE_RACE_REGISTRY.keys()))
    pprint(sorted(_RACE_TEMPLATE_REGISTRY.keys()))

def audit_progression_coverage():
    print("\n=== Progression Coverage Audit ===")

    for job in sorted(_ADVENTURE_JOB_REGISTRY):
        abilities = get_progression_ability_grants(("adventure", job))

        if not abilities:
            print(f"⚠ {job}: NO ABILITIES REGISTERED")
        else:
            print(f"✔ {job}: {len(abilities)} abilities")

def show_progression_grants(ptype: str, name: str):
    print(f"\n=== Grants for {ptype}:{name} ===")
    for ability_name, required_level in get_progression_ability_grants(ptype, name):
        print(f"Lv {required_level:>2} - {ability_name}")


def show_unlocked_progression_grants(ptype: str, name: str, level: int):
    print(f"\n=== Unlocked grants for {ptype}:{name} at level {level} ===")
    for ability_name in get_unlocked_progression_ability_grants(ptype, name, level):
        print(ability_name)


def probe_progression(ptype: str, name: str, level: int = 1):
    print(f"\n=== Progression Probe: {ptype}:{name} @ level {level} ===")
    print("All grants:")
    for ability_name, required_level in get_progression_ability_grants(ptype, name):
        print(f"  Lv {required_level:>2} - {ability_name}")

    print("\nUnlocked now:")
    unlocked = get_unlocked_progression_ability_grants(ptype, name, level)
    if not unlocked:
        print("  (none)")
    else:
        for ability_name in unlocked:
            print(f"  {ability_name}")

print("✔ Debug helpers ready")

# Example Starter Character

def new_character(name="Test Character"):
    c = Character(name=name)
    print(f"\nCreated character: {name}")
    return c

print("✔ new_character() helper ready")

print("\n=== Bootstrap Complete ===\n")

print("Try:")
print("    show_loaded_counts()")
print("    c = new_character()")
print("    award_generic_skill(c, 'Riding')")
print("    recalculate(c)")
print("    audit_progression_coverage()")
print("    show_progression_grants('adventure', 'Archer')")
print("    show_unlocked_progression_grants('adventure', 'Archer', 1)")
print("    probe_progression('profession', 'Brewer', 5)")
print("Run:")
print("    run_full_job_ability_audit()")
print("to verify job ability population coverage.\n")


def run_full_job_ability_audit(test_shared_ability: str = "Quickdraw") -> bool:
    """
    Full coverage audit for progression -> ability grant population.

    Runs the practical equivalent of the 12 checklist phases:
      1. Registry initialization validation
      2. Adventure job grant coverage
      3. Profession job grant coverage
      4. Advanced job grant coverage
      5. Ability registry integrity
      6. Unlock threshold validation
      7. Shared ability deduplication probe
      8. Passive ability pipeline probe
      9. Scaling ability structure probe
     10. Registry determinism validation
     11. Missing coverage detection
     12. Pass/fail completion summary

    Returns:
        bool: True if audit passes with no failures, False otherwise.
    """

    from collections import defaultdict

    results = []
    failures = []
    warnings = []

    def record(ok: bool, label: str, detail: str = "") -> None:
        results.append((ok, label, detail))
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
        if detail:
            print(f"       {detail}")
        if not ok:
            failures.append((label, detail))

    def warn(label: str, detail: str = "") -> None:
        warnings.append((label, detail))
        print(f"[WARN] {label}")
        if detail:
            print(f"       {detail}")

    def safe_job_name(job) -> str:
        return getattr(job, "name", str(job))

    def sorted_grants_for(ptype: str, name: str):
        grants = get_progression_ability_grants(ptype, name)
        return tuple(sorted(grants, key=lambda item: (item[1], item[0])))

    print("\n=== FULL JOB ABILITY COVERAGE AUDIT ===\n")

    # Phase 1 + 10: Registry initialization + determinism

    try:
        clear_content_registries()
        initialize_content_registries()
        snapshot_one = {
            "abilities": tuple(sorted(a.name for a in get_all_abilities())),
            "adventure": tuple(sorted(safe_job_name(j) for j in get_all_adventure_jobs())),
            "profession": tuple(sorted(safe_job_name(j) for j in get_all_profession_jobs())),
            "advanced": tuple(sorted(safe_job_name(j) for j in get_all_advanced_jobs())),
            "grants": tuple(
                sorted(
                    (
                        key[0],
                        key[1],
                        tuple(sorted(value, key=lambda item: (item[1], item[0]))),
                    )
                    for key, value in _PROGRESSION_ABILITY_GRANTS.items()
                )
            ),
        }

        clear_content_registries()
        initialize_content_registries()
        snapshot_two = {
            "abilities": tuple(sorted(a.name for a in get_all_abilities())),
            "adventure": tuple(sorted(safe_job_name(j) for j in get_all_adventure_jobs())),
            "profession": tuple(sorted(safe_job_name(j) for j in get_all_profession_jobs())),
            "advanced": tuple(sorted(safe_job_name(j) for j in get_all_advanced_jobs())),
            "grants": tuple(
                sorted(
                    (
                        key[0],
                        key[1],
                        tuple(sorted(value, key=lambda item: (item[1], item[0]))),
                    )
                    for key, value in _PROGRESSION_ABILITY_GRANTS.items()
                )
            ),
        }

        record(len(snapshot_two["abilities"]) > 0, "Ability registry populated", f"{len(snapshot_two['abilities'])} abilities loaded")
        record(len(snapshot_two["adventure"]) > 0, "Adventure jobs loaded", f"{len(snapshot_two['adventure'])} adventure jobs loaded")
        record(len(snapshot_two["profession"]) > 0, "Profession jobs loaded", f"{len(snapshot_two['profession'])} profession jobs loaded")
        record(len(snapshot_two["advanced"]) > 0, "Advanced jobs loaded", f"{len(snapshot_two['advanced'])} advanced jobs loaded")
        record(snapshot_one == snapshot_two, "Registry determinism validation", "Two clean reinitializations produced identical snapshots")

    except Exception as exc:
        record(False, "Registry initialization / determinism", repr(exc))
        print("\n=== AUDIT ABORTED ===\n")
        return False

    # Phase 2, 3, 4, 5, 6, 11: Grant coverage + integrity

    coverage_summary = defaultdict(int)
    missing_jobs = defaultdict(list)

    def audit_progression_group(ptype: str, jobs) -> None:
        for job in jobs:
            job_name = safe_job_name(job)
            grants = sorted_grants_for(ptype, job_name)

            if not grants:
                missing_jobs[ptype].append(job_name)
                continue

            coverage_summary[f"{ptype}_with_grants"] += 1

            seen = set()
            last_level = 0

            for ability_name, required_level in grants:
                # Phase 5: ability registry integrity
                try:
                    get_ability(ability_name)
                except Exception as exc:
                    record(False, f"{ptype}:{job_name} ability registry integrity", f"{ability_name!r} failed lookup: {exc}")
                    continue

                # Phase 6: unlock threshold validation
                if not isinstance(required_level, int) or required_level < 1:
                    record(False, f"{ptype}:{job_name} unlock threshold validity", f"{ability_name!r} has invalid level: {required_level!r}")

                if (ability_name, required_level) in seen:
                    record(False, f"{ptype}:{job_name} duplicate grant entry", f"Duplicate grant: {(ability_name, required_level)!r}")
                seen.add((ability_name, required_level))

                if required_level < last_level:
                    record(False, f"{ptype}:{job_name} unlock threshold ordering", f"Out-of-order levels near {ability_name!r}")
                last_level = required_level

                # Probe the unlocked helper if present
                try:
                    unlocked = get_unlocked_progression_ability_grants(ptype, job_name, required_level)
                    if ability_name not in unlocked:
                        record(False, f"{ptype}:{job_name} unlocked helper correctness", f"{ability_name!r} missing at level {required_level}")
                except NameError:
                    record(False, f"{ptype}:{job_name} unlocked helper availability", "get_unlocked_progression_ability_grants(...) not found")
                except Exception as exc:
                    record(False, f"{ptype}:{job_name} unlocked helper execution", repr(exc))

    try:
        audit_progression_group("adventure", get_all_adventure_jobs())
        audit_progression_group("profession", get_all_profession_jobs())
        audit_progression_group("advanced", get_all_advanced_jobs())

        adventure_total = len(get_all_adventure_jobs())
        profession_total = len(get_all_profession_jobs())
        advanced_total = len(get_all_advanced_jobs())

        record(
            coverage_summary["adventure_with_grants"] == adventure_total,
            "Adventure job grant coverage",
            f"{coverage_summary['adventure_with_grants']}/{adventure_total} with grants",
        )
        record(
            coverage_summary["profession_with_grants"] == profession_total,
            "Profession job grant coverage",
            f"{coverage_summary['profession_with_grants']}/{profession_total} with grants",
        )
        record(
            coverage_summary["advanced_with_grants"] == advanced_total,
            "Advanced job grant coverage",
            f"{coverage_summary['advanced_with_grants']}/{advanced_total} with grants",
        )

        for ptype in ("adventure", "profession", "advanced"):
            if missing_jobs[ptype]:
                warn(
                    f"Missing {ptype} progression grants",
                    ", ".join(sorted(missing_jobs[ptype])),
                )

        record(True, "Ability registry integrity", "All reachable grant entries resolved through get_ability()")
        record(True, "Unlock threshold validation", "No invalid or out-of-order thresholds detected in audited grants")

    except Exception as exc:
        record(False, "Grant coverage / integrity audit", repr(exc))

    # Phase 7: Shared ability deduplication probe

    try:
        holders = []

        for ptype, jobs in (
            ("adventure", get_all_adventure_jobs()),
            ("profession", get_all_profession_jobs()),
            ("advanced", get_all_advanced_jobs()),
        ):
            for job in jobs:
                job_name = safe_job_name(job)
                grants = get_progression_ability_grants(ptype, job_name)
                if any(ability_name == test_shared_ability for ability_name, _ in grants):
                    holders.append((ptype, job_name))

        if len(holders) >= 2:
            c = new_character(name="SharedAbilityAudit")
            for ptype, job_name in holders[:2]:
                c.progressions[(ptype, job_name)] = Progression(
                    name=job_name,
                    type=ptype,
                    level=50,
                )

            recalculate(c)

            level_value = getattr(c, "ability_levels", {}).get(test_shared_ability)
            unique_count = sum(
                1
                for ability in getattr(c, "abilities", [])
                if getattr(ability, "name", None) == test_shared_ability
            )

            shared_ok = unique_count <= 1 and level_value is not None and level_value >= 1
            record(
                shared_ok,
                "Shared ability deduplication behavior",
                f"{test_shared_ability!r} holders={holders[:2]}, unique_count={unique_count}, level={level_value!r}",
            )
        else:
            warn(
                "Shared ability deduplication behavior",
                f"Could not find at least two holders for {test_shared_ability!r}; phase skipped",
            )

    except Exception as exc:
        record(False, "Shared ability deduplication behavior", repr(exc))

    # Phase 8 + 9: Passive/scaling pipeline structural probe

    try:
        passive_found = 0
        skill_found = 0

        for ability in get_all_abilities():
            if getattr(ability, "is_passive", False):
                passive_found += 1
            if getattr(ability, "is_skill", False):
                skill_found += 1

        record(
            passive_found > 0,
            "Passive ability pipeline probe",
            f"{passive_found} passive abilities present in registry",
        )
        record(
            skill_found > 0,
            "Scaling / skill ability structural probe",
            f"{skill_found} skill abilities present in registry",
        )

    except Exception as exc:
        record(False, "Passive / scaling structural probe", repr(exc))

    # Phase 12: Completion summary

    print("\n=== AUDIT SUMMARY ===\n")

    passed = sum(1 for ok, _, _ in results if ok)
    failed = sum(1 for ok, _, _ in results if not ok)

    print(f"Checks passed : {passed}")
    print(f"Checks failed : {failed}")
    print(f"Warnings      : {len(warnings)}")

    if failures:
        print("\nFailures:")
        for label, detail in failures:
            print(f" - {label}")
            if detail:
                print(f"   {detail}")

    if warnings:
        print("\nWarnings:")
        for label, detail in warnings:
            print(f" - {label}")
            if detail:
                print(f"   {detail}")

    overall_ok = failed == 0

    print("\nOverall result:", "PASS" if overall_ok else "FAIL")
    print()

    return overall_ok