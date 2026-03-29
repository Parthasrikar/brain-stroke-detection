from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os
import logging
import traceback
from dotenv import load_dotenv
from apps.api.models.user import User

logger = logging.getLogger(__name__)

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "your_super_secret_key_here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
MAX_PASSWORD_LENGTH = 128  # Argon2 can handle up to 2^32 bytes, but we set a reasonable limit

router = APIRouter(prefix="/auth", tags=["Auth"])

# Use Argon2 for better security and no byte-length limitations
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- Models ---
class UserAuth(BaseModel):
    email: EmailStr
    password: str

class UserRegister(UserAuth):
    full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str

# --- Utilities ---
def verify_password_length(password: str) -> tuple[bool, Optional[str]]:
    """Validate password length. Returns (is_valid, error_message)"""
    if len(password) == 0:
        return False, "Password cannot be empty"
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password cannot be longer than {MAX_PASSWORD_LENGTH} characters"
    return True, None

def verify_password(plain_password, hashed_password):
    """Verify plain password against hashed password. Includes error handling."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password):
    """Hash password with validation and error handling."""
    # Validate password length before hashing
    is_valid, error_msg = verify_password_length(password)
    if not is_valid:
        raise ValueError(error_msg)
    
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        raise ValueError(f"Failed to hash password: {str(e)}")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await User.find_one(User.email == email)
    if user is None:
        raise credentials_exception
    return user

# --- Routes ---
@router.post("/register", response_model=UserOut)
async def register(user_data: UserRegister):
    """Register a new user with email and password validation."""
    try:
        existing_user = await User.find_one(User.email == user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate password before hashing
        is_valid, error_msg = verify_password_length(user_data.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Hash password
        try:
            password_hash = get_password_hash(user_data.password)
        except ValueError as e:
            logger.error(f"Password hashing failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        user = User(
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name
        )
        await user.insert()
        logger.info(f"User registered successfully: {user_data.email}")
        return UserOut(id=str(user.id), email=user.email, full_name=user.full_name)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error detailed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return JWT access token."""
    try:
        user = await User.find_one(User.email == form_data.username)
        if not user:
            logger.warning(f"Login attempt for non-existent user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(form_data.password, user.password_hash):
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        logger.info(f"User logged in successfully: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(id=str(current_user.id), email=current_user.email, full_name=current_user.full_name)
