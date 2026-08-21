# Abilities System Cleanup Documentation Set

This folder contains the current documentation set for the abilities-system cleanup plan.

The chosen direction is **Option C**: Python-first cleanup using code-first typed definition objects. That means this repository should evolve away from fragile YAML parsing as the primary authoring surface, while also avoiding a risky full rewrite.

## Read this set in order
1. [`dist/abilities_cleanup_main_guide.md`](dist/abilities_cleanup_main_guide.md) — single self-contained recommendation and beginner guide.
2. [`dist/phase_01_architectural_direction.md`](dist/phase_01_architectural_direction.md) — why Option C is the right call.
3. [`dist/phase_02_product_scoping_and_deferments.md`](dist/phase_02_product_scoping_and_deferments.md) — what stays out of scope for the next 2 months.
4. [`dist/phase_03_typed_definitions_layer.md`](dist/phase_03_typed_definitions_layer.md) — define typed Python ability-definition objects.
5. [`dist/phase_04_effect_specs.md`](dist/phase_04_effect_specs.md) — define structured effect-spec objects.
6. [`dist/phase_05_compiler_bridge.md`](dist/phase_05_compiler_bridge.md) — compile typed definitions into runtime [`Ability`](src/domain/abilities/factory.py:6) objects.
7. [`dist/phase_06_migrating_berserker.md`](dist/phase_06_migrating_berserker.md) — use Berserker as the first migration pilot from [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml).
8. [`dist/phase_07_bootstrap_and_registry_updates.md`](dist/phase_07_bootstrap_and_registry_updates.md) — wire the new layer into content loading and registration.
9. [`dist/phase_08_testing_and_validation.md`](dist/phase_08_testing_and_validation.md) — prove the migration is safe.
10. [`dist/phase_09_stakeholder_presentation_roadmap.md`](dist/phase_09_stakeholder_presentation_roadmap.md) — turn the technical work into a 2-month stakeholder narrative.

## Repository anchors
- Current YAML loading entrypoint: [`load_abilities_from_yaml()`](src/domain/abilities/loader.py:9)
- Current dynamic builder: [`build_ability()`](src/domain/abilities/builders/_job_builder.py:39)
- Runtime ability type: [`Ability`](src/domain/abilities/factory.py:6)
- Registry bootstrap area: [`initialize_content_registries()`](src/domain/content_registry.py:229)
- Current Berserker example: [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml)
- Existing architecture context: [`dist/compiled_update.md`](dist/compiled_update.md)
- Existing baseline boundary ADR: [`dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md`](dist/ADR_0001_BASELINE_PATH_AND_PRODUCT_BOUNDARY.md)

## Intended audience
This set is written for a learning-oriented solo developer who needs to make steady technical progress and also explain the plan credibly to a stakeholder within 2 months.
