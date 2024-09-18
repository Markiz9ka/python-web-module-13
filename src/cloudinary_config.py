import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import os
load_dotenv()


cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)
