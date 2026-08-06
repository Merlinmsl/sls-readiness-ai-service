from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response returned by the service health endpoint."""

    status: Literal["healthy"]
    service: str
    version: str
    environment: str