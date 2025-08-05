# Importar todos los modelos para facilitar su uso
from .user import User
from .product import Product, Category, SubCategory
from .sale import Sale, SaleItem, PaymentMethod
from .customer import Customer, Credit, Payment
from .supplier import Supplier, Purchase, PurchaseItem
from .location import Location, Table
from .inventory import Inventory, InventoryMovement
from .recipe import Recipe, RecipeItem

__all__ = [
    "User",
    "Product", 
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
    "Inventory",
    "InventoryMovement",
    "Recipe",
    "RecipeItem"
] 