from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.networks import EmailStr
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select

from app import schemas, deps
from app.models import User, Token
from app.db import Session
from app.core import settings
from app.utils import send_new_account_email

# from app.utils import send_new_account_email

# from app.utils import (
#     generate_password_reset_token,
#     send_reset_password_email,
#     verify_password_reset_token,
# )

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def user_list(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_superuser),
) -> list[User]:
    return list((
        db.scalars(select(User).order_by(User.id).offset(skip).limit(limit))
    ))


@router.post("/", response_model=schemas.User)
def user_create(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Create new user.
    """
    manager = User.crud
    user = manager.get(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = manager.create(db, obj_in=user_in)
    # if settings.EMAILS_ENABLED and user_in.email:
    #     send_new_account_email(
    #         email_to=user_in.email, username=user_in.email, password=user_in.password
    #     )
    return user


@router.put("/me/", response_model=schemas.User)
def user_me_update(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = User.crud.update(db, obj=current_user, obj_in=user_in)
    return user


@router.get("/me/", response_model=schemas.User)
def user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/register/", response_model=schemas.User)
async def user_register(
    *,
    db: Session = Depends(deps.get_db),
    request: Request,
    password: str = Body(...),
    email: EmailStr = Body(...),
    username: str = Body(...),
) -> User:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = User.crud.get_or_none(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )

    user = User.crud.create(db, password=password, email=email, username=username)
    url = request.url
    link = f'{url.scheme}://{url.hostname}/api/user/activate/{user.id}/'
    send_new_account_email(link=link, email=user.email, username=user.username)
    return user


@router.get("/activate/{user_id}/", response_model=schemas.User)
def user_activate(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
) -> Any:
    # TODO: use signed token
    user = User.crud.get_or_404(db, id=user_id)
    user.crud.update(db, user, is_active=True)
    return user

@router.post("/login/")
def user_login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = User.crud.authenticate(
            db,
            username=form_data.username, password=form_data.password
        )
    except NoResultFound as e:
        raise HTTPException(status_code=400, detail="Incorrect email or password") from e

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    token = Token.crud.create(db, user_id=user.id)
    jwt_token = token.encode()
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": user,
    }

# @router.post("/password-recovery/", response_model=schemas.Msg)
# def user_password_recovery(email: str, db: Session = Depends(deps.get_db)) -> Any:
#     """
#     Password Recovery
#     """
#     user = User.crud.get_by_email(email=email)
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the system.",
#         )
#     password_reset_token = generate_password_reset_token(email=email)
#     send_reset_password_email(
#         email_to=user.email, email=email, token=password_reset_token
#     )
#     return {"msg": "Password recovery email sent"}
# @router.post("/password-reset/", response_model=schemas.Msg)
# def user_reset_password(
#     token: str = Body(...),
#     new_password: str = Body(...),
#     db: Session = Depends(deps.get_db),
# ) -> Any:
#     """
#     Reset password
#     """
#     email = verify_password_reset_token(token)
#     if not email:
#         raise HTTPException(status_code=400, detail="Invalid token")
#     user = User.crud.get_by_email(email=email)
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the system.",
#         )
#     if not user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     hashed_password = get_password_hash(new_password)
#     user.hashed_password = hashed_password
#     db.add(user)
#     db.commit()
#     return {"msg": "Password updated successfully"}


@router.get("/{user_id}/", response_model=schemas.User)
def user_detail(
    user_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = User.crud.get(db, id=user_id)
    if user == current_user:
        return user
    if not user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}/", response_model=schemas.User)
def user_update(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Update a user.
    """
    user = User.crud.get_or_404(db, id=user_id)
    user = User.crud.update(db, obj=user, obj_in=user_in)
    return user
