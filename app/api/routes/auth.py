
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import UserModel
from app.schemas.user import UserCreate, UserResponse
from app.core.logging_config import logger

from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import TokenResponse
from app.core.security import verify_password, create_access_token,hash_password

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    # Normalize email before checking for duplicates.
    email = str(user_data.email).lower()

    # Check whether the email is already registered.
    existing_user = db.scalar(
        select(UserModel).where(
            UserModel.email == email
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    # Hash the password before storing it.
    hashed_password = hash_password(user_data.password)

    # Create a new SQLAlchemy user object.
    new_user = UserModel(
        email=email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True,
        role="employee"
    )

    # Save the user in the database.
    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    logger.info(
        "User registered successfully: user_id=%s",
        new_user.id
    )

    return new_user



@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Normalize the email address.
    email = form_data.username.lower().strip()

    # Find the user in the database.
    user = db.scalar(
        select(UserModel).where(
            UserModel.email == email
        )
    )

    # Reject unknown users and incorrect passwords.
    if user is None:
        logger.warning("Failed login attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):
        logger.warning("Failed login attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check whether the account is active.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive"
        )

    # Generate a JWT access token.
    access_token = create_access_token(user.id)

    logger.info(
        "User logged in successfully: user_id=%s",
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
