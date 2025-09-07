"""
Esquemas Pydantic para Usuarios
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole



class UserCreate(BaseModel):
    """Esquema para crear usuario"""
    username: str
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.MESERO
    password: str


class UserUpdate(BaseModel):
    """Esquema para actualizar usuario"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    """Esquema para login de usuario"""
    username: str
    password: str


class UserResponse(BaseModel):
    """Esquema de respuesta para usuario"""
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Esquema para token de autenticación"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Esquema para datos del token"""
    username: Optional[str] = None 