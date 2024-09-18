import fastapi
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
import fastapi.security
import database
import auth.exceptions
import auth.service
import auth.models
import auth.schemas
#import services.email_service as email_service
import uuid
from services.user_service import update_user_avatar

auth_service = auth.service.Auth()
router = fastapi.APIRouter(prefix='/auth', tags=["auth"])

@router.post(
    "/signup",
    status_code=fastapi.status.HTTP_201_CREATED
)
async def signup(
    body: auth.schemas.User,
    db = fastapi.Depends(database.get_database)
) -> auth.schemas.UserDb:
    user = db.query(auth.models.User).filter(auth.models.User.username==body.username).first()
    if user is not None:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_409_CONFLICT,
            detail="Account already exists"
        )

    hashed_password = auth_service.hash_password(body.password)

    verification_token = str(uuid.uuid4())

    new_user = auth.models.User(
        username=body.username,
        hash_password=hashed_password,
        verification_token=verification_token
    )

    db.add(new_user)
    db.commit()

    return new_user


@router.post("/login")
async def login(
    body: fastapi.security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db = fastapi.Depends(database.get_database)
) -> auth.schemas.Token:
    user = db.query(auth.models.User).filter(auth.models.User.username==body.username).first()
    if user is None:
        raise auth.exceptions.AuthException("no such user")

    verification = auth_service.verify_password(body.password, user.hash_password)
    if not verification:
        raise auth.exceptions.AuthException("incorrect credentials")
    
    if not user.is_verified:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )

    refresh_token = await auth_service.create_refresh_token(payload={"sub": body.username})
    access_token = await auth_service.create_access_token(payload={"sub": body.username})

    user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }


@router.post("/logout")
async def logout(
    user = fastapi.Depends(auth_service.get_user),
    db = fastapi.Depends(database.get_database)
) -> auth.schemas.LogoutResponse:
    user.refresh_token = None
    db.commit()

    return {"result": "Success"}

@router.get("/verify/{token}")
async def verify_email(token: str, db = fastapi.Depends(database.get_database)):
    user = db.query(auth.models.User).filter(auth.models.User.verification_token == token).first()
    if user is None:
        raise fastapi.HTTPException(status_code=400, detail="Invalid verification token")
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    
    return {"message": "Email verified successfully"}

@router.post("/users/{user_id}/avatar")
async def upload_avatar(user_id: int, file: UploadFile = File(...), db = fastapi.Depends(database.get_database)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    try:
        avatar_url = update_user_avatar(user_id, await file.read(), db)
        return {"avatar_url": avatar_url}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))