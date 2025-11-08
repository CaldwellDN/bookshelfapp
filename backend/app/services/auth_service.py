from datetime import timedelta, datetime, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.database.repositories.user_repo import UserRepository
from app.database.repositories.token_repo import TokenRepository
from app.core.config import settings
from app.database.models.user import User
from app.database.models.token import RefreshToken
from fastapi import HTTPException
import uuid


class AuthService:
    def __init__(self, user_repo: UserRepository, token_repo: TokenRepository):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain: str, hash: str):
        if not isinstance(plain, str):
            plain = str(plain)
        return self.pwd_context.verify(plain[:72], hash)

    def get_password_hash(self, password: str):
        if not isinstance(password, str):
            password = str(password)
        return self.pwd_context.hash(password[:72])

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict):
        jti = str(uuid.uuid4())
        to_encode = data.copy()
        if not data.get("username"):
            raise HTTPException(status_code=401, detail="Error: Invalid refresh token")
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"jti": jti, "exp": expire, "scope": "refresh_token"})
        
        # Store refresh token in database
        token_entry = RefreshToken(
            jti=jti,
            username=data.get("username"),
            expires_at=int(expire.timestamp()),
            revoked=False
        )
        self.token_repo.create(token_entry)
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def verify_refresh_token(self, token: str) -> dict:
        """
        Verifies and decodes a JWT refresh token.
        Raises an HTTPException if invalid or expired
        """
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("scope") != "refresh_token":
                raise HTTPException(status_code=401, detail="Invalid token scope.")
            return payload
        except JWTError:
            raise credentials_exception

    def register_user(self, username: str, password: str):
        # Check if user already exists
        existing_user = self.user_repo.get_by_username(username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        # Hash password and create user
        hashed_pw = self.get_password_hash(password)
        
        user = User(
            username=username,
            password=hashed_pw
        )
        
        created_user = self.user_repo.create(user)
        return {"message": "User created successfully"}

    def login_user(self, username: str, password: str):
        user = self.user_repo.get_by_username(username)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid username or password.")

        if not self.verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Invalid username or password.")

        access_token = self.create_access_token({"sub": str(user.id), "username": user.username})
        refresh_token = self.create_refresh_token({"sub": str(user.id), "username": user.username})

        return {
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "token_type": "bearer"
        }

    def refresh_token(self, refresh_token_str: str):
        payload = self.verify_refresh_token(refresh_token_str)
        if payload.get("scope") != "refresh_token":
            raise HTTPException(status_code=401, detail="Invalid token scope")
        
        user_id = payload.get('sub')
        username = payload.get('username')
        jti = payload.get('jti')

        if not jti or not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token.")

        # Revoke the old refresh token
        self.token_repo.revoke_token(jti)

        new_access_token = self.create_access_token({"sub": user_id, "username": username})
        new_refresh_token = self.create_refresh_token({"sub": user_id, "username": username})

        return {
            "access_token": new_access_token, 
            "refresh_token": new_refresh_token, 
            "token_type": "bearer"
        }

    def logout_user(self, refresh_token_str: str):
        try:
            payload = self.verify_refresh_token(refresh_token_str)
        except HTTPException:
            return {"message": "Logged Out"}

        jti = payload.get("jti")
        if jti:
            self.token_repo.revoke_token(jti)
        return {"message": "Logged Out"}