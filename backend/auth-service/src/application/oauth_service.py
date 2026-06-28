import httpx
from sqlalchemy.orm import Session
from src.domain.models import User
from src.config.settings import settings
from datetime import datetime, timezone

async def exchange_github_code_for_token(code: str) -> str:
    url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.GITHUB_REDIRECT_URI
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            raise ValueError(f"GitHub Auth Error: {result.get('error_description')}")
            
        return result["access_token"]

async def fetch_github_user_profile(access_token: str) -> dict:
    url = "https://api.github.com/user"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def fetch_github_primary_email(access_token: str) -> str:
    url = "https://api.github.com/user/emails"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        emails = response.json()
        
        for email_info in emails:
            if email_info.get("primary") and email_info.get("verified"):
                return email_info["email"]
                
        if emails:
            return emails[0]["email"]
            
        raise ValueError("No verified email found on GitHub account")

def upsert_user(db: Session, github_profile: dict, email: str) -> User:
    github_id = github_profile["id"]
    
    user = db.query(User).filter(User.github_id == github_id).first()
    
    if user:
        # Update existing user
        user.name = github_profile.get("name")
        user.avatar_url = github_profile.get("avatar_url")
        user.email = email
        user.last_login = datetime.now(timezone.utc)
    else:
        # Create new user
        user = User(
            github_id=github_id,
            email=email,
            name=github_profile.get("name"),
            avatar_url=github_profile.get("avatar_url"),
            role="Owner" # For this demo, first user is owner, but ideally handled by RBAC logic
        )
        db.add(user)
        
    db.commit()
    db.refresh(user)
    return user
