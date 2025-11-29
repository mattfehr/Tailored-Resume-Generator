import requests
from jose import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from app.config import Config

auth_scheme = HTTPBearer()

# Cache JWKS to avoid repeated network calls
JWKS_CACHE = None

def get_jwks():
    global JWKS_CACHE
    if JWKS_CACHE is None:
        jwks_url = f"{Config.SUPABASE_URL}/auth/v1/keys"
        response = requests.get(jwks_url)
        if response.status_code != 200:
            raise Exception("Failed to fetch JWKS keys")
        JWKS_CACHE = response.json()
    return JWKS_CACHE


def verify_jwt(token: str):
    jwks = get_jwks()
    header = jwt.get_unverified_header(token)

    for key in jwks['keys']:
        if key['kid'] == header['kid']:
            public_key = key
            break
    else:
        raise HTTPException(status_code=401, detail="Invalid JWT key ID")

    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[public_key["alg"]],
            audience=Config.SUPABASE_URL,
            options={"verify_aud": False}  # Supabase tokens sometimes omit audience
        )
        return payload

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired JWT") from e


async def get_current_user(token=Depends(auth_scheme)):
    credentials = token.credentials
    payload = verify_jwt(credentials)
    return payload
