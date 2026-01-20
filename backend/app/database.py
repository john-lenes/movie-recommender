"""
Database simples em memória para usuários
Para produção, substituir por SQLite/PostgreSQL
"""
from typing import Dict, List, Optional
from datetime import datetime
from passlib.context import CryptContext

# Configuração segura de hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User:
    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        password_hash: str,
        created_at: datetime = None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now()
        self.liked_movies: List[int] = []
        self.disliked_movies: List[int] = []
        self.ratings: Dict[int, int] = {}  # movie_id -> rating (1-5)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "liked_movies": self.liked_movies,
            "disliked_movies": self.disliked_movies,
            "ratings": self.ratings,
        }


class InMemoryDatabase:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.next_id = 1
        self.username_index: Dict[str, int] = {}
        self.email_index: Dict[str, int] = {}
    
    def _hash_password(self, password: str) -> str:
        """Hash seguro de senha usando bcrypt"""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha corresponde ao hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, username: str, email: str, password: str) -> Optional[User]:
        """Cria novo usuário"""
        # Validações
        if username in self.username_index:
            return None
        if email in self.email_index:
            return None
        
        user_id = self.next_id
        self.next_id += 1
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=self._hash_password(password)
        )
        
        self.users[user_id] = user
        self.username_index[username] = user_id
        self.email_index[email] = user_id
        
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        user_id = self.username_index.get(username)
        return self.users.get(user_id) if user_id else None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        user_id = self.email_index.get(email)
        return self.users.get(user_id) if user_id else None
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Autentica usuário"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        if not self._verify_password(password, user.password_hash):
            return None
        
        return user
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Atualiza dados do usuário"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        if 'username' in kwargs:
            # Atualizar índice
            old_username = user.username
            new_username = kwargs['username']
            if new_username != old_username:
                if new_username in self.username_index:
                    return None
                del self.username_index[old_username]
                self.username_index[new_username] = user_id
                user.username = new_username
        
        if 'email' in kwargs:
            old_email = user.email
            new_email = kwargs['email']
            if new_email != old_email:
                if new_email in self.email_index:
                    return None
                del self.email_index[old_email]
                self.email_index[new_email] = user_id
                user.email = new_email
        
        if 'password' in kwargs:
            user.password_hash = self._hash_password(kwargs['password'])
        
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Deleta usuário"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        del self.username_index[user.username]
        del self.email_index[user.email]
        del self.users[user_id]
        return True
    
    def add_like(self, user_id: int, movie_id: int):
        user = self.get_user_by_id(user_id)
        if user:
            if movie_id in user.disliked_movies:
                user.disliked_movies.remove(movie_id)
            if movie_id not in user.liked_movies:
                user.liked_movies.append(movie_id)
    
    def add_dislike(self, user_id: int, movie_id: int):
        user = self.get_user_by_id(user_id)
        if user:
            if movie_id in user.liked_movies:
                user.liked_movies.remove(movie_id)
            if movie_id not in user.disliked_movies:
                user.disliked_movies.append(movie_id)
    
    def add_rating(self, user_id: int, movie_id: int, rating: int):
        user = self.get_user_by_id(user_id)
        if user and 1 <= rating <= 5:
            user.ratings[movie_id] = rating
    
    def remove_feedback(self, user_id: int, movie_id: int):
        user = self.get_user_by_id(user_id)
        if user:
            if movie_id in user.liked_movies:
                user.liked_movies.remove(movie_id)
            if movie_id in user.disliked_movies:
                user.disliked_movies.remove(movie_id)
            if movie_id in user.ratings:
                del user.ratings[movie_id]


# Singleton
_db = InMemoryDatabase()

def get_db() -> InMemoryDatabase:
    return _db
