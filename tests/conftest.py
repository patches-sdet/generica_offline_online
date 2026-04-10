"""Global pytest fixtures for the Generica test suite.

These fixtures are intentionally conservative and align with the current
registry-first architecture. They avoid assuming future runtime/leveling APIs.
"""

from __future__ import annotations

import pytest

from domain.content_registry import clear_content_registries, initialize_content_registries


@pytest.fixture
def clean_registries():
    """Reset registries before and after a test.

    This is the safest default while the content loader and shared ability
    modules are still evolving.
    """
    clear_content_registries()
    yield
    clear_content_registries()


@pytest.fixture
def initialized_content(clean_registries):
    """Initialize all registries from a clean state."""
    initialize_content_registries(force=True)
    return True
