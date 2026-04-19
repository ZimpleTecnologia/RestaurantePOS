# Tests Unitarios - RestaurantePOS

Este directorio contiene los tests unitarios para el sistema POS.

## Estructura

```
tests/
├── conftest.py                 # Configuración de pytest
├── pytest.ini                  # Configuración de pytest
├── __init__.py
├── unit/                       # Tests unitarios
│   ├── __init__.py
│   ├── test_order_models.py   # Tests para modelos de pedido
│   ├── test_user_models.py    # Tests para modelos de usuario
│   ├── test_schemas.py        # Tests para schemas Pydantic
│   └── test_menu_models.py    # Tests para modelos de menú
└── integration/                # Tests de integración
    └── __init__.py
```

## Ejecución de Tests

### Instalar dependencias de test
```bash
pip install pytest pytest-cov
```

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar tests unitarios solo
```bash
pytest tests/unit/
```

### Ejecutar tests con coverage
```bash
pytest --cov=app --cov-report=html
```

### Ejecutar tests específicos
```bash
# Tests de modelos de orden
pytest tests/unit/test_order_models.py

# Tests de schemas
pytest tests/unit/test_schemas.py -v
```

## Cobertura Actual

Los tests cubren:
- Modelos: Order, OrderItem, OrderItemOption, User, Permiso, MenuDia, PlatoRestaurante, CategoriaMenuRestaurante
- Enums: OrderStatus, OrderType, OrderSource, ItemType, UserRole, TableStatus
- Schemas: UserCreate, OrderCreate, ProductCreate, MesaCreate, TableCreate, CategoriaMenuCreate, PlatoRestauranteCreate, MenuDiaCreate

## Agregar Nuevos Tests

1. Crear archivo `test_<modulo>.py` en `tests/unit/`
2. Importar los módulos a testar
3. Crear clases de test con el prefijo `Test`
4. Crear métodos con el prefijo `test_`

Ejemplo:
```python
class TestMyModel:
    def test_creation(self):
        from app.models import MyModel
        obj = MyModel(...)
        assert obj.field == expected
```
