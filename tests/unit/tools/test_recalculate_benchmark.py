from tools.recalculate_benchmark import build_scenarios, run_benchmarks


def test_recalculate_benchmark_scenarios_build_and_measure(initialized_content):
    scenarios = build_scenarios()

    assert [scenario.name for scenario in scenarios] == [
        "human_baseline",
        "bear_berserker_brewer",
        "crossbreed_multi_progression",
    ]

    results = run_benchmarks(warm_iterations=2)

    assert [result.scenario for result in results] == [scenario.name for scenario in scenarios]

    for result in results:
        assert result.cold_ms >= 0
        assert result.warm.iterations == 2
        assert result.warm.min_ms >= 0
        assert result.warm.max_ms >= result.warm.min_ms

