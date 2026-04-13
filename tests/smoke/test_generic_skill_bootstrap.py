from domain.content_registry import (
    clear_content_registries,
    initialize_content_registries,
    has_ability,
)


def test_generic_skills_register_on_force_reload():
    clear_content_registries()
    initialize_content_registries(force=True)

    assert has_ability("Riding")