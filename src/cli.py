from domain.content_registry import initialize_content_registries
from observability import configure_logging

from cli_support.session import run_cli


configure_logging()
initialize_content_registries()


if __name__ == "__main__":
    run_cli()
