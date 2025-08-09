from passlib.context import CryptContext
from database import User, SessionLocal
from sqlalchemy.orm import Session

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    print(f"🔐 Hashing password... (length: {len(password)})")
    hashed = pwd_context.hash(password)
    print(f"🔐 Password hashed successfully! Hash starts with: {hashed[:20]}...")
    return hashed

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    print(f"🔍 Verifying password... (checking against hash starting with: {hashed_password[:20]}...)")
    is_valid = pwd_context.verify(plain_password, hashed_password)
    print(f"🔍 Password verification result: {is_valid}")
    return is_valid

def create_user(db: Session, username: str, email: str, password: str, is_admin: bool = False) -> User:
    """Create a new user with hashed password"""
    print(f"👤 Creating user: {username} ({email})")
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        print(f"❌ User already exists! Username: {existing_user.username}, Email: {existing_user.email}")
        raise ValueError("User with this username or email already exists")
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Create user object
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_admin=is_admin
    )
    
    # Save to database
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"✅ User created successfully! ID: {user.id}, Admin: {user.is_admin}")
    return user

def get_user_by_username(db: Session, username: str) -> User | None:
    """Get user by username"""
    print(f"🔍 Looking up user by username: {username}")
    user = db.query(User).filter(User.username == username).first()
    if user:
        print(f"✅ User found! ID: {user.id}, Email: {user.email}, Admin: {user.is_admin}")
    else:
        print(f"❌ User not found: {username}")
    return user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Authenticate user with username and password"""
    print(f"🔐 Attempting to authenticate user: {username}")
    
    # Get user from database
    user = get_user_by_username(db, username)
    if not user:
        print(f"❌ Authentication failed: user not found")
        return None
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        print(f"❌ Authentication failed: incorrect password")
        return None
    
    print(f"✅ Authentication successful for user: {username}")
    return user