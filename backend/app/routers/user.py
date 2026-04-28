"""User profile router — view/update profile, change password."""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from app.database import users_collection
from app.models.user import UserResponse, UserProfileUpdate, ChangePassword
from app.utils.auth import hash_password, verify_password
from app.utils.deps import get_current_user
from app.utils.export import auto_export_users_to_file
from bson import ObjectId

router = APIRouter(prefix="/api/user", tags=["User"])


def _user_response(user: dict) -> UserResponse:
    """Build a UserResponse from a MongoDB user document (excludes password)."""
    return UserResponse(
        id=str(user["_id"]),
        name=user.get("full_name", user.get("name", "")),
        email=user["email"],
        role=user["role"],
        phone_number=user.get("phone_number", ""),
        dob=user.get("dob", ""),
        profile_pic=user.get("profile_pic", ""),
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(user=Depends(get_current_user)):
    """Fetch current user data (password hash excluded)."""
    return _user_response(user)


@router.patch("/update", response_model=UserResponse)
async def update_profile(updates: UserProfileUpdate, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    """Update profile details (name, phone, dob, profile_pic)."""
    update_data = {}

    if updates.full_name is not None:
        update_data["full_name"] = updates.full_name
        update_data["name"] = updates.full_name  # keep legacy field in sync

    if updates.phone_number is not None:
        update_data["phone_number"] = updates.phone_number

    if updates.dob is not None:
        update_data["dob"] = updates.dob

    if updates.profile_pic is not None:
        update_data["profile_pic"] = updates.profile_pic

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await users_collection.find_one_and_update(
        {"_id": user["_id"]},
        {"$set": update_data},
        return_document=True,
    )

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    background_tasks.add_task(auto_export_users_to_file)

    return _user_response(result)


@router.post("/change-password")
async def change_password(payload: ChangePassword, user=Depends(get_current_user)):
    """Change password: verify current password, then hash and store the new one."""
    # Step 1: Verify the current password matches the stored hash
    if not verify_password(payload.current_password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Step 2: Hash the new password and update the database
    new_hash = hash_password(payload.new_password)
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"password": new_hash}},
    )

    return {"message": "Password changed successfully"}
