"""
Configuración de producción para el Sistema POS
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class ProductionSettings(BaseSettings):
    """Configuraciones de producción del sistema POS"""
    
    # Database - Configurar con variables de entorno
    database_url: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/sistema_pos")
    
    # Security - IMPORTANTE: Cambiar en producción
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Application
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # File Upload
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    
    # CORS - Configurar dominios permitidos
    allowed_origins: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # Email (para futuras funcionalidades)
    smtp_server: Optional[str] = os.getenv("SMTP_SERVER")
    smtp_port: Optional[int] = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else None
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración de producción
production_settings = ProductionSettings()

# Crear directorio de uploads si no existe
os.makedirs(production_settings.upload_dir, exist_ok=True)
os.makedirs("logs", exist_ok=True)
