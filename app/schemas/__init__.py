# Importar todos los esquemas para facilitar su uso
from .user import UserCreate, UserUpdate, UserResponse, UserLogin
from .product import ProductCreate, ProductUpdate, ProductResponse, CategoryCreate, CategoryUpdate, CategoryResponse
from .sale import SaleCreate, SaleUpdate, SaleResponse, SaleItemCreate, SaleItemResponse
from .customer import CustomerCreate, CustomerUpdate, CustomerResponse, CreditCreate, CreditResponse
from .supplier import SupplierCreate, SupplierUpdate, SupplierResponse, PurchaseCreate, PurchaseResponse
from .location import LocationCreate, LocationUpdate, LocationResponse, TableCreate, TableResponse

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin",
    "ProductCreate", "ProductUpdate", "ProductResponse", 
    "CategoryCreate", "CategoryUpdate", "CategoryResponse",
    "SaleCreate", "SaleUpdate", "SaleResponse", 
    "SaleItemCreate", "SaleItemResponse",
    "CustomerCreate", "CustomerUpdate", "CustomerResponse",
    "CreditCreate", "CreditResponse",
    "SupplierCreate", "SupplierUpdate", "SupplierResponse",
    "PurchaseCreate", "PurchaseResponse",
    "LocationCreate", "LocationUpdate", "LocationResponse",
    "TableCreate", "TableResponse"
] 