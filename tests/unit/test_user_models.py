"""
Tests unitarios para modelos de usuario
"""
import pytest
from decimal import Decimal


class TestUserRole:
    """Tests para el enum UserRole"""
    
    def test_user_role_values(self):
        """Verificar valores de roles de usuario"""
        from app.models.user import UserRole
        
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MESERO.value == "mesero"
        assert UserRole.COCINA.value == "cocina"
        assert UserRole.ALMACEN.value == "almacen"
    
    def test_user_role_count(self):
        """Verificar cantidad de roles"""
        from app.models.user import UserRole
        
        roles = list(UserRole)
        assert len(roles) == 4


class TestUserModel:
    """Tests para el modelo User"""
    
    def test_user_creation(self):
        """Test crear usuario"""
        from app.models.user import User, UserRole
        
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            role=UserRole.MESERO,
            is_active=True
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == UserRole.MESERO
        assert user.is_active == True
    
    def test_user_default_values(self):
        """Verificar valores por defecto"""
        from app.models.user import User
        
        user = User(
            username="defaultuser",
            email="default@example.com"
        )
        
        assert user.is_active == True
        assert user.is_verified == False
        assert user.is_superuser == False
    
    def test_user_hashed_password(self):
        """Test que la contraseña está hasheada"""
        from app.models.user import User
        
        user = User(
            username="passtest",
            email="pass@example.com",
            hashed_password="hashed_secret"
        )
        
        assert user.hashed_password == "hashed_secret"
    
    def test_user_repr(self):
        """Test representación string"""
        from app.models.user import User
        
        user = User(username="reprtest", email="repr@example.com")
        result = repr(user)
        
        assert "reprtest" in result


class TestPermisoModel:
    """Tests para el modelo Permiso"""
    
    def test_permiso_creation(self):
        """Test crear permiso"""
        from app.models.permiso import Permiso
        
        permiso = Permiso(
            nombre="crear_pedido",
            descripcion="Permite crear pedidos"
        )
        
        assert permiso.nombre == "crear_pedido"
        assert permiso.descripcion == "Permite crear pedidos"
    
    def test_permiso_default_values(self):
        """Verificar valores por defecto"""
        from app.models.permiso import Permiso
        
        permiso = Permiso(nombre="test_permiso")
        
        assert permiso.activo == True
