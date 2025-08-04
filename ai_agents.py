"""
AI Agent Framework for Supply Chain Management
Implements different types of AI agents for query processing and reasoning
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from supply_chain_ontology import SupplyChainOntology

@dataclass
class AgentThought:
    """Represents a single thought/reasoning step by an agent"""
    step: int
    thought: str
    action: str
    observation: str
    confidence: float = 0.0

@dataclass
class QueryResult:
    """Result of a query processed by an agent"""
    query: str
    answer: str
    agent_type: str
    thoughts: List[AgentThought]
    data: Dict[str, Any]
    confidence: float
    execution_time_ms: float

class BaseAgent(ABC):
    """Abstract base class for all AI agents"""
    
    def __init__(self, ontology: SupplyChainOntology, name: str = "BaseAgent"):
        self.ontology = ontology
        self.name = name
        self.thoughts = []
        
    def add_thought(self, thought: str, action: str, observation: str, confidence: float = 0.0):
        """Add a reasoning step to the agent's thought process"""
        step = len(self.thoughts) + 1
        self.thoughts.append(AgentThought(step, thought, action, observation, confidence))
    
    def clear_thoughts(self):
        """Clear the agent's thought history"""
        self.thoughts = []
    
    @abstractmethod
    def process_query(self, query: str) -> QueryResult:
        """Process a natural language query and return results"""
        pass
    
    def _parse_query_intent(self, query: str) -> Dict[str, Any]:
        """Parse the intent and entities from a natural language query"""
        query_lower = query.lower()
        
        # Intent classification patterns
        intent_patterns = {
            "inventory_query": [
                r"how many.*items.*store", r"inventory.*level", r"stock.*level",
                r"quantity.*available", r"items.*in.*store", r"products.*at.*location"
            ],
            "location_query": [
                r"where.*located", r"which.*location", r"find.*location",
                r"address.*of", r"coordinates.*of"
            ],
            "order_status": [
                r"order.*status", r"track.*order", r"delivery.*status",
                r"shipment.*status", r"when.*arrive"
            ],
            "supplier_query": [
                r"who.*supplies", r"supplier.*of", r"vendor.*for",
                r"source.*of", r"manufacturer.*of"
            ],
            "capacity_query": [
                r"capacity.*of", r"how much.*can.*store", r"maximum.*capacity",
                r"storage.*space", r"warehouse.*size"
            ],
            "employee_query": [
                r"who.*works.*at", r"manager.*of", r"employees.*at",
                r"staff.*at", r"personnel.*at"
            ],
            "performance_query": [
                r"performance.*of", r"efficiency.*of", r"utilization.*of",
                r"throughput.*of", r"productivity.*of"
            ]
        }
        
        # Find matching intent
        intent = "general_query"
        for intent_type, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    intent = intent_type
                    break
            if intent != "general_query":
                break
        
        # Extract entities (locations, products, etc.)
        entities = self._extract_entities(query)
        
        return {
            "intent": intent,
            "entities": entities,
            "original_query": query
        }
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract named entities from the query"""
        entities = {
            "locations": [],
            "products": [],
            "suppliers": [],
            "customers": [],
            "employees": []
        }
        
        query_lower = query.lower()
        
        # Extract location names
        for entity in self.ontology.entities.values():
            if hasattr(entity, 'name') and entity.name:
                entity_name_lower = entity.name.lower()
                if entity_name_lower in query_lower:
                    if entity.ontology_class == "Location":
                        entities["locations"].append(entity.name)
                    elif entity.ontology_class == "Product":
                        entities["products"].append(entity.name)
                    elif entity.ontology_class == "Supplier":
                        entities["suppliers"].append(entity.name)
                    elif entity.ontology_class == "Customer":
                        entities["customers"].append(entity.name)
                    elif entity.ontology_class == "Employee":
                        entities["employees"].append(entity.name)
        
        return entities

class SimpleReflexAgent(BaseAgent):
    """Simple reflex agent that acts based on current environment state using predefined rules"""
    
    def __init__(self, ontology: SupplyChainOntology):
        super().__init__(ontology, "SimpleReflexAgent")
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict[str, callable]:
        """Initialize predefined rules for different query types"""
        return {
            "inventory_query": self._handle_inventory_query,
            "location_query": self._handle_location_query,
            "order_status": self._handle_order_status,
            "supplier_query": self._handle_supplier_query,
            "capacity_query": self._handle_capacity_query,
            "employee_query": self._handle_employee_query,
            "performance_query": self._handle_performance_query,
            "general_query": self._handle_general_query
        }
    
    def process_query(self, query: str) -> QueryResult:
        """Process query using simple reflex rules"""
        start_time = datetime.now()
        self.clear_thoughts()
        
        # Parse query intent
        parsed = self._parse_query_intent(query)
        intent = parsed["intent"]
        entities = parsed["entities"]
        
        self.add_thought(
            f"Parsing query: '{query}'",
            f"Identified intent: {intent}",
            f"Extracted entities: {entities}",
            0.8
        )
        
        # Apply appropriate rule
        if intent in self.rules:
            result_data = self.rules[intent](entities, query)
            confidence = 0.8
        else:
            result_data = {"error": "Unknown query type"}
            confidence = 0.2
        
        # Generate answer
        answer = self._generate_answer(intent, result_data, entities)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QueryResult(
            query=query,
            answer=answer,
            agent_type="SimpleReflexAgent",
            thoughts=self.thoughts.copy(),
            data=result_data,
            confidence=confidence,
            execution_time_ms=execution_time
        )
    
    def _handle_inventory_query(self, entities: Dict, query: str) -> Dict:
        """Handle inventory-related queries"""
        self.add_thought(
            "Processing inventory query",
            "Searching for inventory data",
            "Looking for matching locations and products",
            0.9
        )
        
        inventory_data = []
        locations = entities.get("locations", [])
        products = entities.get("products", [])
        
        # Get all inventory entities
        inventory_entities = self.ontology.query_by_type("Inventory")
        
        for inv in inventory_entities:
            # Get related location and product
            location = self.ontology.entities.get(inv.location_id)
            product = self.ontology.entities.get(inv.product_id)
            
            if location and product:
                # Filter by entities mentioned in query
                include_item = True
                if locations and location.name not in locations:
                    include_item = False
                if products and product.name not in products:
                    include_item = False
                
                if include_item:
                    inventory_data.append({
                        "location": location.name,
                        "product": product.name,
                        "quantity": inv.quantity,
                        "available": inv.quantity - inv.reserved_quantity,
                        "reserved": inv.reserved_quantity
                    })
        
        self.add_thought(
            "Found inventory records",
            f"Retrieved {len(inventory_data)} inventory items",
            f"Matching locations: {locations}, products: {products}",
            0.9
        )
        
        return {"inventory": inventory_data, "total_items": len(inventory_data)}
    
    def _handle_location_query(self, entities: Dict, query: str) -> Dict:
        """Handle location-related queries"""
        self.add_thought(
            "Processing location query",
            "Searching for location information",
            "Looking for matching locations",
            0.9
        )
        
        locations = self.ontology.query_by_type("Location")
        location_data = []
        
        for location in locations:
            if not entities.get("locations") or location.name in entities["locations"]:
                location_data.append({
                    "name": location.name,
                    "type": location.type.value,
                    "address": location.address,
                    "coordinates": {"lat": location.latitude, "lon": location.longitude},
                    "capacity_m3": location.capacity_m3,
                    "operational_hours": location.operational_hours
                })
        
        return {"locations": location_data}
    
    def _handle_order_status(self, entities: Dict, query: str) -> Dict:
        """Handle order status queries"""
        orders = self.ontology.query_by_type("Order")
        shipments = self.ontology.query_by_type("Shipment")
        
        order_data = []
        for order in orders:
            customer = self.ontology.entities.get(order.customer_id)
            order_shipments = [s for s in shipments if s.order_id == order.id]
            
            order_info = {
                "order_id": order.id,
                "customer": customer.name if customer else "Unknown",
                "status": order.status.value,
                "order_date": order.order_date.isoformat(),
                "delivery_date": order.requested_delivery_date.isoformat(),
                "total_value": order.total_value_usd,
                "shipments": len(order_shipments)
            }
            order_data.append(order_info)
        
        return {"orders": order_data}
    
    def _handle_supplier_query(self, entities: Dict, query: str) -> Dict:
        """Handle supplier-related queries"""
        suppliers = self.ontology.query_by_type("Supplier")
        supplier_data = []
        
        for supplier in suppliers:
            products = [self.ontology.entities.get(pid) for pid in supplier.product_ids]
            product_names = [p.name for p in products if p]
            
            supplier_info = {
                "name": supplier.name,
                "reliability_score": supplier.reliability_score,
                "products_supplied": product_names,
                "product_count": len(product_names)
            }
            supplier_data.append(supplier_info)
        
        return {"suppliers": supplier_data}
    
    def _handle_capacity_query(self, entities: Dict, query: str) -> Dict:
        """Handle capacity-related queries"""
        locations = self.ontology.query_by_type("Location")
        capacity_data = []
        
        for location in locations:
            if not entities.get("locations") or location.name in entities["locations"]:
                capacity_data.append({
                    "location": location.name,
                    "type": location.type.value,
                    "capacity_m3": location.capacity_m3,
                    "utilization": self._calculate_utilization(location)
                })
        
        return {"capacity_info": capacity_data}
    
    def _handle_employee_query(self, entities: Dict, query: str) -> Dict:
        """Handle employee-related queries"""
        employees = self.ontology.query_by_type("Employee")
        employee_data = []
        
        for employee in employees:
            location = self.ontology.entities.get(employee.location_id)
            employee_info = {
                "name": employee.name,
                "role": employee.role.value,
                "location": location.name if location else "Unknown"
            }
            employee_data.append(employee_info)
        
        return {"employees": employee_data}
    
    def _handle_performance_query(self, entities: Dict, query: str) -> Dict:
        """Handle performance-related queries"""
        # Simple performance metrics
        locations = self.ontology.query_by_type("Location")
        orders = self.ontology.query_by_type("Order")
        shipments = self.ontology.query_by_type("Shipment")
        
        performance_data = {
            "total_locations": len(locations),
            "total_orders": len(orders),
            "completed_orders": len([o for o in orders if o.status.value == "delivered"]),
            "active_shipments": len([s for s in shipments if s.status.value == "in_transit"]),
            "order_completion_rate": len([o for o in orders if o.status.value == "delivered"]) / len(orders) if orders else 0
        }
        
        return {"performance": performance_data}
    
    def _handle_general_query(self, entities: Dict, query: str) -> Dict:
        """Handle general queries"""
        return {"message": "I can help with inventory, locations, orders, suppliers, capacity, employees, and performance queries."}
    
    def _calculate_utilization(self, location) -> float:
        """Calculate storage utilization for a location"""
        inventory_items = [inv for inv in self.ontology.query_by_type("Inventory") if inv.location_id == location.id]
        total_volume = sum(
            self.ontology.entities.get(inv.product_id).volume_m3 * inv.quantity 
            for inv in inventory_items 
            if self.ontology.entities.get(inv.product_id)
        )
        return min(total_volume / location.capacity_m3, 1.0) if location.capacity_m3 > 0 else 0.0
    
    def _generate_answer(self, intent: str, data: Dict, entities: Dict) -> str:
        """Generate natural language answer based on query results"""
        if intent == "inventory_query":
            if data.get("inventory"):
                total_items = sum(item["quantity"] for item in data["inventory"])
                answer = f"Found {data['total_items']} inventory records with a total of {total_items:,} items. "
                if len(data["inventory"]) <= 5:
                    for item in data["inventory"]:
                        answer += f"{item['product']} at {item['location']}: {item['available']} available ({item['reserved']} reserved). "
                else:
                    answer += "Top locations: " + ", ".join([f"{item['location']}: {item['quantity']}" for item in data["inventory"][:3]])
                return answer
            else:
                return "No inventory data found matching your query."
        
        elif intent == "location_query":
            if data.get("locations"):
                if len(data["locations"]) == 1:
                    loc = data["locations"][0]
                    return f"{loc['name']} is a {loc['type']} located at {loc['address']} with capacity of {loc['capacity_m3']:,.0f} m³."
                else:
                    return f"Found {len(data['locations'])} locations: " + ", ".join([loc['name'] for loc in data["locations"]])
            else:
                return "No locations found matching your query."
        
        elif intent == "order_status":
            if data.get("orders"):
                total_value = sum(order["total_value"] for order in data["orders"])
                status_counts = {}
                for order in data["orders"]:
                    status = order["status"]
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                answer = f"Found {len(data['orders'])} orders with total value ${total_value:,.2f}. "
                answer += "Status breakdown: " + ", ".join([f"{status}: {count}" for status, count in status_counts.items()])
                return answer
            else:
                return "No orders found."
        
        elif intent == "supplier_query":
            if data.get("suppliers"):
                return f"Found {len(data['suppliers'])} suppliers: " + ", ".join([
                    f"{s['name']} (supplies {s['product_count']} products)" for s in data["suppliers"][:5]
                ])
            else:
                return "No suppliers found."
        
        elif intent == "capacity_query":
            if data.get("capacity_info"):
                answer = "Capacity information: "
                for cap in data["capacity_info"][:5]:
                    utilization_pct = cap["utilization"] * 100
                    answer += f"{cap['location']}: {cap['capacity_m3']:,.0f} m³ ({utilization_pct:.1f}% utilized). "
                return answer
            else:
                return "No capacity information found."
        
        elif intent == "employee_query":
            if data.get("employees"):
                role_counts = {}
                for emp in data["employees"]:
                    role = emp["role"]
                    role_counts[role] = role_counts.get(role, 0) + 1
                
                answer = f"Found {len(data['employees'])} employees. "
                answer += "Role breakdown: " + ", ".join([f"{role}: {count}" for role, count in role_counts.items()])
                return answer
            else:
                return "No employees found."
        
        elif intent == "performance_query":
            if data.get("performance"):
                perf = data["performance"]
                return f"Performance Summary: {perf['total_locations']} locations, {perf['total_orders']} orders " \
                       f"({perf['completed_orders']} completed, {perf['order_completion_rate']:.1%} completion rate), " \
                       f"{perf['active_shipments']} active shipments."
            else:
                return "No performance data available."
        
        else:
            return data.get("message", "I couldn't process your query. Please try asking about inventory, locations, orders, suppliers, capacity, employees, or performance.")

class ModelBasedReflexAgent(BaseAgent):
    """Model-based reflex agent that maintains an internal model of the world state"""
    
    def __init__(self, ontology: SupplyChainOntology):
        super().__init__(ontology, "ModelBasedReflexAgent")
        self.world_model = self._build_world_model()
        self.context_memory = []
    
    def _build_world_model(self) -> Dict[str, Any]:
        """Build internal model of the supply chain world"""
        model = {
            "locations": {},
            "products": {},
            "suppliers": {},
            "inventory_state": {},
            "order_patterns": {},
            "performance_trends": {},
            "relationships": {}
        }
        
        # Build location model
        for location in self.ontology.query_by_type("Location"):
            model["locations"][location.id] = {
                "name": location.name,
                "type": location.type.value,
                "capacity": location.capacity_m3,
                "utilization_history": [],
                "connected_locations": self._find_connected_locations(location.id)
            }
        
        # Build product model
        for product in self.ontology.query_by_type("Product"):
            model["products"][product.id] = {
                "name": product.name,
                "category": product.category,
                "demand_pattern": self._analyze_demand_pattern(product.id),
                "stock_levels": self._get_current_stock_levels(product.id)
            }
        
        # Build relationship model
        model["relationships"] = self.ontology.relationships
        
        return model
    
    def process_query(self, query: str) -> QueryResult:
        """Process query using internal world model and context"""
        start_time = datetime.now()
        self.clear_thoughts()
        
        # Update world model based on current state
        self._update_world_model()
        
        # Parse query with context awareness
        parsed = self._parse_query_with_context(query)
        
        self.add_thought(
            f"Analyzing query with world model context",
            f"Intent: {parsed['intent']}, Context: {parsed.get('context', 'none')}",
            f"Relevant entities: {parsed['entities']}",
            0.85
        )
        
        # Use world model to enhance query processing
        result_data = self._process_with_model(parsed)
        
        # Update context memory
        self.context_memory.append({
            "query": query,
            "intent": parsed["intent"],
            "timestamp": datetime.now(),
            "entities": parsed["entities"]
        })
        
        # Keep only recent context
        if len(self.context_memory) > 10:
            self.context_memory = self.context_memory[-10:]
        
        answer = self._generate_contextual_answer(parsed, result_data)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QueryResult(
            query=query,
            answer=answer,
            agent_type="ModelBasedReflexAgent",
            thoughts=self.thoughts.copy(),
            data=result_data,
            confidence=0.85,
            execution_time_ms=execution_time
        )
    
    def _parse_query_with_context(self, query: str) -> Dict[str, Any]:
        """Parse query considering conversation context"""
        parsed = self._parse_query_intent(query)
        
        # Add context from previous queries
        context = []
        for prev in self.context_memory[-3:]:  # Last 3 queries
            if any(entity in query.lower() for entities in prev["entities"].values() for entity in entities):
                context.append(prev)
        
        parsed["context"] = context
        return parsed
    
    def _update_world_model(self):
        """Update internal world model with current state"""
        # Update utilization for locations
        for location_id, location_info in self.world_model["locations"].items():
            current_utilization = self._calculate_current_utilization(location_id)
            location_info["utilization_history"].append({
                "timestamp": datetime.now(),
                "utilization": current_utilization
            })
            
            # Keep only recent history
            if len(location_info["utilization_history"]) > 100:
                location_info["utilization_history"] = location_info["utilization_history"][-100:]
    
    def _process_with_model(self, parsed: Dict) -> Dict:
        """Process query using world model insights"""
        intent = parsed["intent"]
        entities = parsed["entities"]
        
        if intent == "inventory_query":
            return self._model_based_inventory_query(entities)
        elif intent == "performance_query":
            return self._model_based_performance_query(entities)
        elif intent == "location_query":
            return self._model_based_location_query(entities)
        else:
            # Fall back to simple processing
            simple_agent = SimpleReflexAgent(self.ontology)
            return simple_agent._handle_general_query(entities, parsed["original_query"])
    
    def _model_based_inventory_query(self, entities: Dict) -> Dict:
        """Enhanced inventory query using world model"""
        self.add_thought(
            "Using world model for inventory analysis",
            "Analyzing stock patterns and trends",
            "Considering demand patterns and stock movement",
            0.9
        )
        
        inventory_analysis = {}
        
        # Get basic inventory data
        simple_agent = SimpleReflexAgent(self.ontology)
        basic_data = simple_agent._handle_inventory_query(entities, "")
        
        # Enhance with model insights
        for item in basic_data.get("inventory", []):
            product_id = None
            for pid, product_info in self.world_model["products"].items():
                if product_info["name"] == item["product"]:
                    product_id = pid
                    break
            
            if product_id:
                item["demand_pattern"] = self.world_model["products"][product_id]["demand_pattern"]
                item["stock_trend"] = self._analyze_stock_trend(product_id, item["location"])
                item["reorder_recommendation"] = self._get_reorder_recommendation(product_id, item["available"])
        
        return basic_data
    
    def _model_based_performance_query(self, entities: Dict) -> Dict:
        """Enhanced performance query using world model"""
        performance_data = {}
        
        # Location performance trends
        location_trends = {}
        for location_id, location_info in self.world_model["locations"].items():
            if location_info["utilization_history"]:
                recent_util = [u["utilization"] for u in location_info["utilization_history"][-10:]]
                avg_utilization = sum(recent_util) / len(recent_util)
                trend = "increasing" if recent_util[-1] > recent_util[0] else "decreasing"
                
                location_trends[location_info["name"]] = {
                    "avg_utilization": avg_utilization,
                    "trend": trend,
                    "efficiency_score": self._calculate_efficiency_score(location_id)
                }
        
        performance_data["location_trends"] = location_trends
        
        # Overall network performance
        performance_data["network_health"] = self._assess_network_health()
        
        return performance_data
    
    def _model_based_location_query(self, entities: Dict) -> Dict:
        """Enhanced location query using world model"""
        # Get basic location data
        simple_agent = SimpleReflexAgent(self.ontology)
        basic_data = simple_agent._handle_location_query(entities, "")
        
        # Enhance with connectivity and performance data
        for location in basic_data.get("locations", []):
            location_id = None
            for lid, loc_info in self.world_model["locations"].items():
                if loc_info["name"] == location["name"]:
                    location_id = lid
                    break
            
            if location_id:
                location["connected_locations"] = len(self.world_model["locations"][location_id]["connected_locations"])
                location["performance_score"] = self._calculate_efficiency_score(location_id)
        
        return basic_data
    
    def _find_connected_locations(self, location_id: str) -> List[str]:
        """Find locations connected through shipments"""
        connected = set()
        
        # Check shipment relationships
        for rel_type in ["origin", "destination"]:
            if rel_type in self.ontology.relationships:
                for relation in self.ontology.relationships[rel_type]:
                    if relation["source"] == location_id:
                        connected.add(relation["target"])
                    elif relation["target"] == location_id:
                        connected.add(relation["source"])
        
        return list(connected)
    
    def _analyze_demand_pattern(self, product_id: str) -> str:
        """Analyze demand pattern for a product"""
        # Simplified pattern analysis
        orders = self.ontology.query_by_type("Order")
        product_orders = [o for o in orders if product_id in o.product_quantities]
        
        if len(product_orders) > 10:
            return "high_demand"
        elif len(product_orders) > 5:
            return "medium_demand"
        else:
            return "low_demand"
    
    def _get_current_stock_levels(self, product_id: str) -> Dict:
        """Get current stock levels across all locations"""
        inventory_items = [inv for inv in self.ontology.query_by_type("Inventory") if inv.product_id == product_id]
        
        return {
            "total_stock": sum(inv.quantity for inv in inventory_items),
            "available_stock": sum(inv.quantity - inv.reserved_quantity for inv in inventory_items),
            "locations_count": len(inventory_items)
        }
    
    def _calculate_current_utilization(self, location_id: str) -> float:
        """Calculate current utilization for a location"""
        location = self.ontology.entities.get(location_id)
        if not location:
            return 0.0
        
        inventory_items = [inv for inv in self.ontology.query_by_type("Inventory") if inv.location_id == location_id]
        total_volume = 0
        
        for inv in inventory_items:
            product = self.ontology.entities.get(inv.product_id)
            if product:
                total_volume += product.volume_m3 * inv.quantity
        
        return min(total_volume / location.capacity_m3, 1.0) if location.capacity_m3 > 0 else 0.0
    
    def _analyze_stock_trend(self, product_id: str, location_name: str) -> str:
        """Analyze stock trend for a product at a location"""
        # Simplified trend analysis
        return "stable"  # In a real system, this would analyze historical data
    
    def _get_reorder_recommendation(self, product_id: str, available_quantity: int) -> str:
        """Get reorder recommendation based on stock levels and demand"""
        product = self.ontology.entities.get(product_id)
        if not product:
            return "no_data"
        
        if available_quantity < product.safety_stock_level * 0.5:
            return "urgent_reorder"
        elif available_quantity < product.safety_stock_level:
            return "reorder_soon"
        else:
            return "stock_ok"
    
    def _calculate_efficiency_score(self, location_id: str) -> float:
        """Calculate efficiency score for a location"""
        # Simplified efficiency calculation
        utilization = self._calculate_current_utilization(location_id)
        # Optimal utilization is around 80%
        if utilization <= 0.8:
            return utilization / 0.8
        else:
            return 1.0 - (utilization - 0.8) / 0.2
    
    def _assess_network_health(self) -> Dict:
        """Assess overall supply chain network health"""
        locations = self.ontology.query_by_type("Location")
        orders = self.ontology.query_by_type("Order")
        shipments = self.ontology.query_by_type("Shipment")
        
        # Calculate various health metrics
        avg_utilization = sum(self._calculate_current_utilization(loc.id) for loc in locations) / len(locations)
        order_fulfillment_rate = len([o for o in orders if o.status.value in ["shipped", "delivered"]]) / len(orders) if orders else 0
        on_time_delivery_rate = len([s for s in shipments if s.status.value == "delivered"]) / len(shipments) if shipments else 0
        
        overall_health = (avg_utilization + order_fulfillment_rate + on_time_delivery_rate) / 3
        
        return {
            "overall_health_score": overall_health,
            "avg_utilization": avg_utilization,
            "order_fulfillment_rate": order_fulfillment_rate,
            "on_time_delivery_rate": on_time_delivery_rate,
            "health_status": "excellent" if overall_health > 0.8 else "good" if overall_health > 0.6 else "needs_attention"
        }
    
    def _generate_contextual_answer(self, parsed: Dict, data: Dict) -> str:
        """Generate answer with contextual awareness"""
        intent = parsed["intent"]
        
        if intent == "inventory_query" and "inventory" in data:
            answer = f"Based on current supply chain analysis, found {len(data['inventory'])} inventory records. "
            
            # Add insights from world model
            urgent_reorders = [item for item in data["inventory"] if item.get("reorder_recommendation") == "urgent_reorder"]
            if urgent_reorders:
                answer += f"⚠️ {len(urgent_reorders)} items need urgent reordering: "
                answer += ", ".join([f"{item['product']} at {item['location']}" for item in urgent_reorders[:3]])
                if len(urgent_reorders) > 3:
                    answer += f" and {len(urgent_reorders) - 3} more."
            
            return answer
        
        elif intent == "performance_query" and "network_health" in data:
            health = data["network_health"]
            answer = f"Supply Chain Health Status: {health['health_status'].upper()} "
            answer += f"(Overall Score: {health['overall_health_score']:.1%}). "
            answer += f"Average utilization: {health['avg_utilization']:.1%}, "
            answer += f"Order fulfillment: {health['order_fulfillment_rate']:.1%}, "
            answer += f"On-time delivery: {health['on_time_delivery_rate']:.1%}."
            
            if "location_trends" in data:
                trending_up = [name for name, trend in data["location_trends"].items() if trend["trend"] == "increasing"]
                if trending_up:
                    answer += f" 📈 Locations with increasing utilization: {', '.join(trending_up[:3])}."
            
            return answer
        
        else:
            # Fall back to simple answer generation
            simple_agent = SimpleReflexAgent(self.ontology)
            return simple_agent._generate_answer(intent, data, parsed["entities"])

class GoalBasedAgent(BaseAgent):
    """Goal-based agent that makes decisions to achieve specific objectives"""
    
    def __init__(self, ontology: SupplyChainOntology):
        super().__init__(ontology, "GoalBasedAgent")
        self.goals = {
            "optimize_inventory": 0.9,
            "improve_delivery_time": 0.8,
            "reduce_costs": 0.7,
            "maximize_utilization": 0.6
        }
        self.action_history = []
    
    def process_query(self, query: str) -> QueryResult:
        """Process query by planning actions to achieve goals"""
        start_time = datetime.now()
        self.clear_thoughts()
        
        # Parse query and identify relevant goals
        parsed = self._parse_query_intent(query)
        relevant_goals = self._identify_relevant_goals(parsed)
        
        self.add_thought(
            f"Identified relevant goals: {relevant_goals}",
            "Planning actions to achieve goals",
            f"Query intent: {parsed['intent']}",
            0.8
        )
        
        # Plan actions to achieve goals
        action_plan = self._plan_actions(parsed, relevant_goals)
        
        self.add_thought(
            f"Generated action plan with {len(action_plan)} steps",
            "Executing planned actions",
            f"Actions: {[action['action'] for action in action_plan]}",
            0.85
        )
        
        # Execute action plan
        result_data = self._execute_action_plan(action_plan, parsed)
        
        # Evaluate goal achievement
        goal_achievement = self._evaluate_goal_achievement(relevant_goals, result_data)
        
        self.add_thought(
            f"Goal achievement evaluation: {goal_achievement}",
            "Generating goal-oriented response",
            f"Success rate: {sum(goal_achievement.values()) / len(goal_achievement) if goal_achievement else 0:.1%}",
            0.9
        )
        
        # Generate goal-oriented answer
        answer = self._generate_goal_oriented_answer(parsed, result_data, goal_achievement)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QueryResult(
            query=query,
            answer=answer,
            agent_type="GoalBasedAgent",
            thoughts=self.thoughts.copy(),
            data={**result_data, "goal_achievement": goal_achievement, "action_plan": action_plan},
            confidence=0.9,
            execution_time_ms=execution_time
        )
    
    def _identify_relevant_goals(self, parsed: Dict) -> List[str]:
        """Identify which goals are relevant to the query"""
        intent = parsed["intent"]
        relevant_goals = []
        
        if intent == "inventory_query":
            relevant_goals.extend(["optimize_inventory", "reduce_costs"])
        elif intent == "performance_query":
            relevant_goals.extend(["improve_delivery_time", "maximize_utilization"])
        elif intent == "order_status":
            relevant_goals.extend(["improve_delivery_time"])
        elif intent == "capacity_query":
            relevant_goals.extend(["maximize_utilization", "optimize_inventory"])
        
        return relevant_goals
    
    def _plan_actions(self, parsed: Dict, relevant_goals: List[str]) -> List[Dict]:
        """Plan actions to achieve the relevant goals"""
        action_plan = []
        
        # Base data gathering action
        action_plan.append({
            "action": "gather_base_data",
            "goal": "information_gathering",
            "priority": 1.0
        })
        
        if "optimize_inventory" in relevant_goals:
            action_plan.append({
                "action": "analyze_inventory_optimization",
                "goal": "optimize_inventory",
                "priority": 0.9
            })
        
        if "improve_delivery_time" in relevant_goals:
            action_plan.append({
                "action": "analyze_delivery_performance",
                "goal": "improve_delivery_time",
                "priority": 0.8
            })
        
        if "maximize_utilization" in relevant_goals:
            action_plan.append({
                "action": "analyze_capacity_utilization",
                "goal": "maximize_utilization",
                "priority": 0.7
            })
        
        if "reduce_costs" in relevant_goals:
            action_plan.append({
                "action": "identify_cost_savings",
                "goal": "reduce_costs",
                "priority": 0.6
            })
        
        # Sort by priority
        action_plan.sort(key=lambda x: x["priority"], reverse=True)
        
        return action_plan
    
    def _execute_action_plan(self, action_plan: List[Dict], parsed: Dict) -> Dict:
        """Execute the planned actions"""
        results = {}
        
        for action in action_plan:
            action_type = action["action"]
            
            if action_type == "gather_base_data":
                results["base_data"] = self._gather_base_data(parsed)
            
            elif action_type == "analyze_inventory_optimization":
                results["inventory_optimization"] = self._analyze_inventory_optimization()
            
            elif action_type == "analyze_delivery_performance":
                results["delivery_analysis"] = self._analyze_delivery_performance()
            
            elif action_type == "analyze_capacity_utilization":
                results["capacity_analysis"] = self._analyze_capacity_utilization()
            
            elif action_type == "identify_cost_savings":
                results["cost_analysis"] = self._identify_cost_savings()
        
        return results
    
    def _gather_base_data(self, parsed: Dict) -> Dict:
        """Gather base data using simple reflex agent"""
        simple_agent = SimpleReflexAgent(self.ontology)
        intent = parsed["intent"]
        entities = parsed["entities"]
        
        if intent == "inventory_query":
            return simple_agent._handle_inventory_query(entities, "")
        elif intent == "performance_query":
            return simple_agent._handle_performance_query(entities, "")
        elif intent == "order_status":
            return simple_agent._handle_order_status(entities, "")
        elif intent == "capacity_query":
            return simple_agent._handle_capacity_query(entities, "")
        else:
            return simple_agent._handle_general_query(entities, "")
    
    def _analyze_inventory_optimization(self) -> Dict:
        """Analyze inventory for optimization opportunities"""
        inventory_items = self.ontology.query_by_type("Inventory")
        optimization_opportunities = []
        
        for inv in inventory_items:
            product = self.ontology.entities.get(inv.product_id)
            location = self.ontology.entities.get(inv.location_id)
            
            if product and location:
                # Check for overstocking
                if inv.quantity > product.safety_stock_level * 3:
                    optimization_opportunities.append({
                        "type": "overstock",
                        "product": product.name,
                        "location": location.name,
                        "current_stock": inv.quantity,
                        "recommended_stock": product.safety_stock_level * 2,
                        "potential_savings": (inv.quantity - product.safety_stock_level * 2) * product.cost_usd
                    })
                
                # Check for understocking
                elif inv.quantity < product.safety_stock_level * 0.5:
                    optimization_opportunities.append({
                        "type": "understock",
                        "product": product.name,
                        "location": location.name,
                        "current_stock": inv.quantity,
                        "recommended_stock": product.safety_stock_level,
                        "risk_level": "high"
                    })
        
        return {
            "opportunities": optimization_opportunities,
            "total_potential_savings": sum(opp.get("potential_savings", 0) for opp in optimization_opportunities)
        }
    
    def _analyze_delivery_performance(self) -> Dict:
        """Analyze delivery performance for improvement opportunities"""
        shipments = self.ontology.query_by_type("Shipment")
        
        on_time_deliveries = 0
        late_deliveries = 0
        total_delay_hours = 0
        
        for shipment in shipments:
            if shipment.actual_arrival and shipment.scheduled_arrival:
                delay = (shipment.actual_arrival - shipment.scheduled_arrival).total_seconds() / 3600
                if delay <= 0:
                    on_time_deliveries += 1
                else:
                    late_deliveries += 1
                    total_delay_hours += delay
        
        total_shipments = on_time_deliveries + late_deliveries
        on_time_rate = on_time_deliveries / total_shipments if total_shipments > 0 else 0
        avg_delay_hours = total_delay_hours / late_deliveries if late_deliveries > 0 else 0
        
        return {
            "on_time_rate": on_time_rate,
            "avg_delay_hours": avg_delay_hours,
            "improvement_target": max(0.95, on_time_rate + 0.1),
            "performance_grade": "A" if on_time_rate > 0.9 else "B" if on_time_rate > 0.8 else "C"
        }
    
    def _analyze_capacity_utilization(self) -> Dict:
        """Analyze capacity utilization for optimization"""
        locations = self.ontology.query_by_type("Location")
        utilization_analysis = []
        
        for location in locations:
            if location.type.value in ["warehouse", "distribution_center"]:
                current_utilization = self._calculate_current_utilization(location.id)
                
                if current_utilization < 0.5:
                    recommendation = "underutilized"
                    action = "consider_consolidation"
                elif current_utilization > 0.9:
                    recommendation = "overutilized"
                    action = "expand_capacity"
                else:
                    recommendation = "optimal"
                    action = "maintain_current"
                
                utilization_analysis.append({
                    "location": location.name,
                    "utilization": current_utilization,
                    "recommendation": recommendation,
                    "suggested_action": action
                })
        
        return {
            "location_analysis": utilization_analysis,
            "avg_utilization": sum(loc["utilization"] for loc in utilization_analysis) / len(utilization_analysis) if utilization_analysis else 0
        }
    
    def _identify_cost_savings(self) -> Dict:
        """Identify potential cost savings opportunities"""
        cost_savings = []
        
        # Analyze supplier costs
        suppliers = self.ontology.query_by_type("Supplier")
        for supplier in suppliers:
            if supplier.reliability_score < 0.8:
                cost_savings.append({
                    "type": "supplier_optimization",
                    "description": f"Consider replacing low-reliability supplier {supplier.name}",
                    "potential_savings": "5-15% of supplier costs"
                })
        
        # Analyze transportation efficiency
        vehicles = self.ontology.query_by_type("Vehicle")
        underutilized_vehicles = len([v for v in vehicles if self._calculate_vehicle_utilization(v.id) < 0.6])
        
        if underutilized_vehicles > 0:
            cost_savings.append({
                "type": "transportation_optimization",
                "description": f"Optimize routes for {underutilized_vehicles} underutilized vehicles",
                "potential_savings": f"${underutilized_vehicles * 50000} annually"
            })
        
        return {"opportunities": cost_savings}
    
    def _calculate_current_utilization(self, location_id: str) -> float:
        """Calculate current utilization for a location"""
        location = self.ontology.entities.get(location_id)
        if not location:
            return 0.0
        
        inventory_items = [inv for inv in self.ontology.query_by_type("Inventory") if inv.location_id == location_id]
        total_volume = 0
        
        for inv in inventory_items:
            product = self.ontology.entities.get(inv.product_id)
            if product:
                total_volume += product.volume_m3 * inv.quantity
        
        return min(total_volume / location.capacity_m3, 1.0) if location.capacity_m3 > 0 else 0.0
    
    def _calculate_vehicle_utilization(self, vehicle_id: str) -> float:
        """Calculate vehicle utilization (simplified)"""
        # In a real system, this would analyze actual vs. capacity usage
        return 0.7 # Placeholder
    
    def _evaluate_goal_achievement(self, relevant_goals: List[str], result_data: Dict) -> Dict[str, float]:
        """Evaluate how well the goals were achieved"""
        achievement = {}
        
        for goal in relevant_goals:
            if goal == "optimize_inventory" and "inventory_optimization" in result_data:
                # Success if we found optimization opportunities
                opportunities = len(result_data["inventory_optimization"].get("opportunities", []))
                achievement[goal] = min(1.0, opportunities / 10)  # Scale based on opportunities found
            
            elif goal == "improve_delivery_time" and "delivery_analysis" in result_data:
                # Success based on current performance
                on_time_rate = result_data["delivery_analysis"].get("on_time_rate", 0)
                achievement[goal] = on_time_rate
            
            elif goal == "maximize_utilization" and "capacity_analysis" in result_data:
                # Success based on utilization analysis
                avg_util = result_data["capacity_analysis"].get("avg_utilization", 0)
                # Optimal utilization is around 0.8
                achievement[goal] = 1.0 - abs(avg_util - 0.8) / 0.8
            
            elif goal == "reduce_costs" and "cost_analysis" in result_data:
                # Success if we found cost saving opportunities
                opportunities = len(result_data["cost_analysis"].get("opportunities", []))
                achievement[goal] = min(1.0, opportunities / 5)
            
            else:
                achievement[goal] = 0.5  # Default partial success
        
        return achievement
    
    def _generate_goal_oriented_answer(self, parsed: Dict, result_data: Dict, goal_achievement: Dict) -> str:
        """Generate answer focused on goal achievement"""
        answer = ""
        
        # Start with base information
        if "base_data" in result_data:
            base_data = result_data["base_data"]
            if parsed["intent"] == "inventory_query" and "inventory" in base_data:
                answer += f"Found {len(base_data['inventory'])} inventory records. "
        
        # Add goal-oriented insights
        if "inventory_optimization" in result_data:
            opt_data = result_data["inventory_optimization"]
            opportunities = opt_data.get("opportunities", [])
            if opportunities:
                overstocks = [opp for opp in opportunities if opp["type"] == "overstock"]
                understocks = [opp for opp in opportunities if opp["type"] == "understock"]
                
                answer += f"🎯 INVENTORY OPTIMIZATION: Found {len(overstocks)} overstocking and {len(understocks)} understocking situations. "
                if opt_data.get("total_potential_savings", 0) > 0:
                    answer += f"Potential savings: ${opt_data['total_potential_savings']:,.2f}. "
        
        if "delivery_analysis" in result_data:
            delivery_data = result_data["delivery_analysis"]
            answer += f"🚚 DELIVERY PERFORMANCE: {delivery_data.get('on_time_rate', 0):.1%} on-time rate "
            answer += f"(Grade: {delivery_data.get('performance_grade', 'N/A')}). "
            if delivery_data.get("avg_delay_hours", 0) > 0:
                answer += f"Average delay: {delivery_data['avg_delay_hours']:.1f} hours. "
        
        if "capacity_analysis" in result_data:
            capacity_data = result_data["capacity_analysis"]
            answer += f"📊 CAPACITY UTILIZATION: {capacity_data.get('avg_utilization', 0):.1%} average utilization. "
            
            underutilized = [loc for loc in capacity_data.get("location_analysis", []) if loc["recommendation"] == "underutilized"]
            overutilized = [loc for loc in capacity_data.get("location_analysis", []) if loc["recommendation"] == "overutilized"]
            
            if underutilized:
                answer += f"{len(underutilized)} locations underutilized. "
            if overutilized:
                answer += f"{len(overutilized)} locations need capacity expansion. "
        
        if "cost_analysis" in result_data:
            cost_data = result_data["cost_analysis"]
            opportunities = cost_data.get("opportunities", [])
            if opportunities:
                answer += f"💰 COST SAVINGS: {len(opportunities)} optimization opportunities identified. "
        
        # Add goal achievement summary
        if goal_achievement:
            avg_achievement = sum(goal_achievement.values()) / len(goal_achievement)
            answer += f"\n📈 Goal Achievement: {avg_achievement:.1%} overall success rate."
        
        return answer

# Agent Factory
class AgentFactory:
    """Factory for creating different types of agents"""
    
    @staticmethod
    def create_agent(agent_type: str, ontology: SupplyChainOntology) -> BaseAgent:
        """Create an agent of the specified type"""
        if agent_type == "simple_reflex":
            return SimpleReflexAgent(ontology)
        elif agent_type == "model_based_reflex":
            return ModelBasedReflexAgent(ontology)
        elif agent_type == "goal_based":
            return GoalBasedAgent(ontology)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    @staticmethod
    def get_available_agents() -> List[str]:
        """Get list of available agent types"""
        return ["simple_reflex", "model_based_reflex", "goal_based"]

# Example usage
if __name__ == "__main__":
    # This would typically be loaded from the generated data
    from sample_data_generator import SupplyChainDataGenerator
    
    # Generate sample data
    generator = SupplyChainDataGenerator()
    ontology = generator.generate_complete_dataset(scale_factor=0.5)  # Smaller dataset for testing
    
    # Test different agents
    agents = [
        AgentFactory.create_agent("simple_reflex", ontology),
        AgentFactory.create_agent("model_based_reflex", ontology),
        AgentFactory.create_agent("goal_based", ontology)
    ]
    
    test_queries = [
        "How many items are there in Walmart Supercenter #1 and what are the inventory levels?",
        "What is the performance of our supply chain network?",
        "Which locations have the highest capacity utilization?",
        "What are the current order statuses and delivery performance?"
    ]
    
    print("=== AI AGENT TESTING ===\n")
    
    for query in test_queries:
        print(f"Query: {query}")
        print("-" * 80)
        
        for agent in agents:
            result = agent.process_query(query)
            print(f"\n{agent.name}:")
            print(f"Answer: {result.answer}")
            print(f"Confidence: {result.confidence:.1%}")
            print(f"Execution Time: {result.execution_time_ms:.1f}ms")
            print(f"Thoughts: {len(result.thoughts)} reasoning steps")
            
        print("\n" + "="*80 + "\n")