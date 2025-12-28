from fastapi import APIRouter, Request, Depends, HTTPException
from app.services.user_service import get_user
from app.services.user_service import create_user
from app.utils.auth import authenticate_user
from app.utils.auth import extract_user_email

router = APIRouter(
    dependencies=[Depends(authenticate_user)]
)

@router.post("/user/register/")
async def usage(request: Request, _: None = Depends(authenticate_user)):
    email = extract_user_email(request)
    result = await create_user(email)
    return {"response": result}

@router.get("/user/usage/")
async def usage(request: Request, _: None = Depends(authenticate_user)):
    email = extract_user_email(request)
    result = await get_user(email)
    if result is None:
        raise HTTPException(status_code=404, detail="User Not Found")
                        
    return {"response": result}