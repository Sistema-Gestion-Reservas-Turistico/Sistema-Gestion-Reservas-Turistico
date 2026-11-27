from fastapi import APIRouter, Depends, Path, status
from collections.abc import Callable

from app.domain.entities.destination import Destination
from app.api.dependencies.autorizacion import autorizar_administrador_jwt
from app.api.dependencies.destinations import obtener_caso_guardar_destino
from app.api.responses import JSONResponse
from app.api.schemas.destinations import (
    DestinationData,
    DestinationErrorResponse,
    DestinationInput as DestinationInputSchema,
    DestinationResponse,
)
from app.domain.entities.destination import DestinationNotice
from app.domain.exceptions.destinations import (
    DestinationNotFoundError,
    DestinationPersistenceError,
    DuplicateDestinationError,
    InvalidNoticePeriodError,
    InvalidTourismTypeError,
    MunicipalityNotFoundError,
)
from app.services.use_cases.save_destination import (
    DestinationInput,
    SaveDestinationUseCase,
)


router = APIRouter(prefix="/api/v1/geo/destinos", tags=["Destinations"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DestinationResponse,
    responses={
        400: {"model": DestinationErrorResponse},
        401: {"model": DestinationErrorResponse},
        403: {"model": DestinationErrorResponse},
        404: {"model": DestinationErrorResponse},
        409: {"model": DestinationErrorResponse},
        503: {"model": DestinationErrorResponse},
    },
    summary="Create a tourist destination",
    description=(
        "Creates a destination for an enabled municipality using active tourism "
        "type parameters. Requires an Administrator bearer token."
    ),
)
def create_destination(
    request: DestinationInputSchema,
    _: None = Depends(autorizar_administrador_jwt),
    use_case: SaveDestinationUseCase = Depends(obtener_caso_guardar_destino),
) -> DestinationResponse | JSONResponse:
    return _save(
        lambda: use_case.create(_to_domain(request)),
        "Destination created successfully",
    )


@router.put(
    "/{destination_id}",
    response_model=DestinationResponse,
    responses={
        400: {"model": DestinationErrorResponse},
        401: {"model": DestinationErrorResponse},
        403: {"model": DestinationErrorResponse},
        404: {"model": DestinationErrorResponse},
        409: {"model": DestinationErrorResponse},
        503: {"model": DestinationErrorResponse},
    },
    summary="Update a tourist destination",
    description="Updates a destination using the same validations as creation.",
)
def update_destination(
    request: DestinationInputSchema,
    destination_id: int = Path(gt=0),
    _: None = Depends(autorizar_administrador_jwt),
    use_case: SaveDestinationUseCase = Depends(obtener_caso_guardar_destino),
) -> DestinationResponse | JSONResponse:
    return _save(
        lambda: use_case.update(destination_id, _to_domain(request)),
        "Destination updated successfully",
    )


def _save(
    operation: Callable[[], Destination], success_message: str
) -> DestinationResponse | JSONResponse:
    try:
        destination = operation()
    except ValueError as error:
        return _error(status.HTTP_400_BAD_REQUEST, str(error), "INVALID_DESTINATION")
    except DestinationNotFoundError as error:
        return _error(status.HTTP_404_NOT_FOUND, str(error), "DESTINATION_NOT_FOUND")
    except MunicipalityNotFoundError as error:
        return _error(status.HTTP_404_NOT_FOUND, str(error), "MUNICIPALITY_NOT_FOUND")
    except InvalidTourismTypeError as error:
        return _error(status.HTTP_400_BAD_REQUEST, str(error), "INVALID_TOURISM_TYPE")
    except InvalidNoticePeriodError as error:
        return _error(status.HTTP_400_BAD_REQUEST, str(error), "INVALID_NOTICE_PERIOD")
    except DuplicateDestinationError as error:
        return _error(status.HTTP_409_CONFLICT, str(error), "DESTINATION_ALREADY_EXISTS")
    except DestinationPersistenceError as error:
        return _error(
            status.HTTP_503_SERVICE_UNAVAILABLE, str(error), "SERVICE_UNAVAILABLE"
        )
    return _success(destination, success_message)


def _to_domain(request: DestinationInputSchema) -> DestinationInput:
    return DestinationInput(
        name=request.name,
        municipality_id=request.municipality_id,
        tourism_types=tuple(request.tourism_types),
        description=request.description,
        activities=tuple(request.activities),
        main_image_url=request.main_image_url,
        destination_status=request.destination_status,
        notices=tuple(
            DestinationNotice(
                notice_type=notice.notice_type,
                message=notice.message,
                valid_from=notice.valid_from,
                valid_until=notice.valid_until,
            )
            for notice in request.notices
        ),
    )


def _success(destination: Destination, message: str) -> DestinationResponse:
    return DestinationResponse(
        success=True,
        message=message,
        data=DestinationData(
            destination_id=destination.id,
            name=destination.name,
            municipality_id=destination.municipality_id,
            tourism_types=list(destination.tourism_types),
            destination_status=destination.destination_status,
            coordinates_status=destination.coordinates_status,
            status=destination.status,
        ),
    )


def _error(code: int, message: str, error_code: str) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        content={
            "success": False,
            "message": message,
            "errorCode": error_code,
            "data": None,
        },
    )
