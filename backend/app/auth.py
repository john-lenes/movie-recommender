"""
Autenticação simples com tokens
Para produção, usar JWT com secret key e expiração
"""
from typing import Optional
import secrets
from datetime import datetime, timedelta


class TokenManager:
    def __init__(self):
        self.tokens: dict[str, tuple[int, datetime]] = {}  # token -> (user_id, expiry)
        self.token_expiry_hours = 24 * 7  # 7 dias
    
    def create_token(self, user_id: int) -> str:
        """Cria token para usuário"""
        token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=self.token_expiry_hours)
        self.tokens[token] = (user_id, expiry)
        return token
    
    def validate_token(self, token: str) -> Optional[int]:
        """Valida token e retorna user_id"""
        if token not in self.tokens:
            return None
        
        user_id, expiry = self.tokens[token]
        
        # Verificar expiração
        if datetime.now() > expiry:
            del self.tokens[token]
            return None
        
        return user_id
    
    def revoke_token(self, token: str):
        """Revoga token (logout)"""
        if token in self.tokens:
            del self.tokens[token]
    
    def cleanup_expired(self):
        """Remove tokens expirados"""
        now = datetime.now()
        expired = [token for token, (_, expiry) in self.tokens.items() if now > expiry]
        for token in expired:
            del self.tokens[token]


# Singleton
_token_manager = TokenManager()

def get_token_manager() -> TokenManager:
    return _token_manager
