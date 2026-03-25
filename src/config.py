import re
from dataclasses import dataclass

from src.enums import Environment
from src.exceptions import EnvironmentNotFoundError

DB_NAME_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9_\-]+$")
DB_PATH_TEMPLATE: str = "{base_path}/{environment}/{db_name}.db"
SQLITE_URL_PREFIX: str = "sqlite:///"
BYTES_PER_MB: int = 1024 * 1024


@dataclass(frozen=True)
class EnvironmentConfig:
    base_path: str
    max_size_mb: int


ENVIRONMENT_SETTINGS: dict[Environment, EnvironmentConfig] = {
    Environment.DEVELOPMENT: EnvironmentConfig(
        base_path="/data",
        max_size_mb=500,
    ),
    Environment.STAGING: EnvironmentConfig(
        base_path="/data",
        max_size_mb=1000,
    ),
    Environment.PRODUCTION: EnvironmentConfig(
        base_path="/data",
        max_size_mb=2000,
    ),
    Environment.TESTS: EnvironmentConfig(
        base_path="/data",
        max_size_mb=100,
    ),
}


def get_environment_config(env: Environment) -> EnvironmentConfig:
    config = ENVIRONMENT_SETTINGS.get(env)
    if config is None:
        raise EnvironmentNotFoundError(env)
    return config
