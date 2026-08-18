from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from core.users.service import UserService
from database.connection import get_db
from app.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await UserService.get(db, user_id)
    if user is None:
        raise credentials_exception
    return user

def require_permission(required_permission: str):
    async def dependency(current_user: User = Depends(get_current_user)):
        # Check if user has permission via roles
        user_perms = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_perms.add(perm.codename)
        if required_permission not in user_perms and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Permission denied")
        return current_user
    return dependency