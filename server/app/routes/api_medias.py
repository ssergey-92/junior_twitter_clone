"""Module with APIRouter for url api/medias ."""

from typing import Annotated, Union

from fastapi import Form, Header, Response, UploadFile, APIRouter

from app.project_logger import project_logger
from app.services import media_file
from app.schemas import AddMediaOut, ErrorResponse

router = APIRouter()


@router.post(
    path="/api/medias",
    description="Add media file",
    responses={
        201: {"description": "Created", "model": AddMediaOut},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        422: {"description": "Validation Error", "model": ErrorResponse},
    },
)
async def add_media_file(
    file: Annotated[UploadFile, Form()],
    api_key: Annotated[str, Header()],
    response: Response,
) -> Union[AddMediaOut, ErrorResponse]:
    """Endpoint for adding media file.

    Call handler, then set http status code and return response.

    Args:
        file (UploadFile): media file
        api_key (str): username who adding media_file
        response (Response): fastapi response model for endpoint

    Returns:
        Union[AddMediaOut, ErrorResponse]: success adding media or
            error message with corresponding http status code.

    """
    project_logger.info(f"{api_key=}, {file.filename=}")
    details, http_code = await media_file.add_media_file(api_key, file)
    project_logger.info(f"{details=}, {http_code=}")
    response.status_code = http_code
    if http_code == 201:
        return AddMediaOut(**details)
    return ErrorResponse(**details)
