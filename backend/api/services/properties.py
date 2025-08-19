from pathlib import Path

import pandas as pd

from api.services.s3 import s3_client
from api.config import config
from api.models.properties import Property, PropertyEntry


class Properties:
    def __init__(self):
        self._data = None

    async def get_data(self) -> pd.DataFrame:
        if self._data is not None:
            return self._data

        properties_full_path = Path(config.S3_PATH_PREFIX) / config.PROPERTIES_PATH
        body, _ = await s3_client.get_file(str(properties_full_path))
        data = pd.read_excel(body, config.PROPERTIES_SHEET)
        self._data = data
        return data

    async def get_property_entries(self) -> list[PropertyEntry]:
        data = await self.get_data()
        entries = []

        for _, row in data.iterrows():
            properties = [
                Property(name=col, value=str(row[col])) for col in data.columns
            ]
            entries.append(PropertyEntry(properties=properties))

        return entries
