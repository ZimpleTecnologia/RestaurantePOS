"""
Modelos para el módulo de Pedidos a Cocina
Sistema específico para gestión de pedidos desde meseros hacia cocina
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
from decimal import Decimal
from datetime import datetime


class EstadoPedido(str, enum.Enum):
    """Estados del pedido"""
    BORRADOR = "BORRADOR"                           # Pedido en creación por el mesero
    ENVIADO_A_COCINA = "ENVIADO_A_COCINA"          # Pedido enviado a cocina
    PENDIENTE = "PENDIENTE"                         # En cocina, esperando preparación
    EN_PREPARACION = "EN_PREPARACION"              # Cocina está preparando
    LISTO = "LISTO"                                 # Listo para servir


class TipoItemPedido(str, enum.Enum):
    """Tipos de items en el pedido"""
    MENU = "MENU"           # Menú del día
    PLATO = "PLATO"         # Plato especial


class PedidoCocina(Base):
    """
    Modelo principal para pedidos a cocina
    """
    __tablename__ = "pedidos_cocina"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=False)
    mesero_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Estado del pedido
    estado = Column(Enum(EstadoPedido), default=EstadoPedido.BORRADOR, nullable=False)
    
    # Observaciones generales del pedido
    observaciones = Column(Text, nullable=True)
    
    # Timestamps
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    hora_envio = Column(DateTime(timezone=True), nullable=True)  # Cuando se envía a cocina
    hora_inicio_preparacion = Column(DateTime(timezone=True), nullable=True)  # Cuando cocina inicia
    hora_finalizacion = Column(DateTime(timezone=True), nullable=True)  # Cuando está listo
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    mesa = relationship("Mesa", backref="pedidos_cocina")
    mesero = relationship("User", backref="pedidos_cocina")
    detalles = relationship("PedidoDetalle", back_populates="pedido", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PedidoCocina(id={self.id}, mesa_id={self.mesa_id}, estado='{self.estado}')>"
    
    def puede_editar(self):
        """Verificar si el pedido puede ser editado"""
        return self.estado == EstadoPedido.BORRADOR
    
    def puede_enviar_cocina(self):
        """Verificar si el pedido puede ser enviado a cocina"""
        return self.estado == EstadoPedido.BORRADOR and len(self.detalles) > 0


class PedidoDetalle(Base):
    """
    Detalles de un pedido (menú del día o platos especiales)
    Usa snapshots para preservar información histórica
    """
    __tablename__ = "pedidos_detalle"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos_cocina.id"), nullable=False)
    
    # Tipo de item
    tipo_item = Column(Enum(TipoItemPedido), nullable=False)
    
    # Referencias (pueden ser null si el item fue eliminado después)
    menu_id = Column(Integer, ForeignKey("menus_dia.id"), nullable=True)  # Si es MENU
    plato_id = Column(Integer, ForeignKey("platos_restaurante.id"), nullable=True)  # Si es PLATO
    
    # Snapshots (preservar información histórica)
    nombre_snapshot = Column(String(200), nullable=False)  # Nombre del menú/plato al momento del pedido
    descripcion_snapshot = Column(Text, nullable=True)  # Descripción guardada
    precio_snapshot = Column(Numeric(10, 2), nullable=True)  # Precio guardado (solo para platos)
    
    # Observaciones específicas del item
    observaciones = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    pedido = relationship("PedidoCocina", back_populates="detalles")
    menu = relationship("app.models.restaurant_menu.MenuDia", foreign_keys=[menu_id])
    plato = relationship("app.models.restaurant_menu.PlatoRestaurante", foreign_keys=[plato_id])
    opciones = relationship("PedidoMenuOpcion", back_populates="detalle", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PedidoDetalle(id={self.id}, tipo='{self.tipo_item}', nombre='{self.nombre_snapshot}')>"


class PedidoMenuOpcion(Base):
    """
    Opciones seleccionadas para un menú del día
    Ej: Categoría "Proteína" -> Opción "Pollo"
    """
    __tablename__ = "pedidos_menu_opciones"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_detalle_id = Column(Integer, ForeignKey("pedidos_detalle.id"), nullable=False)
    
    # Categoría y opción elegida (snapshots)
    categoria = Column(String(50), nullable=False)  # Ej: "Proteína", "Principio"
    opcion_elegida = Column(String(200), nullable=False)  # Nombre del plato elegido (snapshot)
    opcion_plato_id = Column(Integer, ForeignKey("platos_restaurante.id"), nullable=True)  # Referencia al plato
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    detalle = relationship("PedidoDetalle", back_populates="opciones")
    plato = relationship("app.models.restaurant_menu.PlatoRestaurante", foreign_keys=[opcion_plato_id])
    
    def __repr__(self):
        return f"<PedidoMenuOpcion(id={self.id}, categoria='{self.categoria}', opcion='{self.opcion_elegida}')>"

