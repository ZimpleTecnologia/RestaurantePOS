"""
Servicio para manejar el consumo automático de inventario
cuando se venden productos que tienen recetas
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from decimal import Decimal
import logging

from app.models.product import Product, ProductType
from app.models.recipe import Recipe, RecipeItem
from app.models.inventory import InventoryMovement, MovementType, MovementReason
from app.models.user import User

logger = logging.getLogger(__name__)


class InventoryConsumptionService:
    """Servicio para manejar el consumo de inventario"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def consume_inventory_for_sale(self, product_id: int, quantity: int, user_id: int, 
                                 sale_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Consumir inventario cuando se vende un producto que tiene receta
        
        Args:
            product_id: ID del producto vendido
            quantity: Cantidad vendida
            user_id: ID del usuario que realiza la venta
            sale_id: ID de la venta (opcional)
            
        Returns:
            Dict con información del consumo realizado
        """
        try:
            # Obtener el producto
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ValueError(f"Producto con ID {product_id} no encontrado")
            
            # Verificar si es un producto de venta con receta
            if not product.can_consume_inventory():
                return {
                    "success": True,
                    "message": "Producto no requiere consumo de inventario",
                    "consumed_items": []
                }
            
            # Obtener la receta del producto
            recipe = self.db.query(Recipe).filter(
                and_(
                    Recipe.product_id == product_id,
                    Recipe.is_active == True
                )
            ).first()
            
            if not recipe:
                logger.warning(f"Producto {product.name} no tiene receta activa")
                return {
                    "success": True,
                    "message": "Producto no tiene receta activa",
                    "consumed_items": []
                }
            
            # Obtener los ingredientes de la receta
            recipe_items = self.db.query(RecipeItem).filter(
                and_(
                    RecipeItem.recipe_id == recipe.id,
                    RecipeItem.is_optional == False  # Solo ingredientes obligatorios
                )
            ).all()
            
            if not recipe_items:
                logger.warning(f"Receta {recipe.name} no tiene ingredientes")
                return {
                    "success": True,
                    "message": "Receta no tiene ingredientes",
                    "consumed_items": []
                }
            
            # Determinar si hay ingredientes con stock insuficiente
            consumed_items = []
            insufficient_stock_items = []
            for recipe_item in recipe_items:
                required_quantity = recipe_item.quantity * quantity
                ingredient = self.db.query(Product).filter(Product.id == recipe_item.product_id).first()
                
                if ingredient and ingredient.is_inventory_product:
                    if ingredient.stock_quantity < required_quantity:
                        insufficient_stock_items.append({
                            "ingredient_id": ingredient.id,
                            "ingredient_name": ingredient.name,
                            "required": required_quantity,
                            "available": ingredient.stock_quantity,
                            "shortage": required_quantity - ingredient.stock_quantity
                        })

            # Consumir el inventario (permitiendo negativo según requerimiento)
            for recipe_item in recipe_items:
                required_quantity = recipe_item.quantity * quantity
                
                # Obtener el producto ingrediente
                ingredient = self.db.query(Product).filter(
                    Product.id == recipe_item.product_id
                ).first()
                
                if not ingredient or not ingredient.is_inventory_product:
                    continue

                # Calcular nuevos valores
                previous_stock = ingredient.stock_quantity
                new_stock = previous_stock - required_quantity
                
                # Crear movimiento de inventario
                movement = InventoryMovement(
                    product_id=ingredient.id,
                    user_id=user_id,
                    adjustment_type=MovementType.SALIDA,
                    reason=MovementReason.VENTA,
                    # reason_detail deprecado en favor de notes en este modelo
                    quantity=required_quantity,
                    previous_stock=previous_stock,
                    new_stock=new_stock,
                    # reference_type/id no están en el modelo actual de InventoryMovement en inventory.py
                    # adaptando a los campos reales vistos en view_file
                    notes=f"Consumo automático por venta de {product.name} (cantidad: {quantity}). ID Venta: {sale_id}"
                )
                
                self.db.add(movement)
                
                # Actualizar stock del ingrediente (permite negativo)
                ingredient.stock_quantity = new_stock
                
                # Generar alerta si el stock es negativo (Deuda de Stock)
                if new_stock < 0:
                    from app.models.inventory import InventoryAlert
                    alert = InventoryAlert(
                        product_id=ingredient.id,
                        alert_type="shortage",
                        alert_level="critical",
                        message=f"⚠️ DEUDA DE STOCK: El producto {ingredient.name} quedó en {new_stock} {ingredient.unit} tras la venta de {product.name}.",
                        is_active=True
                    )
                    self.db.add(alert)
                
                consumed_items.append({
                    "ingredient_id": ingredient.id,
                    "ingredient_name": ingredient.name,
                    "quantity_consumed": required_quantity,
                    "unit": recipe_item.unit,
                    "unit_cost": float(ingredient.purchase_price or 0),
                    "total_cost": float((ingredient.purchase_price or 0) * required_quantity),
                    "is_negative": new_stock < 0
                })
            
            # Confirmar cambios
            self.db.commit()
            
            message = "Consumo de inventario realizado exitosamente"
            if insufficient_stock_items:
                message += " (con alerta de deuda de stock)"
            
            logger.info(f"Consumo de inventario exitoso para producto {product.name} (cantidad: {quantity})")
            
            return {
                "success": True,
                "message": message,
                "consumed_items": consumed_items,
                "total_cost": sum(item["total_cost"] for item in consumed_items),
                "has_shortage": len(insufficient_stock_items) > 0
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al consumir inventario: {str(e)}")
            raise e
    
    def check_inventory_availability(self, product_id: int, quantity: int) -> Dict[str, Any]:
        """
        Verificar disponibilidad de inventario para un producto con receta
        
        Args:
            product_id: ID del producto
            quantity: Cantidad a verificar
            
        Returns:
            Dict con información de disponibilidad
        """
        try:
            # Obtener el producto
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ValueError(f"Producto con ID {product_id} no encontrado")
            
            # Verificar si es un producto de venta con receta
            if not product.can_consume_inventory():
                return {
                    "available": True,
                    "message": "Producto no requiere inventario",
                    "ingredients": []
                }
            
            # Obtener la receta del producto
            recipe = self.db.query(Recipe).filter(
                and_(
                    Recipe.product_id == product_id,
                    Recipe.is_active == True
                )
            ).first()
            
            if not recipe:
                return {
                    "available": True,
                    "message": "Producto no tiene receta activa",
                    "ingredients": []
                }
            
            # Obtener los ingredientes de la receta
            recipe_items = self.db.query(RecipeItem).filter(
                and_(
                    RecipeItem.recipe_id == recipe.id,
                    RecipeItem.is_optional == False
                )
            ).all()
            
            ingredients_status = []
            all_available = True
            
            for recipe_item in recipe_items:
                required_quantity = recipe_item.quantity * quantity
                
                # Obtener el producto ingrediente
                ingredient = self.db.query(Product).filter(
                    Product.id == recipe_item.product_id
                ).first()
                
                if not ingredient or not ingredient.is_inventory_product:
                    continue
                
                available = ingredient.stock_quantity >= required_quantity
                if not available:
                    all_available = False
                
                ingredients_status.append({
                    "ingredient_id": ingredient.id,
                    "ingredient_name": ingredient.name,
                    "required": required_quantity,
                    "available": ingredient.stock_quantity,
                    "sufficient": available,
                    "unit": recipe_item.unit
                })
            
            return {
                "available": all_available,
                "message": "Stock disponible" if all_available else "Stock insuficiente",
                "ingredients": ingredients_status
            }
            
        except Exception as e:
            logger.error(f"Error al verificar disponibilidad: {str(e)}")
            raise e
    
    def get_recipe_cost(self, product_id: int) -> Dict[str, Any]:
        """
        Calcular el costo total de una receta basado en los precios actuales de los ingredientes
        
        Args:
            product_id: ID del producto
            
        Returns:
            Dict con información del costo de la receta
        """
        try:
            # Obtener el producto
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ValueError(f"Producto con ID {product_id} no encontrado")
            
            # Obtener la receta del producto
            recipe = self.db.query(Recipe).filter(
                and_(
                    Recipe.product_id == product_id,
                    Recipe.is_active == True
                )
            ).first()
            
            if not recipe:
                return {
                    "has_recipe": False,
                    "total_cost": 0,
                    "ingredients": []
                }
            
            # Obtener los ingredientes de la receta
            recipe_items = self.db.query(RecipeItem).filter(
                RecipeItem.recipe_id == recipe.id
            ).all()
            
            ingredients_cost = []
            total_cost = Decimal('0')
            
            for recipe_item in recipe_items:
                # Obtener el producto ingrediente
                ingredient = self.db.query(Product).filter(
                    Product.id == recipe_item.product_id
                ).first()
                
                if not ingredient or not ingredient.is_inventory_product:
                    continue
                
                unit_cost = ingredient.purchase_price or Decimal('0')
                item_cost = unit_cost * recipe_item.quantity
                total_cost += item_cost
                
                ingredients_cost.append({
                    "ingredient_id": ingredient.id,
                    "ingredient_name": ingredient.name,
                    "quantity": recipe_item.quantity,
                    "unit": recipe_item.unit,
                    "unit_cost": float(unit_cost),
                    "total_cost": float(item_cost),
                    "is_optional": recipe_item.is_optional
                })
            
            # Actualizar el costo total de la receta
            recipe.total_cost = total_cost
            self.db.commit()
            
            return {
                "has_recipe": True,
                "total_cost": float(total_cost),
                "ingredients": ingredients_cost,
                "recipe_id": recipe.id,
                "recipe_name": recipe.name
            }
            
        except Exception as e:
            logger.error(f"Error al calcular costo de receta: {str(e)}")
            raise e
