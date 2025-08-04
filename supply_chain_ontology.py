"""
Supply Chain Management System - Data Model & Ontology Layer
A comprehensive system modeling Walmart-scale supply chain operations
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
from datetime import datetime, timedelta
import uuid
import json

# Enumerations for controlled vocabularies
class LocationType(Enum):
    WAREHOUSE = "warehouse"
    FACTORY = "factory"
    PORT = "port"
    RETAIL_STORE = "retail_store"
    DISTRIBUTION_CENTER = "distribution_center"

class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class ShipmentStatus(Enum):
    SCHEDULED = "scheduled"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DELAYED = "delayed"

class VehicleType(Enum):
    TRUCK = "truck"
    SHIP = "ship"
    PLANE = "plane"
    TRAIN = "train"

class EmployeeRole(Enum):
    MANAGER = "manager"
    OPERATOR = "operator"
    DRIVER = "driver"
    ANALYST = "analyst"

# Core Entity Classes with Ontology Mapping

@dataclass
class Product:
    """Core product entity with comprehensive properties"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sku: str = ""
    name: str = ""
    category: str = ""
    weight_kg: float = 0.0
    volume_m3: float = 0.0
    cost_usd: float = 0.0
    safety_stock_level: int = 0
    lead_time_days: int = 0
    supplier_ids: List[str] = field(default_factory=list)
    
    # Ontology properties
    ontology_class: str = "Product"
    semantic_tags: Set[str] = field(default_factory=set)
    
    def to_ontology_dict(self) -> Dict:
        return {
            "class": self.ontology_class,
            "id": self.id,
            "properties": {
                "sku": self.sku,
                "name": self.name,
                "category": self.category,
                "physical_properties": {
                    "weight_kg": self.weight_kg,
                    "volume_m3": self.volume_m3
                },
                "economic_properties": {
                    "cost_usd": self.cost_usd
                },
                "supply_properties": {
                    "safety_stock_level": self.safety_stock_level,
                    "lead_time_days": self.lead_time_days
                }
            },
            "relationships": {
                "supplied_by": self.supplier_ids
            },
            "semantic_tags": list(self.semantic_tags)
        }

@dataclass
class Location:
    """Location entity representing warehouses, factories, ports, stores"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: LocationType = LocationType.WAREHOUSE
    address: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    capacity_m3: float = 0.0
    operational_hours: str = "24/7"
    temperature_zone: str = "ambient"
    manager_id: Optional[str] = None
    
    # Ontology properties
    ontology_class: str = "Location"
    
    def to_ontology_dict(self) -> Dict:
        return {
            "class": self.ontology_class,
            "id": self.id,
            "properties": {
                "name": self.name,
                "type": self.type.value,
                "address": self.address,
                "coordinates": {
                    "latitude": self.latitude,
                    "longitude": self.longitude
                },
                "operational_properties": {
                    "capacity_m3": self.capacity_m3,
                    "operational_hours": self.operational_hours,
                    "temperature_zone": self.temperature_zone
                }
            },
            "relationships": {
                "managed_by": self.manager_id
            }
        }

@dataclass
class Supplier:
    """Supplier entity with comprehensive business properties"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    contact_info: str = ""
    location_id: str = ""
    reliability_score: float = 0.0  # 0-1 scale
    product_ids: List[str] = field(default_factory=list)
    
    ontology_class: str = "Supplier"
    
    def to_ontology_dict(self) -> Dict:
        return {
            "class": self.ontology_class,
            "id": self.id,
            "properties": {
                "name": self.name,
                "contact_info": self.contact_info,
                "reliability_score": self.reliability_score
            },
            "relationships": {
                "located_at": self.location_id,
                "supplies": self.product_ids
            }
        }

@dataclass
class Customer:
    """Customer entity for B2B and B2C relationships"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = "retail"  # retail, wholesale, business
    contact_info: str = ""
    location_id: str = ""
    
    ontology_class: str = "Customer"
    
    def to_ontology_dict(self) -> Dict:
        return {
            "class": self.ontology_class,
            "id": self.id,
            "properties": {
                "name": self.name,
                "type": self.type,
                "contact_info": self.contact_info
            },
            "relationships": {
                "located_at": self.location_id
            }
        }

@dataclass
class Order:
    """Order entity linking customers and products"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    product_quantities: Dict[str, int] = field(default_factory=dict)  # product_id -> quantity
    order_date: datetime = field(default_factory=datetime.now)
    requested_delivery_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))
    status: OrderStatus = OrderStatus.PENDING
    total_value_usd: float = 0.0
    
    ontology_class: str = "Order"
    
    def to_ontology_dict(self) -> Dict:
        return {
            "class": self.ontology_class,
            "id": self.id,
            "properties": {
                "order_date": self.order_date.isoformat(),
                "requested_delivery_date": self.requested_delivery_date.isoformat(),
                "status": self.status.value,
                "total_value_usd": self.total_value_usd
            },
            "relationships": {
                "ordered_by": self.customer_id,
                "contains_products": self.product_quantities
            }
        }

@dataclass
class Inventory:
    """Inventory entity tracking product quantities at locations"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str = ""
    location_id: str = ""
    quantity: int = 0
    reserved_quantity: int = 0  # Reserved for orders
    last_updated: datetime = field(default_factory=datetime.now)
    
    ontology_class: str = "Inventory"
    
    def to_ontology_dict(self) -> Dict:
        return {
            "class": self.ontology_class,
            "id": self.id,
            "properties": {
                "quantity": self.quantity,
                "reserved_quantity": self.reserved_quantity,
                "available_quantity": self.quantity - self.reserved_quantity,
                "last_updated": self.last_updated.isoformat()
            },
            "relationships": {
                "product": self.product_id,
                "stored_at": self.location_id
            }
        }

@dataclass
class Vehicle:
    """Vehicle entity for transportation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: VehicleType = VehicleType.TRUCK
    capacity_m3: float = 0.0
    max_weight_kg: float = 0.0
    current_location_id: Optional[str] = None
    driver_id: Optional[str] = None
    
    ontology_class: str = "Vehicle"
    
    def to_ontology_dict(self) -> Dict:
        return {
            "class": self.ontology_class,
            "id": self.id,
            "properties": {
                "type": self.type.value,
                "capacity_m3": self.capacity_m3,
                "max_weight_kg": self.max_weight_kg
            },
            "relationships": {
                "currently_at": self.current_location_id,
                "operated_by": self.driver_id
            }
        }

@dataclass
class Shipment:
    """Shipment entity for tracking product movement"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str = ""
    origin_location_id: str = ""
    destination_location_id: str = ""
    vehicle_id: str = ""
    product_quantities: Dict[str, int] = field(default_factory=dict)
    scheduled_departure: datetime = field(default_factory=datetime.now)
    scheduled_arrival: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=3))
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    status: ShipmentStatus = ShipmentStatus.SCHEDULED
    
    ontology_class: str = "Shipment"
    
    def to_ontology_dict(self) -> Dict:
        return {
            "class": self.ontology_class,
            "id": self.id,
            "properties": {
                "scheduled_departure": self.scheduled_departure.isoformat(),
                "scheduled_arrival": self.scheduled_arrival.isoformat(),
                "actual_departure": self.actual_departure.isoformat() if self.actual_departure else None,
                "actual_arrival": self.actual_arrival.isoformat() if self.actual_arrival else None,
                "status": self.status.value
            },
            "relationships": {
                "fulfills_order": self.order_id,
                "origin": self.origin_location_id,
                "destination": self.destination_location_id,
                "transported_by": self.vehicle_id,
                "contains_products": self.product_quantities
            }
        }

@dataclass
class Employee:
    """Employee entity for workforce management"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    role: EmployeeRole = EmployeeRole.OPERATOR
    location_id: str = ""
    contact_info: str = ""
    
    ontology_class: str = "Employee"
    
    def to_ontology_dict(self) -> Dict:
        return {
            "class": self.ontology_class,
            "id": self.id,
            "properties": {
                "name": self.name,
                "role": self.role.value,
                "contact_info": self.contact_info
            },
            "relationships": {
                "works_at": self.location_id
            }
        }

@dataclass
class Machine:
    """Machine entity for manufacturing and automation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = ""  # conveyor, robot, packaging_machine, etc.
    location_id: str = ""
    capacity_per_hour: float = 0.0
    operational_status: str = "operational"  # operational, maintenance, broken
    
    ontology_class: str = "Machine"
    
    def to_ontology_dict(self) -> Dict:
        return {
            "class": self.ontology_class,
            "id": self.id,
            "properties": {
                "name": self.name,
                "type": self.type,
                "capacity_per_hour": self.capacity_per_hour,
                "operational_status": self.operational_status
            },
            "relationships": {
                "located_at": self.location_id
            }
        }

# Ontology Relationship Mapping
class SupplyChainOntology:
    """Central ontology manager for the supply chain system"""
    
    def __init__(self):
        self.entities = {}
        self.relationships = {
            "supplies": [],           # Supplier -> Product
            "contains": [],           # Order -> Product
            "stores": [],             # Location -> Inventory -> Product
            "transports": [],         # Shipment -> Product
            "produces": [],           # Factory -> Product
            "manages": [],            # Employee -> Location
            "operates": [],           # Employee -> Vehicle/Machine
            "located_at": [],         # Entity -> Location
            "fulfills": [],           # Shipment -> Order
            "works_at": [],           # Employee -> Location
        }
    
    def add_entity(self, entity):
        """Add an entity to the ontology"""
        self.entities[entity.id] = entity
    
    def add_relationship(self, relationship_type: str, source_id: str, target_id: str, properties: Dict = None):
        """Add a relationship between entities"""
        if relationship_type not in self.relationships:
            self.relationships[relationship_type] = []
        
        self.relationships[relationship_type].append({
            "source": source_id,
            "target": target_id,
            "properties": properties or {}
        })
    
    def get_entity_relationships(self, entity_id: str) -> Dict:
        """Get all relationships for a specific entity"""
        relationships = {}
        for rel_type, relations in self.relationships.items():
            relationships[rel_type] = []
            for relation in relations:
                if relation["source"] == entity_id or relation["target"] == entity_id:
                    relationships[rel_type].append(relation)
        return relationships
    
    def export_full_ontology(self) -> Dict:
        """Export the complete ontology as a structured dictionary"""
        return {
            "entities": {eid: entity.to_ontology_dict() for eid, entity in self.entities.items()},
            "relationships": self.relationships,
            "metadata": {
                "total_entities": len(self.entities),
                "relationship_types": list(self.relationships.keys()),
                "export_timestamp": datetime.now().isoformat()
            }
        }
    
    def query_by_type(self, entity_type: str) -> List:
        """Query entities by their ontology class"""
        return [entity for entity in self.entities.values() if entity.ontology_class == entity_type]
    
    def find_path(self, source_id: str, target_id: str, max_depth: int = 3) -> List:
        """Find relationship paths between two entities"""
        # Simple BFS implementation for finding paths
        from collections import deque
        
        queue = deque([(source_id, [source_id])])
        visited = set()
        
        while queue and len(queue[0][1]) <= max_depth:
            current_id, path = queue.popleft()
            
            if current_id == target_id:
                return path
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            # Find all connected entities
            for rel_type, relations in self.relationships.items():
                for relation in relations:
                    next_id = None
                    if relation["source"] == current_id:
                        next_id = relation["target"]
                    elif relation["target"] == current_id:
                        next_id = relation["source"]
                    
                    if next_id and next_id not in visited:
                        queue.append((next_id, path + [next_id]))
        
        return []  # No path found