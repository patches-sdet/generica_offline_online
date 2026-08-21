# Phase 9 - Stakeholder Presentation Roadmap

## Goal
Turn the technical cleanup into a simple and credible story a stakeholder can understand within the first 2 months.

## The message to communicate
The system is **not** being rewritten. It is being made safer and easier to extend by introducing typed Python definitions that compile into the existing engine.

## Recommended presentation structure

### 1. Problem
Current content authoring is hard to validate and harder to evolve safely.

Repository anchors you can mention:
- current YAML loading is thin in [`load_abilities_from_yaml()`](src/domain/abilities/loader.py:9)
- current runtime ability objects are already Python-native in [`Ability`](src/domain/abilities/factory.py:6)
- existing bootstrap already relies on Python module loading in [`initialize_content_registries()`](src/domain/content_registry.py:229)

### 2. Chosen solution
Introduce typed Python definition objects plus a compiler/bridge.

### 3. Why this is lower risk
- no full rewrite
- incremental migration
- existing tests remain useful
- one pilot job proves the pattern first

### 4. Proof point
Berserker is migrated from [`src/domain/abilities/adventure/berserker.yml`](src/domain/abilities/adventure/berserker.yml) into typed Python content.

### 5. Outcome
Future jobs can follow the same pattern with less risk and less confusion.

## Suggested stakeholder slide outline

### Slide 1: the issue
“The engine is workable, but ability content is authored in a fragile way.”

### Slide 2: the decision
“We are keeping the engine and improving the content-authoring layer.”

### Slide 3: the architecture
“Typed Python definitions -> compiler/bridge -> existing runtime objects.”

### Slide 4: the pilot
“Berserker proves the pattern.”

### Slide 5: the evidence
“Bootstrap still works, tests still pass, and the new model is easier to read.”

### Slide 6: next step
“Repeat the pattern for more jobs only after the pilot is stable.”

## Beginner-friendly speaking script
Use a plain-English framing like this:

> We are not rebuilding the whole abilities engine. We are improving how abilities are defined so future work becomes safer and faster. We start with one representative job, prove it works with the current system, and then repeat the pattern.

## What a stakeholder most likely cares about
- Is this safer than a rewrite?
- Will progress be visible within 2 months?
- Will this reduce future delivery cost?
- Is there a clear proof point?

This plan gives “yes” answers to all four.

## Deliverables to show by the end of 2 months
- the main guide in [`dist/abilities_cleanup_main_guide.md`](dist/abilities_cleanup_main_guide.md)
- the phase docs in [`dist/README.md`](dist/README.md)
- migrated Berserker source work later
- focused tests demonstrating parity later

## Exit criteria for this phase
- You can explain the cleanup in business language.
- You can show one credible proof point.
- You can explain the next migration step without overpromising a rewrite.
