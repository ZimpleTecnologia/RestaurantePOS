"""
Configuración principal del sistema POS
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configuraciones del sistema POS"""
    
    # Database
    database_url: str = "sqlite:///./restaurante_pos.db"
    database_test_url: str = "sqlite:///./restaurante_pos_test.db"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Session Timeout
    session_timeout_minutes: int = 30  # Timeout por inactividad
    session_warning_minutes: int = 2   # Minutos antes del timeout para mostrar advertencia
    session_check_interval: int = 60   # Segundos entre verificaciones de sesión
    
    # Application
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # File Upload
    upload_dir: str = "uploads"
    max_file_size: int = 10485760  # 10MB
    
    # Email (for future use)
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()

# Crear directorio de uploads si no existe
os.makedirs(settings.upload_dir, exist_ok=True) 