from domain.content_registry import has_ability, initialize_content_registries


def test_shared_ability_present_after_init(clean_registries):
    initialize_content_registries(force=True)
    assert has_ability("Growl") is True
