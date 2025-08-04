"""
Handle / uploads
"""

from api.services.s3 import s3_client

from fastapi import Query, APIRouter, HTTPException
from fastapi.responses import Response


from pydantic import BaseModel


class FilePath(BaseModel):
    paths: list[str]


router = APIRouter()


@router.get(
    "/get/{file_path:path}",
    status_code=200,
    description="Download any assets from S3",
)
async def get_file(
    file_path: str,
    download: bool = Query(
        False, alias="d", description="Download file instead of inline display"
    ),
):
    (body, content_type) = await s3_client.get_file(file_path)
    if body:
        if download:
            # download file
            return Response(
                content=body,
                media_type=content_type,
                headers={
                    "Content-Disposition": "attachment; filename="
                    + file_path.split("/")[-1]
                },
            )
        else:
            # inline image
            return Response(content=body)
    else:
        raise HTTPException(status_code=404, detail="File not found")


@router.get(
    "/list/{directory_path:path}",
    status_code=200,
    description="List files in a given directory path on S3",
)
async def list_files(
    directory_path: str,
):
    try:
        files = await s3_client.list_files(directory_path)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
