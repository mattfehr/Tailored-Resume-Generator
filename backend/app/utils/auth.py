from jose import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from app.config import Config

auth_scheme = HTTPBearer()

def verify_jwt(token: str):
    print("DEBUG: Using LEGACY Supabase HS256 JWT verification")

    try:
        payload = jwt.decode(
            token,
            Config.SUPABASE_JWT_SECRET,  # <- legacy JWT secret from Supabase dashboard
            algorithms=["HS256"],
            options={
                "verify_aud": False  # Supabase access tokens do not include an audience
            }
        )

        return payload

    except Exception as e:
        print("JWT DECODE ERROR:", e)
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired JWT"
        )


async def get_current_user(token=Depends(auth_scheme)):
    credentials = token.credentials
    payload = verify_jwt(credentials)
    return payload
