from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DestinationNotice:
    notice_type: str
    message: str
    valid_from: datetime | None = None
    valid_until: datetime | None = None


@dataclass(frozen=True)
class Destination:
    id: int
    name: str
    description: str | None
    municipality_id: int
    tourism_types: tuple[str, ...]
    activities: tuple[str, ...]
    main_image_url: str | None
    destination_status: str
    coordinates_status: str
    status: str
    notices: tuple[DestinationNotice, ...]
