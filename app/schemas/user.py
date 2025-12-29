"""
Esquemas Pydantic para Usuarios
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole



class UserCreate(BaseModel):
    """Esquema para crear usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=3, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.MESERO
    password: str = Field(..., min_length=6)
    is_active: Optional[bool] = Field(True, description="Estado activo del usuario")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre de usuario no puede estar vacío')
        return v.strip().lower()
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre completo no puede estar vacío')
        return v.strip()
    
    @field_validator('role', mode='before')
    @classmethod
    def validate_role(cls, v):
        """Valida y convierte el rol a enum"""
        if isinstance(v, str):
            # Intentar convertir string a enum
            try:
                return UserRole(v.upper())
            except ValueError:
                raise ValueError(f'Rol inválido: {v}. Los roles válidos son: {", ".join([r.value for r in UserRole])}')
        return v


class UserUpdate(BaseModel):
    """Esquema para actualizar usuario"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=3, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, description="Nueva contraseña (opcional, mínimo 6 caracteres si se proporciona)")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Valida que la contraseña tenga al menos 6 caracteres si se proporciona"""
        if v is not None and v != '' and len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v if v and v.strip() else None
    
    @field_validator('role', mode='before')
    @classmethod
    def validate_role(cls, v):
        """Valida y convierte el rol a enum"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return UserRole(v.upper())
            except ValueError:
                raise ValueError(f'Rol inválido: {v}. Los roles válidos son: {", ".join([r.value for r in UserRole])}')
        return v


class UserPasswordReset(BaseModel):
    """Esquema para resetear contraseña"""
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v


class UserLogin(BaseModel):
    """Esquema para login de usuario"""
    username: str
    password: str


class PermisoSimpleInUser(BaseModel):
    """Schema simple de permiso para incluir en usuario"""
    id: int
    codigo: str
    nombre: str
    modulo: str
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Esquema de respuesta para usuario"""
    id: int
    username: str
    email: EmailStr
    full_name: str
    telefono: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    permisos: List[PermisoSimpleInUser] = []
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema para lista de usuarios"""
    usuarios: List[UserResponse]
    total: int
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Esquema para token de autenticación"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Esquema para datos del token"""
    username: Optional[str] = None 