import tempfile
from fastapi import APIRouter, HTTPException, UploadFile

from api.models.compute import CorrelationResult
from api.services.correlation import compute_correlation_parameters
from api.services.line_minimum_trace import calculate_line_minimum_trace

router = APIRouter()


@router.get("/correlation")
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
                temp_image.name, [start_x, start_y], [end_x, end_y], return_plot=False
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
