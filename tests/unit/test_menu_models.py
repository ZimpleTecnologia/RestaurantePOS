"""
Tests unitarios para modelos de menú del restaurante
"""
import pytest
from decimal import Decimal
from datetime import date


class TestMenuDiaModel:
    """Tests para el modelo MenuDia"""
    
    def test_menu_dia_creation(self):
        """Test crear menú del día"""
        from app.models.restaurant_menu import MenuDia
        
        menu = MenuDia(
            fecha=date(2024, 1, 15),
            nombre="Menú del Día",
            precio=Decimal('12.50'),
            estado="ACTIVE"
        )
        
        assert menu.fecha == date(2024, 1, 15)
        assert menu.nombre == "Menú del Día"
        assert menu.precio == Decimal('12.50')
        assert menu.estado == "ACTIVE"
    
    def test_menu_dia_default_values(self):
        """Verificar valores por defecto"""
        from app.models.restaurant_menu import MenuDia
        
        menu = MenuDia(
            fecha=date(2024, 1, 16),
            nombre="Test Menu",
            precio=Decimal('10.00')
        )
        
        assert menu.estado == "ACTIVE"
        assert menu.activo == True


class TestPlatoRestauranteModel:
    """Tests para el modelo PlatoRestaurante"""
    
    def test_plato_creation(self):
        """Test crear plato"""
        from app.models.restaurant_menu import PlatoRestaurante
        
        plato = PlatoRestaurante(
            nombre="Pollo a la Plancha",
            descripcion="Pollo fresco a la plancha",
            precio=Decimal('15.00'),
            tipo="Plato_Fijo",
            activo=True
        )
        
        assert plato.nombre == "Pollo a la Plancha"
        assert plato.precio == Decimal('15.00')
        assert plato.tipo == "Plato_Fijo"
        assert plato.activo == True
    
    def test_plato_tipo_values(self):
        """Verificar valores de tipo"""
        from app.models.restaurant_menu import PlatoRestaurante
        
        # Tipos válidos
        assert PlatoRestaurante.tipo in ["Menu_Dia", "Plato_Fijo", "Acompanamiento_Fijo"]


class TestCategoriaMenuRestauranteModel:
    """Tests para el modelo CategoriaMenuRestaurante"""
    
    def test_categoria_creation(self):
        """Test crear categoría"""
        from app.models.restaurant_menu import CategoriaMenuRestaurante
        
        categoria = CategoriaMenuRestaurante(
            nombre="Proteínas",
            descripcion="Opciones de proteína",
            orden=1,
            is_active=True
        )
        
        assert categoria.nombre == "Proteínas"
        assert categoria.orden == 1
        assert categoria.is_active == True
    
    def test_categoria_default_values(self):
        """Verificar valores por defecto"""
        from app.models.restaurant_menu import CategoriaMenuRestaurante
        
        categoria = CategoriaMenuRestaurante(nombre="Test")
        
        assert categoria.is_active == True
        assert categoria.orden == 0


class TestMenuCategoriaPlatoModel:
    """Tests para el modelo MenuCategoriaPlato"""
    
    def test_menu_categoria_plato_creation(self):
        """Test crear asociación menú-categoría-plato"""
        from app.models.restaurant_menu import MenuCategoriaPlato
        
        assoc = MenuCategoriaPlato(
            menu_dia_id=1,
            categoria_id=1,
            plato_id=1,
            activo=True
        )
        
        assert assoc.menu_dia_id == 1
        assert assoc.categoria_id == 1
        assert assoc.plato_id == 1
        assert assoc.activo == True


class TestMenuSchemas:
    """Tests para schemas de menú"""
    
    def test_categoria_menu_create_valid(self):
        """Test crear categoría con schema válido"""
        from app.schemas.restaurant_menu import CategoriaMenuCreate
        
        data = {
            "nombre": "Bebidas",
            "descripcion": "Bebidas del menú",
            "orden": 3
        }
        
        categoria = CategoriaMenuCreate(**data)
        
        assert categoria.nombre == "Bebidas"
        assert categoria.orden == 3
    
    def test_categoria_menu_create_minimal(self):
        """Test crear categoría con datos mínimos"""
        from app.schemas.restaurant_menu import CategoriaMenuCreate
        
        data = {"nombre": "Postres"}
        
        categoria = CategoriaMenuCreate(**data)
        
        assert categoria.nombre == "Postres"
        assert categoria.is_active == True
        assert categoria.orden == 0
    
    def test_plato_restaurante_create_valid(self):
        """Test crear plato con schema válido"""
        from app.schemas.restaurant_menu import PlatoRestauranteCreate
        
        data = {
            "nombre": "Ensalada Caesar",
            "descripcion": "Ensalada con aderezo cesar",
            "precio": 8.50,
            "tipo": "Plato_Fijo"
        }
        
        plato = PlatoRestauranteCreate(**data)
        
        assert plato.nombre == "Ensalada Caesar"
        assert plato.precio == Decimal('8.50')
    
    def test_plato_restaurante_invalid_tipo(self):
        """Test crear plato con tipo inválido"""
        from app.schemas.restaurant_menu import PlatoRestauranteCreate
        from pydantic import ValidationError
        
        data = {
            "nombre": "Plato Inválido",
            "precio": 10.00,
            "tipo": "Tipo_Inexistente"
        }
        
        with pytest.raises(ValidationError):
            PlatoRestauranteCreate(**data)
    
    def test_menu_dia_create_valid(self):
        """Test crear menú del día"""
        from app.schemas.restaurant_menu import MenuDiaCreate
        
        data = {
            "fecha": "2024-01-20",
            "nombre": "Menú Especial",
            "precio": 15.00,
            "descripcion": "Menú del día especial"
        }
        
        menu = MenuDiaCreate(**data)
        
        assert menu.fecha == date(2024, 1, 20)
        assert menu.precio == Decimal('15.00')
