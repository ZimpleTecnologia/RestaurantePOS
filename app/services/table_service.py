"""
Servicio para el manejo de mesas del restaurante
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.location import Table, TableStatus
from app.models.order import Order, OrderStatus


class TableService:
    """Servicio para manejo de mesas"""
    
    @staticmethod
    def get_all_tables(db: Session) -> List[Table]:
        """Obtener todas las mesas activas"""
        return db.query(Table).filter(Table.is_active == True).order_by(Table.table_number).all()
    
    @staticmethod
    def get_table_by_id(db: Session, table_id: int) -> Optional[Table]:
        """Obtener mesa por ID"""
        return db.query(Table).filter(Table.id == table_id).first()
    
    @staticmethod
    def get_table_by_number(db: Session, table_number: str) -> Optional[Table]:
        """Obtener mesa por número"""
        return db.query(Table).filter(Table.table_number == table_number).first()
    
    @staticmethod
    def get_available_tables(db: Session) -> List[Table]:
        """Obtener mesas disponibles"""
        return db.query(Table).filter(
            and_(
                Table.is_active == True,
                Table.status == TableStatus.AVAILABLE
            )
        ).order_by(Table.table_number).all()
    
    @staticmethod
    def get_occupied_tables(db: Session) -> List[Table]:
        """Obtener mesas ocupadas"""
        return db.query(Table).filter(
            and_(
                Table.is_active == True,
                Table.status == TableStatus.OCCUPIED
            )
        ).order_by(Table.table_number).all()
    
    @staticmethod
    def create_table(
        db: Session, 
        table_number: str, 
        name: str, 
        capacity: int = 4,
        location: str = None,
        description: str = None
    ) -> Table:
        """Crear una nueva mesa"""
        table = Table(
            table_number=table_number,
            name=name,
            capacity=capacity,
            location=location,
            description=description
        )
        db.add(table)
        db.commit()
        db.refresh(table)
        return table
    
    @staticmethod
    def update_table_status(db: Session, table_id: int, status: TableStatus) -> Optional[Table]:
        """Actualizar estado de una mesa"""
        table = TableService.get_table_by_id(db, table_id)
        if table:
            table.status = status
            db.commit()
            db.refresh(table)
        return table
    
    @staticmethod
    def occupy_table(db: Session, table_id: int) -> Optional[Table]:
        """Ocupar una mesa"""
        return TableService.update_table_status(db, table_id, TableStatus.OCCUPIED)
    
    @staticmethod
    def free_table(db: Session, table_id: int) -> Optional[Table]:
        """Liberar una mesa"""
        return TableService.update_table_status(db, table_id, TableStatus.AVAILABLE)
    
    @staticmethod
    def get_table_status_summary(db: Session) -> Dict[str, Any]:
        """Obtener resumen del estado de las mesas"""
        total_tables = db.query(Table).filter(Table.is_active == True).count()
        available_tables = db.query(Table).filter(
            and_(
                Table.is_active == True,
                Table.status == TableStatus.AVAILABLE
            )
        ).count()
        occupied_tables = db.query(Table).filter(
            and_(
                Table.is_active == True,
                Table.status == TableStatus.OCCUPIED
            )
        ).count()
        
        return {
            "total_tables": total_tables,
            "available_tables": available_tables,
            "occupied_tables": occupied_tables,
            "utilization_rate": (occupied_tables / total_tables * 100) if total_tables > 0 else 0
        }
    
    @staticmethod
    def get_table_with_active_order(db: Session, table_id: int) -> Optional[Dict[str, Any]]:
        """Obtener mesa con su pedido activo"""
        table = TableService.get_table_by_id(db, table_id)
        if not table:
            return None
        
        active_order = None
        if table.has_active_order:
            active_order = table.current_order
        
        return {
            "table": {
                "id": table.id,
                "table_number": table.table_number,
                "name": table.name,
                "capacity": table.capacity,
                "status": table.status,
                "location": table.location
            },
            "active_order": {
                "id": active_order.id,
                "order_number": active_order.order_number,
                "status": active_order.status,
                "total_amount": float(active_order.total_amount),
                "final_amount": float(active_order.final_amount),
                "created_at": active_order.created_at,
                "items_count": len(active_order.items)
            } if active_order else None
        }
    
    @staticmethod
    def initialize_default_tables(db: Session) -> List[Table]:
        """Inicializar mesas por defecto"""
        default_tables = [
            {"table_number": "M1", "name": "Mesa 1", "capacity": 4, "location": "Interior"},
            {"table_number": "M2", "name": "Mesa 2", "capacity": 4, "location": "Interior"},
            {"table_number": "M3", "name": "Mesa 3", "capacity": 6, "location": "Interior"},
            {"table_number": "M4", "name": "Mesa 4", "capacity": 4, "location": "Interior"},
            {"table_number": "T1", "name": "Terraza 1", "capacity": 4, "location": "Terraza"},
            {"table_number": "T2", "name": "Terraza 2", "capacity": 6, "location": "Terraza"},
            {"table_number": "B1", "name": "Bar 1", "capacity": 2, "location": "Bar"},
            {"table_number": "B2", "name": "Bar 2", "capacity": 2, "location": "Bar"},
        ]
        
        created_tables = []
        for table_data in default_tables:
            existing = TableService.get_table_by_number(db, table_data["table_number"])
            if not existing:
                table = TableService.create_table(
                    db=db,
                    table_number=table_data["table_number"],
                    name=table_data["name"],
                    capacity=table_data["capacity"],
                    location=table_data["location"]
                )
                created_tables.append(table)
        
        return created_tables
