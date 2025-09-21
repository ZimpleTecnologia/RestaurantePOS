# Importar todos los modelos para facilitar su uso
from .user import User
from .product import Product, ProductCategory, Category, SubCategory
from .sale import Sale, SaleItem, PaymentMethod
from .customer import Customer, Credit, Payment
from .supplier import Supplier, Purchase, PurchaseItem
from .location import Location, Table
from .inventory import InventoryMovement
from .recipe import Recipe, RecipeItem
from .settings import SystemSettings
from .order import Order, OrderItem
from .menu import MenuDayOld, CategoriaMenu, OpcionMenu, MenuStatus as OldMenuStatus, MenuStatus
from .carta_restaurante import CartaRestaurante, MenuDia as MenuDiaCarta, MenuOpcion, TipoPlato, CategoriaPlato
from .menu_restructured import CategoriaPlatoVariable, OpcionPlato, MenuDiaRestructured, MenuDiaOpcion

__all__ = [
    "User",
    "Product", 
    "ProductCategory",
    "Category",
    "SubCategory",
    "Sale",
    "SaleItem", 
    "PaymentMethod",
    "Customer",
    "Credit",
    "Payment",
    "Supplier",
    "Purchase",
    "PurchaseItem",
    "Location",
    "Table",
    "InventoryMovement",
    "Recipe",
    "RecipeItem",
    "SystemSettings",
    "Order",
    "OrderItem",
    "MenuDayOld",
    "CategoriaMenu", 
    "OpcionMenu",
    "OldMenuStatus",
    "MenuStatus",
    "CartaRestaurante",
    "MenuDiaCarta",
    "MenuOpcion",
    "TipoPlato",
    "CategoriaPlato",
    "CategoriaPlatoVariable",
    "OpcionPlato",
    "MenuDiaRestructured",
    "MenuDiaOpcion"
] 