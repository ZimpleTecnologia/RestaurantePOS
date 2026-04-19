"""
Configuración de pytest para tests unitarios
"""
import os
import sys
import pytest

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar base de datos de test
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_restaurante_pos.db")


@pytest.fixture(scope="session")
def test_db():
    """Fixture para crear base de datos de test"""
    from app.database import Base, engine
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Limpiar después de los tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Fixture para crear sesión de base de datos"""
    from app.database import SessionLocal
    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """Fixture para crear cliente de test"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    return TestClient(app)
