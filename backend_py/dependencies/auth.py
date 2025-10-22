from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..utils.supabase_client import get_supabase_client

security = HTTPBearer(auto_error=True)


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    jwt = creds.credentials
    supabase = get_supabase_client()
    try:
        res = supabase.auth.get_user(jwt)
        user = res.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"id": user.id, "email": user.email}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
