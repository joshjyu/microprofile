from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException
import bcrypt

from app.database import profiles
from app.models import (
    ProfileCreateRequest,
    ProfileCreateResponse,
    PatchProfileRequest,
    ProfileResponse,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])
# bcrypt algorithm for hashing


@router.post("", response_model=ProfileCreateResponse, status_code=201)
async def create_profile(
    body: ProfileCreateRequest,
) -> ProfileCreateResponse:
    """
    Create a new user profile.

    Parameters:
      body: Request containing username and password.
    Returns:
      The newly created profile's unique ID.
    """
    if await profiles.find_one({"username": body.username}):
        raise HTTPException(status_code=409, detail="Username already taken")

    password_hash = bcrypt.hashpw(
        body.password.encode(), bcrypt.gensalt()
    ).decode()
    result = await profiles.insert_one(
        {
            "username": body.username,
            "password_hash": password_hash,
            "created_at": datetime.now(timezone.utc),
            "client_data": {},
        }
    )

    return ProfileCreateResponse(id=str(result.inserted_id))


@router.get("/{user_id}", response_model=ProfileResponse, status_code=200)
async def get_profile(user_id: str) -> ProfileResponse:
    """
    Retrieve a user profile by ID.

    Parameters:
      user_id: The unique ID of the target user profile.
    Returns:
      The user's profile data excluding password and app data.
    """
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="User not found")

    doc = await profiles.find_one({"_id": oid})
    if doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    return ProfileResponse(
        id=str(doc["_id"]),
        username=doc["username"],
        created_at=doc["created_at"],
    )


@router.get("/{user_id}/apps/{app_id}", status_code=200)
async def get_app_data(user_id: str, app_id: str) -> dict[str, Any]:
    """
    Retrieve app-specific data for a user profile.

    Parameters:
      user_id: The unique ID of the target user profile.
      app_id: The client application's identifier.
    Returns:
      The stored JSON data for the given app.
    """
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="User not found")

    doc = await profiles.find_one({"_id": oid})
    if doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    app_data = doc.get("client_data", {}).get(app_id)
    if app_data is None:
        raise HTTPException(status_code=404, detail="App data not found")

    return app_data


@router.put("/{user_id}/apps/{app_id}", status_code=200)
async def update_app_data(
    user_id: str,
    app_id: str,
    body: dict[str, Any],
) -> dict[str, str]:
    """
    Store or update app-specific data for a user profile.

    Parameters:
      user_id: The unique ID of the target user profile.
      app_id: The client application's identifier.
      body: Arbitrary JSON payload to store under client_data.{app_id}.
    Returns:
      A confirmation message.
    """
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="User not found")

    result = await profiles.update_one(
        {"_id": oid}, {"$set": {f"client_data.{app_id}": body}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "ok"}


@router.patch("/{user_id}", status_code=200)
async def patch_profile(
    user_id: str, body: PatchProfileRequest
) -> dict[str, str]:
    """
    Update the username or password of an existing user profile.

    Parameters:
      user_id: The unique ID of the profile to update.
      body: Request containing the new username and/or password.
    Returns:
      A confirmation message.
    """
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="User not found")

    updates: dict = {}

    if body.username is not None:
        if await profiles.find_one(
            # $ne ensures current user is excluded from duplicate username check
            {"username": body.username, "_id": {"$ne": oid}}
        ):
            raise HTTPException(
                status_code=409, detail="Username already taken"
            )
        updates["username"] = body.username

    if body.password is not None:
        updates["password_hash"] = bcrypt.hashpw(
            body.password.encode(), bcrypt.gensalt()
        ).decode()

    if not updates:
        raise HTTPException(
            status_code=400, detail="No fields provided to update"
        )

    result = await profiles.update_one({"_id": oid}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "ok"}


@router.delete("/{user_id}", status_code=200)
async def delete_profile(user_id: str) -> dict[str, str]:
    """
    Delete a user profile by ID.

    Parameters:
      user_id: The unique ID of the profile to delete.
    Returns:
      A confirmation message.
    """
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="User not found")

    result = await profiles.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "ok"}
