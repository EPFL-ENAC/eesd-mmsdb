import tempfile
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi_cache.decorator import cache

from api.models.compute import CorrelationResult
from api.services.correlation import compute_correlation_parameters
from api.services.line_minimum_trace import calculate_line_minimum_trace

router = APIRouter()


@router.get("/correlation")
@cache()
async def get_correlation_parameters(
    x_column: str,
    y_column: str,
) -> CorrelationResult:
    """Get correlation parameters between two columns in a dataset."""
    return await compute_correlation_parameters(x_column, y_column)


@router.post("/line")
async def compute_line_minimum_trace(
    image: UploadFile,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    real_length: float,
    real_height: float,
    analysis_type: int,
    boundary_margin: int,
) -> dict:
    """Compute the line of minimum trace."""
    if (
        not hasattr(image, "content_type")
        or image.content_type is None
        or not image.content_type.startswith("image/")
    ):
        raise HTTPException(status_code=400, detail="Invalid image file")

    with tempfile.NamedTemporaryFile(delete=True) as temp_image:
        temp_image.write(await image.read())
        temp_image.flush()

        try:
            result = calculate_line_minimum_trace(
                temp_image.name,
                start_coords=[start_x, start_y],
                end_coords=[end_x, end_y],
                real_length=real_length,
                real_height=real_height,
                calculate_LMT=analysis_type,
                boundary_margin=boundary_margin,
                return_plot=False,
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
