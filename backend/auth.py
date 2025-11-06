from fastapi import APIRouter, HTTPException, Depends, status
from passlib.context import CryptContext
from librarytools import UserTable, RTT
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime, timezone
from jose import JWTError, jwt
import uuid
from fastapi import Request

SECRET_KEY = "TESTKEY" # FIX LATER
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 1

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

userTable = UserTable()
refreshTokenTable = RTT()

# Pydantic Models
class UserRegister(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class CurrentUser(BaseModel):
    user_id: int
    username: str


# Utility Functions
def verify_password(plain: str, hash: str):
    if not isinstance(plain, str):
        plain = str(plain)
    return pwd_context.verify(plain[:72], hash)

def get_password_hash(password: str):
    if not isinstance(password, str):
        password = str(password)
    return pwd_context.hash(password[:72])

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    jti = str(uuid.uuid4())
    to_encode = data.copy()
    if not data.get("username"):
        raise HTTPException(status_code=401, detail="Error: Invalid refresh token")
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"jti": jti, "exp": expire, "scope": "refresh_token"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    refreshTokenTable.store_refresh_token(jti=jti, username=data.get("username"), expires_at=int(expire.timestamp()))
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_refresh_token(token: str) -> dict:
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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("scope") != "refresh_token":
            raise HTTPException(status_code=401, detail="Invalid token scope.")
        return payload
    except JWTError:
        raise credentials_exception
    
async def get_current_userID(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    print(f"Received token: {token}")  # 👈 TEMP DEBUG
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")  # 👈 TEMP DEBUG
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        
        if user_id is None:
            raise credentials_exception
        user = CurrentUser(user_id=int(user_id), username=username)
        return user
    except JWTError:
        raise credentials_exception


 
# Routes
@router.post("/register")
def register_user(user: UserRegister):
    username = user.username
    password = user.password
    # check if the username already exists
    if userTable.usernameCheck(username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pw = get_password_hash(password)
    try:
        userTable.addUser(username, hashed_pw)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error adding user to users table.")
    
    return {"message": "User created successfully"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = userTable.usernameCheck(form_data.username) 
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password.")        

    id, username, hashed_pw = user
    id = str(id)

    if not verify_password(form_data.password, hashed_pw):
        raise HTTPException(status_code=400, detail="Invalid username or password.")
    
    access_token = create_access_token({"sub": id, "username": username})
    refresh_token = create_refresh_token({"sub": id, "username": username})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
def refresh(refresh_info: RefreshRequest):
    payload = verify_refresh_token(refresh_info.refresh_token)
    if payload.get("scope") != "refresh_token":
        raise HTTPException(status_code=401, detail="Invalid token scope")
    user_id = payload.get('sub')
    username = payload.get('username')  # Get the username from the payload
    jti = payload.get('jti')
    
    if not jti or not user_id:
        return HTTPException(status_code=401, detail="Invalid refresh token.")
    
    refreshTokenTable.revoke_refresh_token(jti=jti)

    new_access_token = create_access_token({"sub": user_id, "username": username})
    new_refresh_token = create_refresh_token({"sub": user_id, "username": username})

    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.post("/logout")
def logout(logout_info: LogoutRequest):
    try:
        payload = verify_refresh_token(logout_info.refresh_token)
    except HTTPException:
        return {"message": "Logged Out1"}
    
    jti = payload.get("jti")
    if jti:
        refreshTokenTable.revoke_refresh_token(jti=jti)
    return {"message": "Logged Out2"}