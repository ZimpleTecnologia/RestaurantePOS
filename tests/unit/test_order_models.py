"""
Tests unitarios para modelos de pedido
"""
import pytest
from decimal import Decimal
from datetime import datetime


class TestOrderStatus:
    """Tests para el enum OrderStatus"""
    
    def test_order_status_values(self):
        """Verificar que todos los estados tienen valores correctos"""
        from app.models.order import OrderStatus
        
        assert OrderStatus.DRAFT.value == "borrador"
        assert OrderStatus.PENDING.value == "pendiente"
        assert OrderStatus.CONFIRMED.value == "confirmado"
        assert OrderStatus.PREPARING.value == "preparando"
        assert OrderStatus.READY.value == "listo"
        assert OrderStatus.SERVED.value == "servido"
        assert OrderStatus.PAID.value == "pagado"
        assert OrderStatus.CANCELLED.value == "cancelado"
    
    def test_order_status_count(self):
        """Verificar cantidad de estados"""
        from app.models.order import OrderStatus
        
        statuses = list(OrderStatus)
        assert len(statuses) == 8


class TestOrderType:
    """Tests para el enum OrderType"""
    
    def test_order_type_values(self):
        """Verificar valores de tipos de pedido"""
        from app.models.order import OrderType
        
        assert OrderType.DINE_IN.value == "mesa"
        assert OrderType.TAKEAWAY.value == "para_llevar"
        assert OrderType.DELIVERY.value == "domicilio"


class TestOrderSource:
    """Tests para el enum OrderSource"""
    
    def test_order_source_values(self):
        """Verificar valores de origen de pedido"""
        from app.models.order import OrderSource
        
        assert OrderSource.POS.value == "pos"
        assert OrderSource.KITCHEN.value == "cocina"
        assert OrderSource.KIOSK.value == "kiosco"
        assert OrderSource.APP.value == "app"


class TestItemType:
    """Tests para el enum ItemType"""
    
    def test_item_type_values(self):
        """Verificar valores de tipos de item"""
        from app.models.order import ItemType
        
        assert ItemType.PRODUCT.value == "product"
        assert ItemType.MENU.value == "menu"
        assert ItemType.PLATO.value == "plato"


class TestOrderModel:
    """Tests para el modelo Order"""
    
    def test_order_creation(self):
        """Test crear orden básica"""
        from app.models.order import Order, OrderStatus, OrderType
        
        order = Order(
            order_number="ORD-001",
            waiter_id=1,
            status=OrderStatus.DRAFT,
            order_type=OrderType.DINE_IN
        )
        
        assert order.order_number == "ORD-001"
        assert order.waiter_id == 1
        assert order.status == OrderStatus.DRAFT
        assert order.order_type == OrderType.DINE_IN
    
    def test_order_default_values(self):
        """Verificar valores por defecto"""
        from app.models.order import Order, OrderStatus, OrderType, OrderSource
        
        order = Order(order_number="ORD-002", waiter_id=1)
        
        assert order.status == OrderStatus.DRAFT
        assert order.order_type == OrderType.DINE_IN
        assert order.source == OrderSource.POS
        assert order.total_amount == Decimal('0.00')
        assert order.tax_amount == Decimal('0.00')
        assert order.discount_amount == Decimal('0.00')
        assert order.final_amount == Decimal('0.00')
    
    def test_order_is_active(self):
        """Test propiedad is_active"""
        from app.models.order import Order, OrderStatus
        
        order_draft = Order(order_number="ORD-003", waiter_id=1, status=OrderStatus.DRAFT)
        assert order_draft.is_active == True
        
        order_pending = Order(order_number="ORD-004", waiter_id=1, status=OrderStatus.PENDING)
        assert order_pending.is_active == True
        
        order_paid = Order(order_number="ORD-005", waiter_id=1, status=OrderStatus.PAID)
        assert order_paid.is_active == False
        
        order_cancelled = Order(order_number="ORD-006", waiter_id=1, status=OrderStatus.CANCELLED)
        assert order_cancelled.is_active == False
    
    def test_order_can_be_served(self):
        """Test propiedad can_be_served"""
        from app.models.order import Order, OrderStatus
        
        order_ready = Order(order_number="ORD-007", waiter_id=1, status=OrderStatus.READY)
        assert order_ready.can_be_served == True
        
        order_pending = Order(order_number="ORD-008", waiter_id=1, status=OrderStatus.PENDING)
        assert order_pending.can_be_served == False
    
    def test_order_can_be_paid(self):
        """Test propiedad can_be_paid"""
        from app.models.order import Order, OrderStatus
        
        order_served = Order(order_number="ORD-009", waiter_id=1, status=OrderStatus.SERVED)
        assert order_served.can_be_paid == True
        
        order_ready = Order(order_number="ORD-010", waiter_id=1, status=OrderStatus.READY)
        assert order_ready.can_be_paid == False


class TestOrderItemModel:
    """Tests para el modelo OrderItem"""
    
    def test_order_item_creation(self):
        """Test crear item de orden"""
        from app.models.order import OrderItem, ItemType
        
        item = OrderItem(
            order_id=1,
            item_type=ItemType.PRODUCT,
            product_id=1,
            quantity=2,
            unit_price=Decimal('10.50'),
            total_price=Decimal('21.00')
        )
        
        assert item.order_id == 1
        assert item.item_type == ItemType.PRODUCT
        assert item.quantity == 2
        assert item.unit_price == Decimal('10.50')
        assert item.total_price == Decimal('21.00')
    
    def test_order_item_calculate_total(self):
        """Test cálculo de total"""
        from app.models.order import OrderItem
        
        item = OrderItem(
            order_id=1,
            quantity=3,
            unit_price=Decimal('15.00')
        )
        item.calculate_total()
        
        assert item.total_price == Decimal('45.00')
    
    def test_order_item_default_values(self):
        """Verificar valores por defecto"""
        from app.models.order import OrderItem, ItemType
        
        item = OrderItem(order_id=1, quantity=1, unit_price=Decimal('10.00'))
        
        assert item.item_type == ItemType.PRODUCT
        assert item.is_ready == False
        assert item.is_served == False


class TestOrderItemOptionModel:
    """Tests para el modelo OrderItemOption"""
    
    def test_order_item_option_creation(self):
        """Test crear opción de item"""
        from app.models.order import OrderItemOption
        
        option = OrderItemOption(
            order_item_id=1,
            categoria="Proteína",
            opcion_elegida="Pollo"
        )
        
        assert option.order_item_id == 1
        assert option.categoria == "Proteína"
        assert option.opcion_elegida == "Pollo"
