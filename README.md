# microprofile

A microservice for user profile creation and data storage for client applications. Each client application stores its data under its own isolated namespace so no schema changes are needed when a client modifies its data structure.

## Directory Layout

```
microprofile/
├── pyproject.toml          # Dependencies and project metadata
├── main.py                 # FastAPI app entry point
├── app/
│   ├── config.py           # Loads settings from .env.mongodb
│   ├── database.py         # MongoDB connection and collection
│   ├── models.py           # Pydantic request/response schemas
│   └── routers/
│       └── profiles.py     # All endpoint handlers
└── tests/
    ├── conftest.py         # Shared fixtures (mock database)
    └── test_profiles.py    
```

## Setup

**Prerequisites:** Python 3.13+, [uv](https://docs.astral.sh/uv/), MongoDB.

1. Clone the repository.

2. Create `.env.mongodb` in the project root. Example using a local database:
   ```
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB_NAME=microprofile
   ```

3. Install dependencies:
   ```
   uv sync
   ```

4. Start the server:
   ```
   uv run uvicorn main:app --reload
   ```

The service runs on `http://localhost:8000`. Interactive API docs are at `http://localhost:8000/docs`.

## Running Tests

```
uv run pytest tests/ -v
```

---

## Endpoints

### POST /profiles
Create a new user profile.

**Request body:**
```json
{"username": "string", "password": "string"}
```

**Responses:**
| Status         | Meaning                                     |
|----------------|---------------------------------------------|
| `201 Created`  | Profile created and returns the new user ID |
| `409 Conflict` | Username already taken                      |

**Success response:**
```json
{"id": "507f1f77bcf86cd799439011"}
```

---

### GET /profiles/{user_id}
Retrieve a user's profile.

**Path parameters:**
- `user_id`: The 24-character ID returned by `POST /profiles`

**Responses:**
| Status          | Meaning              |
|-----------------|----------------------|
| `200 OK`        | Returns profile data |
| `404 Not Found` | User does not exist  |

**Success response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "username": "string",
  "created_at": "2026-06-03T00:00:00Z"
}
```

---

### PATCH /profiles/{user_id}
Update a user's username, password, or both. At least one field must be provided.

**Path parameters:**
- `user_id`: The 24-character ID returned by `POST /profiles`

**Request body** (all fields optional, at least one required):
```json
{"username": "new_name", "password": "new_password"}
```

**Responses:**
| Status            | Meaning                                |
|-------------------|----------------------------------------|
| `200 OK`          | Updated successfully                   |
| `400 Bad Request` | No fields provided                     |
| `404 Not Found`   | User does not exist                    |
| `409 Conflict`    | Username already taken by another user |

---

### DELETE /profiles/{user_id}
Permanently delete a user profile and all associated data.

**Path parameters:**
- `user_id`: The 24-character ID returned by `POST /profiles`

**Responses:**
| Status          | Meaning              |
|-----------------|----------------------|
| `200 OK`        | Deleted successfully |
| `404 Not Found` | User does not exist  |

---

### PUT /profiles/{user_id}/apps/{app_id}
Store or update app-specific data for a user. The `app_id` is chosen by your application — pick a consistent string that identifies your app (e.g. `dungeon_crawler`, `wildlife_tracker`). The request body is arbitrary JSON; no schema is enforced. Each app's data is stored in isolation and will never overwrite another app's data.

**Path parameters:**
- `user_id`: The 24-character ID returned by `POST /profiles`
- `app_id`: Your application's identifier (you decide this string)

**Request body:** Any JSON object.
```json
{"score": 100, "level": 5, "inventory": ["sword", "shield"]}
```

**Responses:**
| Status          | Meaning                  |
|-----------------|--------------------------|
| `200 OK`        | Data stored successfully |
| `404 Not Found` | User does not exist      |

---

### GET /profiles/{user_id}/apps/{app_id}
Retrieve the stored data for a specific app.

**Path parameters:**
- `user_id`: The 24-character ID returned by `POST /profiles`
- `app_id`: Your application's identifier

**Responses:**
| Status          | Meaning                                                 |
|-----------------|---------------------------------------------------------|
| `200 OK`        | Returns the stored JSON object                          |
| `404 Not Found` | User does not exist, or no data stored for this app yet |

**Success response:** the exact JSON object previously stored via `PUT`.
```json
{"score": 100, "level": 5, "inventory": ["sword", "shield"]}
```

---

## Notes

- `user_id` is a MongoDB ObjectId. Store it after calling `POST /profiles`. It's needed for all subsequent calls.
- Passwords are stored as bcrypt hashes. Plain-text passwords are never persisted.
- App data is stored at `client_data.{app_id}` in the user document. Calling `PUT` again for the same `app_id` overwrites that app's data only.
- Calling `GET /profiles/{user_id}` does not expose password hashes or other apps' data.
