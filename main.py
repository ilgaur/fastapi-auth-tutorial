from fastapi import FastAPI, Depends, HTTPException, Header
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from jwt_utils import create_token_for_user, verify_token

# Import our database and auth components
from database import create_tables, get_db, User
from auth_utils import create_user, get_user_by_username, authenticate_user

# Request/Response models
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    is_admin: bool

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 App starting up...")
    print("📊 Initializing database...")
    create_tables()
    print("✅ Startup complete!")
    yield
    # Shutdown
    print("🛑 App shutting down...")

# Create our FastAPI app with lifespan - MOVE THIS TO THE TOP
app = FastAPI(title="Auth Tutorial", version="1.0.0", lifespan=lifespan)

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Dependency to get current user from JWT token"""
    print(f"🔒 Checking authorization header...")
    
    # Check if Authorization header exists
    if not authorization:
        print("❌ No Authorization header found")
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Check if it starts with "Bearer "
    if not authorization.startswith("Bearer "):
        print("❌ Authorization header must start with 'Bearer '")
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    # Extract the token
    token = authorization.split(" ")[1]
    print(f"🔒 Extracted token: {token[:50]}...")
    
    # Verify the token
    payload = verify_token(token)
    if not payload:
        print("❌ Token verification failed")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get username from token
    username = payload.get("sub")
    if not username:
        print("❌ Token missing username")
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Get user from database
    user = get_user_by_username(db, username)
    if not user:
        print(f"❌ User {username} not found in database")
        raise HTTPException(status_code=401, detail="User not found")
    
    print(f"✅ User authenticated: {username}")
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """Dependency to ensure current user is an admin"""
    print(f"🔐 Checking admin privileges for user: {current_user.username}")
    
    if not current_user.is_admin:
        print(f"❌ User {current_user.username} is not an admin")
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    print(f"✅ Admin access granted for user: {current_user.username}")
    return current_user

@app.post("/signup", response_model=dict)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Sign up a new user"""
    print(f"📝 SIGNUP attempt for user: {request.username}")
    
    try:
        user = create_user(db, request.username, request.email, request.password)
        print(f"✅ SIGNUP successful for user: {request.username}")
        
        return {
            "message": "Account created successfully",
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }
    except ValueError as e:
        print(f"❌ SIGNUP failed for user: {request.username} - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint - returns JWT token"""
    print(f"🚪 LOGIN attempt for user: {request.username}")
    
    # Authenticate user
    user = authenticate_user(db, request.username, request.password)
    if not user:
        print(f"❌ LOGIN failed for user: {request.username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create JWT token
    access_token = create_token_for_user(user.username, user.is_admin)
    
    print(f"✅ LOGIN successful for user: {request.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "is_admin": user.is_admin,
        "message": "Login successful!"
    }

@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Protected endpoint - returns current user info"""
    print(f"👤 /me endpoint called by user: {current_user.username}")
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "message": f"Hello {current_user.username}! This is your protected profile."
    }

@app.get("/admin")
def admin_only(current_user: User = Depends(get_current_admin_user)):
    """Admin-only endpoint"""
    print(f"👑 /admin endpoint called by admin: {current_user.username}")
    
    return {
        "message": f"Welcome to the admin panel, {current_user.username}!",
        "admin_user": current_user.username,
        "secret_admin_data": "Only admins can see this!",
        "server_status": "All systems operational"
    }

@app.get("/health")
def health_check():
    """Simple health check to verify our API is running"""
    current_time = datetime.now().isoformat()
    print(f"🏥 Health check called at {current_time}")
    
    return {
        "status": "healthy",
        "timestamp": current_time,
        "message": "FastAPI Auth Tutorial is running!",
        "database": "PostgreSQL connected"
    }

@app.get("/db-test")
def test_database():
    """Test our database connection"""
    print("🧪 Testing database connection...")
    
    try:
        # Get a database session
        db = next(get_db())
        
        # Try a simple query using text() for raw SQL
        result = db.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        
        print(f"✅ Database connected! Version: {version}")
        
        return {
            "status": "database_connected",
            "postgresql_version": version,
            "message": "Database connection successful!"
        }
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return {
            "status": "database_error",
            "error": str(e)
        }

if __name__ == "__main__":
    print("🚀 Starting FastAPI Auth Tutorial...")
    print("📍 Health endpoint: http://localhost:8000/health")
    print("📖 Docs: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)