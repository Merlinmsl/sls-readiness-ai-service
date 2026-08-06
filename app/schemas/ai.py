from typing import Literal

from pydantic import BaseModel


class AIStatusResponse(BaseModel):
    """Non-sensitive AI provider configuration status."""

    provider: Literal["mock", "gemini"]
    configured: bool
    model: str
    live_request_performed: bool
    