from fastapi import Depends, HTTPException, status, Request
import jwt
from pydantic import BaseModel
from src.config.settings import settings

class TokenData(BaseModel):
    user_id: str | None = None

def get_current_user(request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = None
    # 1. Try to get from Cookie
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        if cookie_token.startswith("Bearer "):
            token = cookie_token.split(" ")[1]
        else:
            token = cookie_token
            
    # 2. Try to get from Header if not in cookie
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    return token_data
