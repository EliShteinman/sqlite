from pydantic import BaseModel, ConfigDict, Field

from src.enums import ColumnType


class ColumnModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    table_name: str
    name: str
    type: ColumnType


class TableModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str


class DatabaseModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    max_size_mb: int
    tables: list[TableModel] = Field(default_factory=list)
    columns: list[ColumnModel] = Field(default_factory=list)
