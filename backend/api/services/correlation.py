import numpy as np
from api.models.compute import CorrelationResult
from api.services.properties import properties
from sklearn.linear_model import HuberRegressor
from sklearn.metrics import mean_absolute_error


async def compute_correlation_parameters(
    x_column: str, y_column: str, allowed_categories: list[str] = []
) -> CorrelationResult:
    x_raw = await properties.get_property_column_values(
        x_column, allowed_categories=allowed_categories
    )
    y_raw = await properties.get_property_column_values(
        y_column, allowed_categories=allowed_categories
    )

    x_valid = []
    y_valid = []

    for x_val, y_val in zip(x_raw, y_raw):
        try:
            x_float = float(x_val)
            y_float = float(y_val)
            x_valid.append(x_float)
            y_valid.append(y_float)
        except (ValueError, TypeError):
            continue

    x1 = np.array(x_valid, dtype=float)
    y1 = np.array(y_valid, dtype=float)

    # ==============================
    # ROBUST REGRESSION (Huber)
    # ==============================
    X = x1.reshape(-1, 1)
    y = y1

    huber = HuberRegressor().fit(X, y)

    robust_slope = huber.coef_[0]
    robust_intercept = huber.intercept_

    # Predictions
    y_predicted_robust = huber.predict(X)

    # R²
    SS_res = np.sum((y - y_predicted_robust) ** 2)
    SS_tot = np.sum((y - np.mean(y)) ** 2)
    R2_robust = 1 - SS_res / SS_tot

    # MAE
    MAE_robust = mean_absolute_error(y, y_predicted_robust)

    # Outliers (residual > MAD threshold)
    residuals = y - y_predicted_robust
    mad_s = np.median(np.abs(residuals - np.median(residuals)))
    outliers_ind = np.where(np.abs(residuals) > 1 * mad_s)[0]

    return CorrelationResult(
        slope=robust_slope,
        intercept=robust_intercept,
        R2=R2_robust,
        MAE=MAE_robust,
        outlier_indices=outliers_ind.tolist(),
    )
