from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"  # Same as your apps use!
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token"""
    print(f"🎫 Creating JWT token for data: {data}")
    
    # Copy the data we want to put in the token
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration to token data
    to_encode.update({"exp": expire})
    
    print(f"🎫 Token will expire at: {expire}")
    print(f"🎫 Token payload: {to_encode}")
    
    # Create the JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    print(f"🎫 JWT token created! Length: {len(encoded_jwt)}")
    print(f"🎫 Token starts with: {encoded_jwt[:50]}...")
    
    return encoded_jwt

def verify_token(token: str):
    """Verify and decode a JWT token"""
    print(f"🔍 Verifying JWT token...")
    print(f"🔍 Token starts with: {token[:50]}...")
    
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ Token is valid! Payload: {payload}")
        
        # Extract username from token
        username = payload.get("sub")  # "sub" is standard for "subject" (user)
        if username is None:
            print("❌ Token is missing 'sub' (username)")
            return None
            
        print(f"✅ Token belongs to user: {username}")
        return payload
        
    except JWTError as e:
        print(f"❌ Token verification failed: {str(e)}")
        return None

def create_token_for_user(username: str, is_admin: bool = False):
    """Create a token for a specific user"""
    print(f"🎫 Creating token for user: {username} (admin: {is_admin})")
    
    # Standard JWT payload
    # Standard JWT payload with issuer for Kong
    token_data = {
        "sub": username,  # "subject" - who this token is for
        "admin": is_admin,  # Custom field for authorization
        "iat": datetime.utcnow(),  # "issued at" time
        "iss": "fastapi-jwt-issuer",  # "issuer" - required by Kong JWT plugin
    }
    
    return create_access_token(token_data)