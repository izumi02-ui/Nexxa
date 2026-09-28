from dataclasses import dataclass

from app.config import Settings


@dataclass(frozen=True)
class Environment:
    name: str
    debug: bool
    is_development: bool
    is_staging: bool
    is_production: bool


def get_environment(settings: Settings) -> Environment:
    name = settings.environment.lower().strip()

    if name not in {"development", "staging", "production"}:
        raise ValueError(
            "ENVIRONMENT must be one of: development, staging, production"
        )

    return Environment(
        name=name,
        debug=settings.debug,
        is_development=name == "development",
        is_staging=name == "staging",
        is_production=name == "production",
    )