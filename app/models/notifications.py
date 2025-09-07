"""
Modelo de Notificaciones para el sistema POS
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class NotificationType(str, enum.Enum):
    """Tipos de notificaciones"""
    ORDER_READY = "order_ready"
    ORDER_DELAYED = "order_delayed"
    ORDER_URGENT = "order_urgent"
    TABLE_CHECK = "table_check"
    INVENTORY_ALERT = "inventory_alert"
    LOW_STOCK = "low_stock"
    EXPIRING_PRODUCT = "expiring_product"
    SYSTEM_ALERT = "system_alert"
    PAYMENT_RECEIVED = "payment_received"
    CASH_REGISTER_ALERT = "cash_register_alert"


class NotificationPriority(str, enum.Enum):
    """Prioridades de notificaciones"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """Modelo de Notificación"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información de la notificación
    type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Datos adicionales (JSON)
    data = Column(JSON, nullable=True)
    
    # Estado
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    user = relationship("User", backref="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type}', title='{self.title}')>"
    
    def mark_as_read(self):
        """Marcar notificación como leída"""
        self.is_read = True
        self.read_at = func.now()
    
    def dismiss(self):
        """Descartar notificación"""
        self.is_dismissed = True
        self.dismissed_at = func.now()
    
    @property
    def is_active(self):
        """Verificar si la notificación está activa"""
        return not self.is_dismissed
    
    @property
    def age_minutes(self):
        """Obtener edad de la notificación en minutos"""
        from datetime import datetime
        return int((datetime.utcnow() - self.created_at).total_seconds() / 60)
    
    @property
    def priority_color(self):
        """Obtener color CSS para la prioridad"""
        colors = {
            NotificationPriority.LOW: "info",
            NotificationPriority.MEDIUM: "warning",
            NotificationPriority.HIGH: "danger",
            NotificationPriority.URGENT: "danger"
        }
        return colors.get(self.priority, "secondary")
    
    @property
    def priority_icon(self):
        """Obtener icono para la prioridad"""
        icons = {
            NotificationPriority.LOW: "info-circle",
            NotificationPriority.MEDIUM: "exclamation-triangle",
            NotificationPriority.HIGH: "exclamation-triangle-fill",
            NotificationPriority.URGENT: "exclamation-octagon-fill"
        }
        return icons.get(self.priority, "bell")
