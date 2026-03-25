from src.enums import Environment


class EnvironmentNotFoundError(Exception):
    def __init__(self, environment: Environment) -> None:
        super().__init__(
            f"No configuration found for environment '{environment.value}'"
        )
        self.environment = environment
