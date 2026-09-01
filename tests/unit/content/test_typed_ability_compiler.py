from unittest.mock import patch

import pytest

from domain.abilities.adventure.berserker import berserker_job
from domain.abilities.compiler import compile_ability, compile_job
from domain.abilities.compiler_bridge.dispatch import dispatch_effect_compiler
from domain.abilities.compiler_bridge.future_seams import PHASE_6_RESERVED_EFFECT_SPECS
from domain.abilities.compiler_bridge.grants import register_compiled_job
from domain.abilities.definitions.definitions import (
    AbilityDefinition,
    ActivationSpec,
    GrantSpec,
    JobDefinition,
)
from domain.abilities.definitions.effects_spec import (
    ApplyStateSpec,
    DerivedStatBuffSpec,
    FlatBonus,
    ModifyNextAttackSpec,
    OnEventSpec,
)
from domain.content_registry import get_progression_ability_grants


def test_berserker_job_definition_contains_expected_typed_abilities():
    job_def = berserker_job()

    assert job_def.owner_type == "adventure"
    assert job_def.owner_name == "Berserker"
    assert len(job_def.abilities) == 2
    assert {ability.name for ability in job_def.abilities} == {
        "Furious Strike",
        "Tough as Leather",
    }


def test_compile_ability_compiles_furious_strike_to_runtime_ability(clean_registries):
    job_def = berserker_job()
    furious_strike_def = next(
        ability for ability in job_def.abilities if ability.name == "Furious Strike"
    )

    furious_strike = compile_ability(
        furious_strike_def,
        owner_name=job_def.owner_name,
        source_type=job_def.owner_type,
    )

    assert furious_strike.name == "Furious Strike"
    assert furious_strike.is_skill is True
    assert furious_strike.is_passive is False
    assert furious_strike.scales_with_level is True
    assert furious_strike.cost == 10
    assert furious_strike.cost_pool == "hp"
    assert furious_strike.duration == "1 Attack"
    assert furious_strike.target_type == "enemy"
    assert furious_strike.execute is not None
    assert furious_strike.effect_generator is None


def test_compile_ability_compiles_tough_as_leather_to_runtime_ability(clean_registries):
    job_def = berserker_job()
    tough_as_leather_def = next(
        ability for ability in job_def.abilities if ability.name == "Tough as Leather"
    )

    tough_as_leather = compile_ability(
        tough_as_leather_def,
        owner_name=job_def.owner_name,
        source_type=job_def.owner_type,
    )

    assert tough_as_leather.name == "Tough as Leather"
    assert tough_as_leather.is_passive is True
    assert tough_as_leather.is_skill is False
    assert tough_as_leather.cost == 0
    assert tough_as_leather.cost_pool is None
    assert tough_as_leather.duration == "Passive Constant"
    assert tough_as_leather.target_type == "self"
    assert tough_as_leather.execute is None
    assert tough_as_leather.effect_generator is not None


def test_compile_job_returns_runtime_abilities_and_grants(clean_registries):
    job_def = berserker_job()

    compiled_abilities, grants = compile_job(job_def)

    assert [ability.name for ability in compiled_abilities] == [
        "Furious Strike",
        "Tough as Leather",
    ]
    assert [(grant.name, grant.required_level) for grant in grants] == [
        ("Furious Strike", 1),
        ("Tough as Leather", 10),
    ]


def test_register_compiled_job_registers_implicit_progression_grants(clean_registries):
    job_def = berserker_job()

    compiled_abilities, grants = compile_job(job_def)
    registered_grants = register_compiled_job(job_def, compiled_abilities)

    assert registered_grants == grants
    assert get_progression_ability_grants("adventure", "Berserker") == (
        ("Furious Strike", 1),
        ("Tough as Leather", 10),
    )


def test_compile_job_preserves_explicit_grants_after_implicit_ones(clean_registries):
    job_def = JobDefinition(
        owner_type="adventure",
        owner_name="Bridge Tester",
        abilities=(
            AbilityDefinition(
                name="Bridge Skill",
                kind="skill",
                required_level=2,
                description="",
                activation=ActivationSpec(cost=1, duration="1 Attack", target="enemy"),
                effects=(ModifyNextAttackSpec(),),
            ),
        ),
        grants=(GrantSpec(name="Legacy Bonus", required_level=7),),
    )

    _, grants = compile_job(job_def)

    assert [(grant.name, grant.required_level) for grant in grants] == [
        ("Bridge Skill", 2),
        ("Legacy Bonus", 7),
    ]


def test_register_compiled_job_registers_explicit_and_implicit_grants(clean_registries):
    job_def = JobDefinition(
        owner_type="adventure",
        owner_name="Bridge Tester",
        abilities=(
            AbilityDefinition(
                name="Bridge Skill",
                kind="skill",
                required_level=2,
                description="",
                activation=ActivationSpec(cost=1, duration="1 Attack", target="enemy"),
                effects=(ModifyNextAttackSpec(),),
            ),
            AbilityDefinition(
                name="Legacy Bonus",
                kind="passive",
                required_level=9,
                description="",
                activation=ActivationSpec(duration="Passive Constant", target="self"),
                effects=(DerivedStatBuffSpec(stat="endurance", amount=(FlatBonus(1),)),),
            ),
        ),
        grants=(GrantSpec(name="Legacy Bonus", required_level=7),),
    )

    compiled_abilities, _ = compile_job(job_def)

    registered_grants = register_compiled_job(job_def, compiled_abilities)

    assert [(grant.name, grant.required_level) for grant in registered_grants] == [
        ("Bridge Skill", 2),
        ("Legacy Bonus", 9),
        ("Legacy Bonus", 7),
    ]
    assert get_progression_ability_grants("adventure", "Bridge Tester") == (
        ("Bridge Skill", 2),
        ("Legacy Bonus", 9),
        ("Legacy Bonus", 7),
    )


def test_dispatch_effect_compiler_routes_passive_effects_to_passive_module():
    defn = AbilityDefinition(
        name="Passive Boundary",
        kind="passive",
        required_level=1,
        description="",
        activation=ActivationSpec(duration="Passive Constant"),
        effects=(DerivedStatBuffSpec(stat="endurance", amount=(1,)),),
    )

    with patch(
        "domain.abilities.compiler_bridge.dispatch.compile_passive_effects",
        return_value="passive-result",
    ) as compile_passive:
        compiler = dispatch_effect_compiler(defn, owner_name="Boundary Owner")

        assert compiler(defn.effects) == "passive-result"
        compile_passive.assert_called_once_with(defn.effects, "Boundary Owner", "Passive Boundary")


def test_dispatch_effect_compiler_routes_stateful_passives_to_future_seam():
    defn = AbilityDefinition(
        name="State Boundary",
        kind="passive",
        required_level=1,
        description="",
        activation=ActivationSpec(duration="Passive Constant"),
        effects=(ApplyStateSpec(state="rage"),),
    )

    with patch(
        "domain.abilities.compiler_bridge.dispatch.compile_state_effects",
        return_value="state-result",
    ) as compile_state:
        compiler = dispatch_effect_compiler(defn, owner_name="Boundary Owner")

        assert compiler(defn.effects) == "state-result"
        compile_state.assert_called_once_with(defn.effects, "Boundary Owner", "State Boundary")


def test_dispatch_effect_compiler_routes_active_effects_to_active_module():
    defn = AbilityDefinition(
        name="Active Boundary",
        kind="skill",
        required_level=1,
        description="",
        activation=ActivationSpec(cost=1, duration="1 Attack", target="enemy"),
        effects=(ModifyNextAttackSpec(),),
    )

    with patch(
        "domain.abilities.compiler_bridge.dispatch.compile_active_effects",
        return_value="active-result",
    ) as compile_active:
        compiler = dispatch_effect_compiler(defn, owner_name="Boundary Owner")

        assert compiler(defn.effects) == "active-result"
        compile_active.assert_called_once_with(defn.effects, "Boundary Owner", "Active Boundary")


def test_dispatch_effect_compiler_routes_event_effects_to_future_seam():
    defn = AbilityDefinition(
        name="Event Boundary",
        kind="skill",
        required_level=1,
        description="",
        activation=ActivationSpec(cost=1, duration="Instant", target="self"),
        effects=(OnEventSpec(event_name="on_hit", effect=object()),),
    )

    with patch(
        "domain.abilities.compiler_bridge.dispatch.compile_event_effects",
        return_value="event-result",
    ) as compile_event:
        compiler = dispatch_effect_compiler(defn, owner_name="Boundary Owner")

        assert compiler(defn.effects) == "event-result"
        compile_event.assert_called_once_with(defn.effects, "Boundary Owner", "Event Boundary")


@pytest.mark.parametrize(
    ("defn", "expected_message"),
    [
        (
            AbilityDefinition(
                name="State Boundary",
                kind="passive",
                required_level=1,
                description="",
                activation=ActivationSpec(duration="Passive Constant"),
                effects=(ApplyStateSpec(state="rage"),),
            ),
            "Boundary Owner.State Boundary: state-driven compilation is reserved for phase 6",
        ),
        (
            AbilityDefinition(
                name="Event Boundary",
                kind="skill",
                required_level=1,
                description="",
                activation=ActivationSpec(cost=1, duration="Instant", target="self"),
                effects=(OnEventSpec(event_name="on_hit", effect=object()),),
            ),
            "Boundary Owner.Event Boundary: event-driven compilation is reserved for phase 6",
        ),
    ],
)
def test_compile_ability_surfaces_phase_6_reserved_effects(defn, expected_message):
    with pytest.raises(NotImplementedError, match=expected_message):
        compile_ability(defn, owner_name="Boundary Owner", source_type="adventure")


def test_phase_6_reserved_effect_types_are_explicitly_tracked():
    assert PHASE_6_RESERVED_EFFECT_SPECS == (ApplyStateSpec, OnEventSpec)
