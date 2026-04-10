from domain.content_registry import clear_content_registries, initialize_content_registries


def test_force_reload_does_not_raise_duplicate_registration_errors():
    clear_content_registries()
    initialize_content_registries(force=True)

    # A second full rebuild should also succeed.
    clear_content_registries()
    initialize_content_registries(force=True)
