from sqlalchemy.orm import Session
from auth.models import User 
from cloudinary.uploader import upload
from cloudinary_config import cloudinary
import database
import fastapi

def update_user_avatar(user_id: int, avatar_file: bytes, db = fastapi.Depends(database.get_database)) -> str:
    response = upload(avatar_file, folder='avatars')
    avatar_url = response['secure_url']

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.avatar_url = avatar_url
        db.commit()
        return avatar_url
    else:
        raise Exception("User not found")
