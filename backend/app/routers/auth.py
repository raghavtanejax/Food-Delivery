"""Authentication router — signup, login, and current user."""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from app.database import users_collection
from app.models.user import UserSignup, UserLogin, UserResponse, TokenResponse
from app.utils.auth import hash_password, verify_password, create_access_token
from app.utils.deps import get_current_user
from app.utils.export import auto_export_users_to_file
from datetime import datetime, timezone

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _user_response(user: dict) -> UserResponse:
    """Build a UserResponse from a MongoDB user document."""
    return UserResponse(
        id=str(user["_id"]),
        name=user.get("full_name", user.get("name", "")),
        email=user["email"],
        role=user["role"],
        phone_number=user.get("phone_number", ""),
        dob=user.get("dob", ""),
        profile_pic=user.get("profile_pic", ""),
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup, background_tasks: BackgroundTasks):
    """Register a new user (Customer or Admin)."""
    email_lower = user_data.email.lower().strip()
    existing = await users_collection.find_one({"email": email_lower})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user document
    user_doc = {
        "name": user_data.name,
        "full_name": user_data.name,
        "email": email_lower,
        "password": hash_password(user_data.password),
        "role": user_data.role.value,
        "phone_number": "",
        "dob": "",
        "profile_pic": "",
        "created_at": datetime.now(timezone.utc),
    }

    result = await users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    # Automatically save updated user list to a file
    background_tasks.add_task(auto_export_users_to_file)

    # Generate JWT
    token = create_access_token({"sub": str(result.inserted_id), "role": user_data.role.value})

    return TokenResponse(access_token=token, user=_user_response(user_doc))


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login with email and password, receive JWT."""
    email_lower = credentials.email.lower().strip()
    user = await users_collection.find_one({"email": email_lower})
    # Also attempt case-insensitive match for older records
    if not user:
        user = await users_collection.find_one({"email": {"$regex": f"^{email_lower}$", "$options": "i"}})

    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user_id = str(user["_id"])
    token = create_access_token({"sub": user_id, "role": user["role"]})

    return TokenResponse(access_token=token, user=_user_response(user))


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return _user_response(user)
