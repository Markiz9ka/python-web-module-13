import jose.jwt
import typing
import fastapi
import fastapi.security
import datetime
import passlib.context
import os
from dotenv import load_dotenv
load_dotenv()
import auth.models
import auth.exceptions
import database

class Auth:
    HASH_CONTEXT = passlib.context.CryptContext(schemes=["bcrypt"])
    ALGORITHM = os.environ.get('ALGORITHM')
    SECRET = os.environ.get('SECRET_KEY')
    oauth2_schema = fastapi.security.OAuth2PasswordBearer("/auth/login")

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        return self.HASH_CONTEXT.verify(plain_password, hashed_password)

    def hash_password(self, plain_password: str) -> str:
        return self.HASH_CONTEXT.hash(plain_password)

    async def create_access_token(
        self, payload: dict[str, typing.Any]
    ) -> str:
        current_time = datetime.datetime.now(datetime.timezone.utc)
        expire_time = current_time + datetime.timedelta(minutes=15)

        payload.update({
            "iat": current_time,
            "exp": expire_time,
            "scope": "access_token"
        })

        jwt_token = jose.jwt.encode(
            payload, self.SECRET, self.ALGORITHM
        )

        return jwt_token


    async def create_refresh_token(
        self, payload: dict[str, typing.Any]
    ) -> str:
        current_time = datetime.datetime.now(datetime.timezone.utc)
        expire_time = current_time + datetime.timedelta(days=7)

        payload.update({
            "iat": current_time,
            "exp": expire_time,
            "scope": "refresh_token"
        })

        jwt_token = jose.jwt.encode(
            payload, self.SECRET, self.ALGORITHM
        )

        return jwt_token

    def get_user(
        self,
        token = fastapi.Depends(oauth2_schema),
        db = fastapi.Depends(database.get_database)
    ) -> auth.models.User:
        try:
            payload = jose.jwt.decode(
                token, self.SECRET, algorithms=[self.ALGORITHM]
            )

            if payload['scope'] == "access_token":
                username = payload.get("sub")

                if username is None:
                    raise auth.exceptions.AuthException("Invalid user")

                user = db.query(auth.models.User).filter(auth.models.User.username==username).first()
                if user is None:
                    raise auth.exceptions.AuthException("No such user")
                
                if user.refresh_token is None:
                    raise auth.exceptions.AuthException("No way")

                return user

            elif payload['scope'] == "refresh_token":
                raise auth.exceptions.AuthException("What are you doing?")
            else:
                raise auth.exceptions.AuthException("Do you know the secret?")
        except jose.JWTError as e:
            raise auth.exceptions.AuthException(e)
