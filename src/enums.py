from enum import Enum


class ColumnType(str, Enum):
    TEXT = "TEXT"
    INTEGER = "INTEGER"
    REAL = "REAL"
    BLOB = "BLOB"


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTS = "tests"
