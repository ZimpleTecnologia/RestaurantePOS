"""
Tests unitarios para schemas de validación (Pydantic)
"""
import pytest
from decimal import Decimal
from datetime import date, datetime


class TestUserSchemas:
    """Tests para schemas de usuario"""
    
    def test_user_create_valid(self):
        """Test crear usuario con datos válidos"""
        from app.schemas.user import UserCreate
        
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "full_name": "New User",
            "password": "securepass123",
            "role": "mesero"
        }
        
        user = UserCreate(**user_data)
        
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.password == "securepass123"
    
    def test_user_create_invalid_email(self):
        """Test crear usuario con email inválido"""
        from app.schemas.user import UserCreate
        from pydantic import ValidationError
        
        user_data = {
            "username": "baduser",
            "email": "not-an-email",
            "password": "pass123"
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)
    
    def test_user_create_short_password(self):
        """Test crear usuario con contraseña corta"""
        from app.schemas.user import UserCreate
        from pydantic import ValidationError
        
        user_data = {
            "username": "shortpass",
            "email": "short@example.com",
            "password": "123"
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)


class TestOrderSchemas:
    """Tests para schemas de orden"""
    
    def test_order_create_valid(self):
        """Test crear orden con datos válidos"""
        from app.schemas.order import OrderCreate
        
        order_data = {
            "order_number": "ORD-TEST-001",
            "waiter_id": 1,
            "table_id": 1,
            "order_type": "mesa"
        }
        
        order = OrderCreate(**order_data)
        
        assert order.order_number == "ORD-TEST-001"
        assert order.waiter_id == 1
    
    def test_order_item_create_valid(self):
        """Test crear item de orden"""
        from app.schemas.order import OrderItemCreate
        
        item_data = {
            "product_id": 1,
            "quantity": 2,
            "unit_price": 10.50
        }
        
        item = OrderItemCreate(**item_data)
        
        assert item.quantity == 2
        assert item.unit_price == Decimal('10.50')


class TestProductSchemas:
    """Tests para schemas de producto"""
    
    def test_product_create_valid(self):
        """Test crear producto con datos válidos"""
        from app.schemas.product import ProductCreate
        
        product_data = {
            "name": "Test Product",
            "price": 25.99,
            "category_id": 1,
            "sku": "TEST-001"
        }
        
        product = ProductCreate(**product_data)
        
        assert product.name == "Test Product"
        assert product.price == Decimal('25.99')
    
    def test_product_create_negative_price(self):
        """Test crear producto con precio negativo"""
        from app.schemas.product import ProductCreate
        from pydantic import ValidationError
        
        product_data = {
            "name": "Bad Product",
            "price": -10.00,
            "sku": "BAD-001"
        }
        
        with pytest.raises(ValidationError):
            ProductCreate(**product_data)


class TestMesaSchemas:
    """Tests para schemas de mesa"""
    
    def test_mesa_create_valid(self):
        """Test crear mesa con datos válidos"""
        from app.schemas.mesa import MesaCreate
        
        mesa_data = {
            "nombre": "Mesa 1",
            "numero": 1,
            "capacidad": 4
        }
        
        mesa = MesaCreate(**mesa_data)
        
        assert mesa.nombre == "Mesa 1"
        assert mesa.numero == 1
        assert mesa.capacidad == 4
    
    def test_mesa_create_zero_numero(self):
        """Test crear mesa con número cero"""
        from app.schemas.mesa import MesaCreate
        from pydantic import ValidationError
        
        mesa_data = {
            "nombre": "Mesa Cero",
            "numero": 0,
            "capacidad": 4
        }
        
        with pytest.raises(ValidationError):
            MesaCreate(**mesa_data)
    
    def test_mesa_create_negative_capacidad(self):
        """Test crear mesa con capacidad negativa"""
        from app.schemas.mesa import MesaCreate
        from pydantic import ValidationError
        
        mesa_data = {
            "nombre": "Mesa Negativa",
            "numero": 1,
            "capacidad": -2
        }
        
        with pytest.raises(ValidationError):
            MesaCreate(**mesa_data)


class TestLocationSchemas:
    """Tests para schemas de ubicación/mesa"""
    
    def test_table_create_valid(self):
        """Test crear mesa con schema TableCreate"""
        from app.schemas.location import TableCreate
        from app.models.location import TableStatus
        
        table_data = {
            "table_number": "T1",
            "name": "Mesa Principal",
            "capacity": 6,
            "status": TableStatus.AVAILABLE
        }
        
        table = TableCreate(**table_data)
        
        assert table.table_number == "T1"
        assert table.capacity == 6
    
    def test_table_status_values(self):
        """Verificar valores de TableStatus"""
        from app.models.location import TableStatus
        
        assert TableStatus.AVAILABLE.value == "disponible"
        assert TableStatus.OCCUPIED.value == "ocupada"
        assert TableStatus.RESERVED.value == "reservada"
        assert TableStatus.CLEANING.value == "limpieza"
        assert TableStatus.OUT_OF_SERVICE.value == "fuera_de_servicio"
