from pathlib import Path
from io import StringIO

import pandas as pd
from fastapi import HTTPException

from api.services.s3 import s3_client
from api.config import config
from api.models.properties import Column, Table


class Properties:
    def __init__(self):
        self._data = None
        self._stone_data = {}

    async def get_data(self) -> pd.DataFrame:
        if self._data is not None:
            return self._data

        properties_full_path = Path(config.S3_PATH_PREFIX) / config.PROPERTIES_PATH
        body, _ = await s3_client.get_file(str(properties_full_path))
        data = pd.read_excel(body, config.PROPERTIES_SHEET)
        self._data = data
        return data

    async def get_stone_data(self, wall_id: str) -> pd.DataFrame:
        if wall_id in self._stone_data:
            return self._stone_data[wall_id]

        properties_full_path = (
            Path(config.S3_PATH_PREFIX)
            / config.STONE_PROPERTIES_DIR_PATH
            / f"{wall_id}.csv"
        )
        body, _ = await s3_client.get_file(str(properties_full_path))
        if not body:
            raise HTTPException(
                status_code=404,
                detail=f"Stone properties file for wall_id '{wall_id}' not found.",
            )

        data = pd.read_csv(StringIO(body.decode("utf-8")))
        self._stone_data[wall_id] = data
        return data

    async def get_property_entries(self) -> Table:
        data = await self.get_data()
        columns = []

        for col in data.columns:
            column = Column(
                name=str(col).strip(), values=data[col].astype(str).tolist()
            )
            columns.append(column)

        return columns

    async def get_stones_property_entries(self, wall_id: str) -> Table:
        data = await self.get_stone_data(wall_id)
        columns = []

        for col in data.columns:
            column = Column(name=col.strip(), values=data[col].astype(str).tolist())
            columns.append(column)

        return columns
