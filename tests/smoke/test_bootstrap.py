from domain.content_registry import has_ability, initialize_content_registries


def test_content_bootstrap_runs_without_error(clean_registries):
    initialize_content_registries(force=True)


def test_expected_shared_abilities_exist_after_bootstrap(initialized_content):
    assert has_ability("Growl") is True
    assert has_ability("Fast as Death") is True
    assert has_ability("Quickdraw") is True
