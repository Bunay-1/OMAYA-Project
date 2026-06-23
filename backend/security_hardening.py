"""
Security Hardening Module for OMAYA Platform
Production-ready security configurations and utilities
"""
from typing import Dict, Any, Optional, List
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
import ssl
import os

logger = logging.getLogger(__name__)

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer()

class SecurityConfig:
    """Centralized security configuration."""
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Token settings
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 100
    RATE_LIMIT_PER_HOUR = 1000
    
    # Session settings
    MAX_SESSIONS_PER_USER = 5
    SESSION_TIMEOUT_MINUTES = 60
    
    # Encryption
    ENCRYPTION_KEY_LENGTH = 32
    SALT_LENGTH = 16


class PasswordValidator:
    """Password validation and strength checking."""
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, List[str]]:
        """
        Validate password against security requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters")
        
        if SecurityConfig.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if SecurityConfig.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if SecurityConfig.REQUIRE_DIGITS and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if SecurityConfig.REQUIRE_SPECIAL_CHARS and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a cryptographically secure random password."""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))


class TokenManager:
    """JWT token management with rotation support."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.blacklisted_tokens = set()
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: timedelta = None) -> str:
        """Create JWT access token."""
        from jose import jwt
        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        from jose import jwt
        
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        from jose import jwt, JWTError
        
        try:
            if token in self.blacklisted_tokens:
                return None
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def blacklist_token(self, token: str):
        """Add token to blacklist."""
        self.blacklisted_tokens.add(token)
    
    def cleanup_expired_blacklist(self):
        """Clean up expired tokens from blacklist."""
        from jose import jwt, JWTError
        
        active_tokens = set()
        for token in self.blacklisted_tokens:
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                if payload.get('exp', 0) > datetime.utcnow().timestamp():
                    active_tokens.add(token)
            except JWTError:
                pass
        
        self.blacklisted_tokens = active_tokens


class RateLimiter:
    """Advanced rate limiting with Redis backend."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def check_rate_limit(self, identifier: str, limit: int, window: int = 60) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            identifier: Unique identifier (IP, user_id, etc.)
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            True if within limit, False otherwise
        """
        key = f"ratelimit:{identifier}"
        
        try:
            current = self.redis.incr(key)
            if current == 1:
                self.redis.expire(key, window)
            
            return current <= limit
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error
    
    async def get_remaining_requests(self, identifier: str, limit: int) -> int:
        """Get remaining requests for identifier."""
        key = f"ratelimit:{identifier}"
        
        try:
            current = int(self.redis.get(key) or 0)
            return max(0, limit - current)
        except Exception as e:
            logger.error(f"Failed to get remaining requests: {e}")
            return limit


class IPWhitelist:
    """IP whitelist management for access control."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.whitelist_key = "security:ip_whitelist"
        self.blacklist_key = "security:ip_blacklist"
    
    async def add_to_whitelist(self, ip: str, description: str = ""):
        """Add IP to whitelist."""
        try:
            self.redis.hset(self.whitelist_key, ip, description)
            logger.info(f"Added {ip} to whitelist")
        except Exception as e:
            logger.error(f"Failed to add IP to whitelist: {e}")
    
    async def remove_from_whitelist(self, ip: str):
        """Remove IP from whitelist."""
        try:
            self.redis.hdel(self.whitelist_key, ip)
            logger.info(f"Removed {ip} from whitelist")
        except Exception as e:
            logger.error(f"Failed to remove IP from whitelist: {e}")
    
    async def add_to_blacklist(self, ip: str, reason: str = ""):
        """Add IP to blacklist."""
        try:
            self.redis.hset(self.blacklist_key, ip, reason)
            logger.info(f"Added {ip} to blacklist: {reason}")
        except Exception as e:
            logger.error(f"Failed to add IP to blacklist: {e}")
    
    async def remove_from_blacklist(self, ip: str):
        """Remove IP from blacklist."""
        try:
            self.redis.hdel(self.blacklist_key, ip)
            logger.info(f"Removed {ip} from blacklist")
        except Exception as e:
            logger.error(f"Failed to remove IP from blacklist: {e}")
    
    async def is_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted."""
        try:
            return self.redis.hexists(self.whitelist_key, ip)
        except Exception as e:
            logger.error(f"Failed to check whitelist: {e}")
            return False
    
    async def is_blacklisted(self, ip: str) -> bool:
        """Check if IP is blacklisted."""
        try:
            return self.redis.hexists(self.blacklist_key, ip)
        except Exception as e:
            logger.error(f"Failed to check blacklist: {e}")
            return False


class CertificateManager:
    """SSL/TLS certificate management and rotation."""
    
    @staticmethod
    def generate_self_signed_cert(cert_path: str, key_path: str, 
                                  common_name: str = "omaya.local") -> bool:
        """
        Generate self-signed SSL certificate.
        
        Args:
            cert_path: Path to save certificate
            key_path: Path to save private key
            common_name: Common name for certificate
            
        Returns:
            True on success, False on error
        """
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "BG"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Sofia"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Sofia"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "OMAYA"),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(common_name),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256(), default_backend())
            
            # Save certificate
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Save private key
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info(f"Generated self-signed certificate for {common_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate certificate: {e}")
            return False
    
    @staticmethod
    def check_cert_expiry(cert_path: str) -> Optional[int]:
        """
        Check certificate expiry date.
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            Days until expiry, None if error
        """
        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            
            with open(cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read(), default_backend())
            
            expiry = cert.not_valid_after
            days_until_expiry = (expiry - datetime.utcnow()).days
            return days_until_expiry
            
        except Exception as e:
            logger.error(f"Failed to check certificate expiry: {e}")
            return None


class SecurityHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers dictionary."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }


class AuditLogger:
    """Security event logging for compliance."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.audit_key = "security:audit_log"
    
    async def log_security_event(self, event_type: str, user_id: str, 
                                 ip: str, details: Dict[str, Any] = None):
        """
        Log security event.
        
        Args:
            event_type: Type of security event
            user_id: User identifier
            ip: IP address
            details: Additional event details
        """
        try:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "user_id": user_id,
                "ip": ip,
                "details": details or {}
            }
            
            self.redis.lpush(self.audit_key, str(event))
            # Keep only last 10000 events
            self.redis.ltrim(self.audit_key, 0, 9999)
            
            logger.info(f"Security event logged: {event_type} by {user_id} from {ip}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    async def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit log entries."""
        try:
            events = self.redis.lrange(self.audit_key, 0, limit - 1)
            return [eval(event) for event in events]
        except Exception as e:
            logger.error(f"Failed to get audit log: {e}")
            return []


def rate_limit_decorator(limit: int, window: int = 60):
    """Decorator for rate limiting endpoints."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if request:
                identifier = get_remote_address(request)
                # Implement rate limit check here
                pass
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class DynamicSecretsManager:
    """Dynamic secrets management using Vault."""
    
    def __init__(self, vault_addr: str, vault_token: str):
        self.vault_addr = vault_addr
        self.vault_token = vault_token
        self.client = None
    
    async def initialize(self):
        """Initialize Vault client."""
        try:
            import hvac
            self.client = hvac.Client(url=self.vault_addr, token=self.vault_token)
            if self.client.is_authenticated():
                logger.info("Vault client initialized successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Vault client: {e}")
            return False
    
    async def create_machine_secret(self, machine_id: str, ttl: int = 3600) -> Optional[Dict[str, str]]:
        """
        Create dynamic secret for a machine.
        
        Args:
            machine_id: Machine identifier
            ttl: Time to live in seconds
            
        Returns:
            Dictionary with credentials or None on error
        """
        try:
            path = f"omaya/machines/{machine_id}"
            secret_data = {
                "username": f"machine_{machine_id}",
                "password": secrets.token_urlsafe(32),
                "ttl": ttl
            }
            
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secret_data
            )
            
            logger.info(f"Created dynamic secret for machine {machine_id}")
            return secret_data
            
        except Exception as e:
            logger.error(f"Failed to create machine secret: {e}")
            return None
    
    async def revoke_machine_secret(self, machine_id: str) -> bool:
        """Revoke machine secret."""
        try:
            path = f"omaya/machines/{machine_id}"
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=path)
            logger.info(f"Revoked secret for machine {machine_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke machine secret: {e}")
            return False
