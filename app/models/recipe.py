"""
Modelos de Recetas para Combos y Productos Compuestos
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Recipe(Base):
    """Modelo de Receta"""
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    preparation_time = Column(Integer, default=0)  # en minutos
    instructions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Costo total de la receta (calculado automáticamente)
    total_cost = Column(Numeric(10, 2), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    product = relationship("Product", back_populates="recipe")
    items = relationship("RecipeItem", back_populates="recipe", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Recipe(id={self.id}, name='{self.name}', product_id={self.product_id})>"


class RecipeItem(Base):
    """Modelo de Item de Receta"""
    __tablename__ = "recipe_items"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), default="unidad")  # unidad, gramo, ml, etc.
    is_optional = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Costo unitario del ingrediente en el momento de la receta
    unit_cost = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(10, 2), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    recipe = relationship("Recipe", back_populates="items")
    product = relationship("Product", back_populates="recipe_items")
    
    def __repr__(self):
        return f"<RecipeItem(id={self.id}, recipe_id={self.recipe_id}, product_id={self.product_id})>" 