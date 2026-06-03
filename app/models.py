from datetime import datetime
from pydantic import BaseModel


class ProfileCreateRequest(BaseModel):
    """
    Request body for creating a new user profile.
    """

    username: str
    password: str


class ProfileCreateResponse(BaseModel):
    """
    Response body returned after successful profile creation.
    """

    id: str


class PatchProfileRequest(BaseModel):
    """
    Request body for updating a user profile's username.
    """

    username: str | None = None
    password: str | None = None


class ProfileResponse(BaseModel):
    """
    Response body for a user profile lookup.
    """

    id: str
    username: str
    created_at: datetime
