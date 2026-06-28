from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.infrastructure.database import get_db
from src.config.settings import settings
from src.application import oauth_service
from src.domain.security import create_access_token

router = APIRouter(prefix="/auth/github", tags=["Authentication"])

@router.get("/login")
async def github_login():
    """Redirects to GitHub OAuth consent screen."""
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope=read:user user:email repo"
    )
    return RedirectResponse(url=github_auth_url)

@router.get("/callback")
async def github_callback(
    response: Response,
    code: str = Query(...),
    db: Session = Depends(get_db)
):
    """Handles GitHub callback, creates/updates user, and issues JWT."""
    try:
        # 1. Exchange code for access token
        access_token = await oauth_service.exchange_github_code_for_token(code)
        
        # 2. Fetch user profile and email
        github_profile = await oauth_service.fetch_github_user_profile(access_token)
        email = await oauth_service.fetch_github_primary_email(access_token)
        
        # 3. Upsert user in database
        user = oauth_service.upsert_user(db, github_profile, email)
        
        # 4. Create JWT
        jwt_token = create_access_token(data={"sub": str(user.id), "role": user.role})
        
        # 5. Set JWT as HTTP-Only Cookie
        response = RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard")
        response.set_cookie(
            key="access_token",
            value=f"Bearer {jwt_token}",
            httponly=True,
            secure=False, # Set to True in production
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
