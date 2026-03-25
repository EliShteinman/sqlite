from src.config import (
    DB_NAME_PATTERN,
    DB_PATH_TEMPLATE,
    SQLITE_URL_PREFIX,
    get_environment_config,
)
from src.enums import Environment
from src.exceptions import InvalidDBNameError


class SQLiteConnectionResolver:
    def resolve(self, db_name: str, environment: Environment) -> str:
        self._validate_db_name(db_name)
        env_config = get_environment_config(environment)
        path = DB_PATH_TEMPLATE.format(
            base_path=env_config.base_path,
            environment=environment.value,
            db_name=db_name,
        )
        return f"{SQLITE_URL_PREFIX}{path}"

    @staticmethod
    def _validate_db_name(db_name: str) -> None:
        if not db_name or not DB_NAME_PATTERN.match(db_name):
            raise InvalidDBNameError(db_name)
