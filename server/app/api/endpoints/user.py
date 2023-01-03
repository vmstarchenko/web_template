from fastapi import Depends, APIRouter

from app import deps
from app.db import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.models.user import auth_backend, current_active_user, fastapi_users

router = APIRouter()

router.include_router(fastapi_users.get_auth_router(auth_backend))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
router.include_router(fastapi_users.get_reset_password_router())
router.include_router(fastapi_users.get_verify_router(UserRead))
router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))


@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@router.get("/verify/{user_id}/", response_model=UserRead)
async def user_verify(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
) -> User:
    # TODO: use signed token instead user_id
    user = await User.crud.get_or_404(db, id=user_id)
    await User.crud.update(db, user, is_verified=True)
    return user
