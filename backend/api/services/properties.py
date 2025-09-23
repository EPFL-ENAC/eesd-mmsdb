from pathlib import Path
from io import StringIO

import pandas as pd
from fastapi import HTTPException

from api.views.files import get_local_file_content
from api.config import config
from api.models.properties import Column, Table


class Properties:
    def __init__(self) -> None:
        self._data: pd.DataFrame | None = None
        self._stone_data: dict[str, pd.DataFrame] = {}
        self._properties: Table | None = None
        self._property_columns: dict[str, list[str]] = {}
        self._stone_properties: dict[str, Table] = {}

    async def get_data(self) -> pd.DataFrame:
        if self._data is not None:
            return self._data

        properties_full_path = (
            Path(config.LFS_CLONED_REPO_PATH) / "data" / config.PROPERTIES_PATH
        )
        body, _ = get_local_file_content(properties_full_path)
        if body is None:
            raise HTTPException(
                status_code=404,
                detail=f"Properties file not found at {properties_full_path}",
            )
        data = pd.read_csv(StringIO(body.decode("utf-8")))
        self._data = data
        return data

    async def get_stone_data(self, wall_id: str) -> pd.DataFrame:
        if wall_id in self._stone_data:
            return self._stone_data[wall_id]

        properties_full_path = (
            Path(config.LFS_CLONED_REPO_PATH)
            / "data"
            / config.STONE_PROPERTIES_DIR_PATH
            / f"{wall_id}.csv"
        )
        body, _ = get_local_file_content(properties_full_path)
        if body is None:
            raise HTTPException(
                status_code=404,
                detail=f"Stone properties file for wall_id '{wall_id}' not found.",
            )

        data = pd.read_csv(StringIO(body.decode("utf-8")))
        self._stone_data[wall_id] = data
        return data

    async def get_property_entries(self) -> Table:
        if self._properties is not None:
            return self._properties

        data = await self.get_data()
        columns = []

        for col in data.columns:
            column = Column(
                name=str(col).strip(), values=data[col].astype(str).tolist()
            )
            columns.append(column)

        self._properties = columns
        return columns

    async def get_property_column_values(self, column_name: str) -> list[str]:
        if column_name in self._property_columns:
            return self._property_columns[column_name]

        properties = await self.get_property_entries()

        for column in properties:
            if column.name == column_name:
                self._property_columns[column_name] = column.values
                return column.values

        raise HTTPException(
            status_code=404,
            detail=f"Column '{column_name}' not found in properties table.",
        )

    async def get_stones_property_entries(self, wall_id: str) -> Table:
        if wall_id in self._stone_properties:
            return self._stone_properties[wall_id]

        data = await self.get_stone_data(wall_id)
        columns = []

        for col in data.columns:
            column = Column(name=col.strip(), values=data[col].astype(str).tolist())
            columns.append(column)

        self._stone_properties[wall_id] = columns
        return columns


properties = Properties()
