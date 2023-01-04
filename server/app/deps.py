from fastapi import Depends, HTTPException

from app.db.deps import get_db, DbDependency
from app.models import User

from app.models.user import get_current_user

__all__ = ('get_db', 'DbDependency')



def get_current_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user
