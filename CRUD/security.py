from dataclasses import dataclass
from enum import Enum
import re
from typing import Optional
import hashlib
import time
from datetime import datetime, timedelta

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

@dataclass
class Session:
    user_id: int
    role: UserRole
    expires: datetime
    
class SecurityManager:
    def __init__(self):
        self._failed_attempts = {}
        self._sessions = {}
        self._lockout_duration = 300  # 5 minutes
        self._max_attempts = 3
        
    def validate_password(self, password: str) -> bool:
        """Check password meets security requirements"""
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        return True

    def check_rate_limit(self, username: str) -> bool:
        """Check if user is rate limited"""
        if username in self._failed_attempts:
            attempts, last_attempt = self._failed_attempts[username]
            if attempts >= self._max_attempts:
                if time.time() - last_attempt < self._lockout_duration:
                    return False
                self._failed_attempts[username] = (0, time.time())
        return True

    def create_session(self, user_id: int, role: UserRole) -> str:
        """Create new session"""
        session_id = hashlib.sha256(f"{user_id}{time.time()}".encode()).hexdigest()
        self._sessions[session_id] = Session(
            user_id=user_id,
            role=role,
            expires=datetime.now() + timedelta(hours=1)
        )
        return session_id

    def validate_session(self, session_id: str) -> Optional[Session]:
        """Validate session exists and not expired"""
        session = self._sessions.get(session_id)
        if not session:
            return None
        if datetime.now() > session.expires:
            del self._sessions[session_id]
            return None
        return session

    def record_failed_attempt(self, username: str):
        """Record failed login attempt"""
        attempts, _ = self._failed_attempts.get(username, (0, 0))
        self._failed_attempts[username] = (attempts + 1, time.time())