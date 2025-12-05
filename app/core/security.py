from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
import secrets
import re
from app.core.config import settings
from app.core.exceptions import UnauthorizedError

# Context pour le hashing des mots de passe
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


class PasswordValidator:
    """Validateur de mots de passe"""

    @staticmethod
    def validate(password: str) -> tuple[bool, list[str]]:
        """
        Valider un mot de passe selon la politique

        Returns:
            Tuple (is_valid, error_messages)
        """
        errors = []

        if len(password) < settings.password_min_length:
            errors.append(
                f"Le mot de passe doit contenir au moins {settings.password_min_length} caractères"
            )

        if settings.password_require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Le mot de passe doit contenir au moins une majuscule")

        if settings.password_require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Le mot de passe doit contenir au moins une minuscule")

        if settings.password_require_digit and not re.search(r'\d', password):
            errors.append("Le mot de passe doit contenir au moins un chiffre")

        if settings.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Le mot de passe doit contenir au moins un caractère spécial")

        return len(errors) == 0, errors


class PasswordManager:
    """Gestionnaire de mots de passe"""

    @staticmethod
    def hash(password: str) -> str:
        """Hasher un mot de passe"""
        return pwd_context.hash(password)

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """Vérifier un mot de passe"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False

    @staticmethod
    def needs_update(hashed_password: str) -> bool:
        """Vérifier si le hash doit être mis à jour"""
        return pwd_context.needs_update(hashed_password)

    @staticmethod
    def generate_random(length: int = 16) -> str:
        """Générer un mot de passe aléatoire sécurisé"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
        return ''.join(secrets.choice(alphabet) for _ in range(length))


class TokenManager:
    """Gestionnaire de tokens JWT"""

    @staticmethod
    def create_access_token(
            data: Dict[str, Any],
            expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Créer un token d'accès JWT

        Args:
            data: Données à encoder dans le token
            expires_delta: Durée de validité personnalisée

        Returns:
            Token JWT signé
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc).isoformat() + "Z",
            "type": "access"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )

        return encoded_jwt

    @staticmethod
    def create_refresh_token(
            data: Dict[str, Any],
            expires_delta: Optional[timedelta] = None
    ) -> str:
        """Créer un refresh token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=settings.refresh_token_expire_days
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc).isoformat() + "Z",
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Vérifier et décoder un token

        Args:
            token: Token JWT à vérifier
            token_type: Type de token attendu

        Returns:
            Payload décodé

        Raises:
            UnauthorizedError: Si le token est invalide
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )

            # Vérifier le type de token
            if payload.get("type") != token_type:
                raise UnauthorizedError(f"Type de token invalide: attendu {token_type}")

            return payload

        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token expiré")
        except jwt.JWTClaimsError:
            raise UnauthorizedError("Claims du token invalides")
        except JWTError as e:
            raise UnauthorizedError(f"Token invalide: {str(e)}")

    @staticmethod
    def decode_token_unsafe(token: str) -> Optional[Dict[str, Any]]:
        """
        Décoder un token sans vérification (pour inspection)

        Returns:
            Payload ou None si invalide
        """
        try:
            return jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm],
                options={"verify_signature": False}
            )
        except Exception:
            return None


class APIKeyManager:
    """Gestionnaire d'API Keys"""

    @staticmethod
    def verify(api_key: str) -> bool:
        """
        Vérifier une API key

        Args:
            api_key: API key à vérifier

        Returns:
            True si valide
        """
        if not settings.api_key_enabled:
            return True

        if not api_key:
            return False

        return api_key in settings.api_keys

    @staticmethod
    def generate() -> str:
        """Générer une nouvelle API key"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hasher une API key pour stockage"""
        return bcrypt.hash(api_key)

    @staticmethod
    def verify_hashed(api_key: str, hashed: str) -> bool:
        """Vérifier une API key contre son hash"""
        try:
            return bcrypt.verify(api_key, hashed)
        except Exception:
            return False


class SecurityHeaders:
    """Headers de sécurité recommandés"""

    @staticmethod
    def get_default_headers() -> Dict[str, str]:
        """Obtenir les headers de sécurité par défaut"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


# Fonctions utilitaires exportées
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Créer un token d'accès"""
    return TokenManager.create_access_token(data, expires_delta)


def verify_token(token: str) -> dict:
    """Vérifier un token"""
    return TokenManager.verify_token(token)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe"""
    return PasswordManager.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hasher un mot de passe"""
    return PasswordManager.hash(password)


def verify_api_key(api_key: str) -> bool:
    """Vérifier une API key"""
    return APIKeyManager.verify(api_key)


def generate_api_key() -> str:
    """Générer une API key"""
    return APIKeyManager.generate()