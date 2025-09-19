from pydantic import BaseModel


class CorrelationResult(BaseModel):
    slope: float
    intercept: float
    R2: float
    MAE: float
    outlier_indices: list[int]
