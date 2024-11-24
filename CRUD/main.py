from pathlib import Path
import sys
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from contextlib import asynccontextmanager
from config import get_async_session, init_db, close_db
from db.models import User
from typing import List
from pydantic import BaseModel
from utils.encryption import encrypt_password, verify_password
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from shared.schemas.user import User_Login, User_Create

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(
    title="User API",
    lifespan=lifespan,
    debug=True
)

@app.post("/users/register", status_code=status.HTTP_204_NO_CONTENT)
async def register_user(
    user_create: User_Create,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        logger.debug(f"Attempting to register user: {user_create.username}")
        
        query = select(User).where(User.username == user_create.username)
        result = await db.execute(query)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )
        
        query = select(User).where(User.email == user_create.email)
        result = await db.execute(query)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        encrypted_password = encrypt_password(user_create.password)
        
        new_user = User(
            username=user_create.username,
            password=encrypted_password,
            email=user_create.email,
            fname=user_create.f_name,
            lname=user_create.l_name
        )
        
        db.add(new_user)
        await db.commit()
        logger.debug("User registered successfully")
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/search")
async def search_users(
    name: str = None,
    email: str = None,
    role: str = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(User)
        if name:
            query = query.where(User.name == name)
        if email:
            query = query.where(User.email == email)
        if role:
            query = query.where(User.role == role)
            
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/exists/username/{username}")
async def user_exists(
    username: str,
    db: AsyncSession = Depends(get_async_session)
) -> bool:
    try:
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalars().first() is not None
    except Exception as e:
        logger.error(f"Error checking user existence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/exists/email/{email}")
async def email_exists(
    email: str,
    db: AsyncSession = Depends(get_async_session)
) -> bool:
    try:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalars().first() is not None
    except Exception as e:
        logger.error(f"Error checking email existence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/login")
async def login_user(
    user_login: User_Login,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(User).where(User.username == user_login.username)
        result = await db.execute(query)
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(user_login.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password")
        return user.user_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    print("\n=== Clean Start ===")
    print(f"App ID: {id(app)}")
    print("Active routes:")
    for route in app.routes:
        print(f"[{route.methods}] {route.path}")