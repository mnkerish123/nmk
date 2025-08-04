"""
Sample Data Generator for Walmart-Scale Supply Chain
Generates realistic sample data for testing and demonstration
"""

import random
from datetime import datetime, timedelta
from supply_chain_ontology import *
import json

class SupplyChainDataGenerator:
    """Generate comprehensive sample data for supply chain operations"""
    
    def __init__(self):
        self.ontology = SupplyChainOntology()
        
        # Sample data pools
        self.product_names = [
            "Great Value Milk", "Equate Pain Reliever", "Mainstays Towels", 
            "Sam's Choice Cola", "Faded Glory Jeans", "Ozark Trail Tent",
            "Marketside Salad", "Parent's Choice Diapers", "Equate Vitamins",
            "Great Value Bread", "Mainstays Bedding", "Time and Tru Dress",
            "Spark Energy Drink", "Freshness Guaranteed Cookies", "Hyper Tough Tools",
            "Better Homes Garden Decor", "No Boundaries Shirt", "Athletic Works Shoes",
            "Onn Electronics", "Pen+Gear Supplies", "Blackstone Grill", "Ozark Trail Cooler"
        ]
        
        self.categories = [
            "Groceries", "Health & Wellness", "Home & Garden", "Electronics", 
            "Clothing", "Sports & Outdoors", "Baby & Kids", "Automotive"
        ]
        
        self.locations_data = [
            # Distribution Centers
            ("Bentonville DC", LocationType.DISTRIBUTION_CENTER, "Bentonville, AR", 36.3729, -94.2088),
            ("Dallas DC", LocationType.DISTRIBUTION_CENTER, "Dallas, TX", 32.7767, -96.7970),
            ("Atlanta DC", LocationType.DISTRIBUTION_CENTER, "Atlanta, GA", 33.7490, -84.3880),
            ("Los Angeles DC", LocationType.DISTRIBUTION_CENTER, "Los Angeles, CA", 34.0522, -118.2437),
            ("Chicago DC", LocationType.DISTRIBUTION_CENTER, "Chicago, IL", 41.8781, -87.6298),
            
            # Warehouses
            ("Memphis Warehouse", LocationType.WAREHOUSE, "Memphis, TN", 35.1495, -90.0490),
            ("Phoenix Warehouse", LocationType.WAREHOUSE, "Phoenix, AZ", 33.4484, -112.0740),
            ("Denver Warehouse", LocationType.WAREHOUSE, "Denver, CO", 39.7392, -104.9903),
            
            # Factories
            ("Arkansas Food Processing", LocationType.FACTORY, "Springdale, AR", 36.1867, -94.1288),
            ("Texas Electronics Factory", LocationType.FACTORY, "Austin, TX", 30.2672, -97.7431),
            ("California Textile Mill", LocationType.FACTORY, "Fresno, CA", 36.7378, -119.7871),
            
            # Retail Stores
            ("Walmart Supercenter #1", LocationType.RETAIL_STORE, "Rogers, AR", 36.3320, -94.1185),
            ("Walmart Supercenter #2", LocationType.RETAIL_STORE, "Plano, TX", 33.0198, -96.6989),
            ("Walmart Supercenter #3", LocationType.RETAIL_STORE, "Marietta, GA", 33.9526, -84.5499),
            ("Walmart Supercenter #4", LocationType.RETAIL_STORE, "Torrance, CA", 33.8358, -118.3406),
            ("Walmart Supercenter #5", LocationType.RETAIL_STORE, "Schaumburg, IL", 42.0334, -88.0834),
            
            # Ports
            ("Port of Long Beach", LocationType.PORT, "Long Beach, CA", 33.7701, -118.1937),
            ("Port of Houston", LocationType.PORT, "Houston, TX", 29.7604, -95.3698),
        ]
        
        self.supplier_names = [
            "Procter & Gamble", "Unilever", "Nestle USA", "PepsiCo", "Coca-Cola",
            "Johnson & Johnson", "Kimberly-Clark", "General Mills", "Kraft Heinz",
            "Tyson Foods", "ConAgra Foods", "Campbell Soup", "Kellogg Company",
            "Mars Inc", "Mondelez International", "Hershey Company"
        ]
        
        self.customer_names = [
            "Regional Grocery Chain", "Local Restaurant Group", "School District",
            "Hospital Network", "Hotel Chain", "Corporate Cafeteria Services",
            "Emergency Services", "Military Base Supply", "University System",
            "Retail Franchise Group"
        ]
        
        self.employee_names = [
            "John Smith", "Maria Garcia", "David Johnson", "Sarah Williams", "Michael Brown",
            "Jennifer Davis", "Robert Miller", "Lisa Wilson", "James Moore", "Jessica Taylor",
            "Christopher Anderson", "Amanda Thomas", "Matthew Jackson", "Ashley White", "Daniel Harris"
        ]
    
    def generate_complete_dataset(self, scale_factor: float = 1.0):
        """Generate a complete dataset scaled by the given factor"""
        
        # Scale quantities based on factor
        num_products = int(50 * scale_factor)
        num_suppliers = int(16 * scale_factor)
        num_customers = int(25 * scale_factor)
        num_employees = int(60 * scale_factor)
        num_vehicles = int(30 * scale_factor)
        num_machines = int(20 * scale_factor)
        num_orders = int(100 * scale_factor)
        
        print(f"Generating supply chain data (scale: {scale_factor}x)")
        print(f"- Products: {num_products}")
        print(f"- Suppliers: {num_suppliers}")
        print(f"- Customers: {num_customers}")
        print(f"- Employees: {num_employees}")
        print(f"- Vehicles: {num_vehicles}")
        print(f"- Orders: {num_orders}")
        
        # Generate core entities
        locations = self._generate_locations()
        products = self._generate_products(num_products, locations)
        suppliers = self._generate_suppliers(num_suppliers, locations, products)
        customers = self._generate_customers(num_customers, locations)
        employees = self._generate_employees(num_employees, locations)
        vehicles = self._generate_vehicles(num_vehicles, locations, employees)
        machines = self._generate_machines(num_machines, locations)
        
        # Generate operational entities
        inventory = self._generate_inventory(products, locations)
        orders = self._generate_orders(num_orders, customers, products)
        shipments = self._generate_shipments(orders, locations, vehicles)
        
        # Establish relationships in ontology
        self._establish_relationships(suppliers, products, customers, orders, 
                                    inventory, shipments, employees, locations, vehicles, machines)
        
        return self.ontology
    
    def _generate_locations(self):
        """Generate location entities"""
        locations = []
        for name, loc_type, address, lat, lon in self.locations_data:
            location = Location(
                name=name,
                type=loc_type,
                address=address,
                latitude=lat,
                longitude=lon,
                capacity_m3=random.uniform(10000, 100000) if loc_type != LocationType.RETAIL_STORE else random.uniform(1000, 5000),
                operational_hours="24/7" if loc_type in [LocationType.WAREHOUSE, LocationType.DISTRIBUTION_CENTER] else "6AM-11PM",
                temperature_zone=random.choice(["ambient", "refrigerated", "frozen"]) if random.random() < 0.3 else "ambient"
            )
            locations.append(location)
            self.ontology.add_entity(location)
        
        print(f"Generated {len(locations)} locations")
        return locations
    
    def _generate_products(self, num_products, locations):
        """Generate product entities"""
        products = []
        
        for i in range(num_products):
            product = Product(
                sku=f"WM{random.randint(100000, 999999)}",
                name=random.choice(self.product_names) + f" {random.choice(['XL', 'Regular', 'Mini', 'Family Size', 'Travel Size'])}",
                category=random.choice(self.categories),
                weight_kg=round(random.uniform(0.1, 50.0), 2),
                volume_m3=round(random.uniform(0.001, 2.0), 3),
                cost_usd=round(random.uniform(1.0, 500.0), 2),
                safety_stock_level=random.randint(50, 1000),
                lead_time_days=random.randint(1, 30)
            )
            
            # Add semantic tags based on category
            if product.category == "Groceries":
                product.semantic_tags.update(["food", "consumable", "perishable"])
            elif product.category == "Electronics":
                product.semantic_tags.update(["technology", "durable", "warranty"])
            elif product.category == "Clothing":
                product.semantic_tags.update(["apparel", "seasonal", "fashion"])
            
            products.append(product)
            self.ontology.add_entity(product)
        
        print(f"Generated {len(products)} products")
        return products
    
    def _generate_suppliers(self, num_suppliers, locations, products):
        """Generate supplier entities"""
        suppliers = []
        
        for i in range(min(num_suppliers, len(self.supplier_names))):
            supplier = Supplier(
                name=self.supplier_names[i],
                contact_info=f"supplier{i}@company.com",
                location_id=random.choice([loc for loc in locations if loc.type == LocationType.FACTORY]).id,
                reliability_score=round(random.uniform(0.7, 1.0), 2)
            )
            
            # Assign random products to supplier
            num_products_supplied = random.randint(1, min(8, len(products)))
            supplier.product_ids = [random.choice(products).id for _ in range(num_products_supplied)]
            
            suppliers.append(supplier)
            self.ontology.add_entity(supplier)
        
        print(f"Generated {len(suppliers)} suppliers")
        return suppliers
    
    def _generate_customers(self, num_customers, locations):
        """Generate customer entities"""
        customers = []
        
        for i in range(min(num_customers, len(self.customer_names) * 3)):
            customer = Customer(
                name=self.customer_names[i % len(self.customer_names)] + f" #{i//len(self.customer_names) + 1}",
                type=random.choice(["retail", "wholesale", "business"]),
                contact_info=f"customer{i}@business.com",
                location_id=random.choice(locations).id
            )
            
            customers.append(customer)
            self.ontology.add_entity(customer)
        
        print(f"Generated {len(customers)} customers")
        return customers
    
    def _generate_employees(self, num_employees, locations):
        """Generate employee entities"""
        employees = []
        
        for i in range(num_employees):
            employee = Employee(
                name=random.choice(self.employee_names) + f" {chr(65 + i % 26)}",
                role=random.choice(list(EmployeeRole)),
                location_id=random.choice(locations).id,
                contact_info=f"employee{i}@walmart.com"
            )
            
            employees.append(employee)
            self.ontology.add_entity(employee)
        
        # Assign managers to locations
        for location in locations:
            managers = [emp for emp in employees if emp.role == EmployeeRole.MANAGER and emp.location_id == location.id]
            if managers:
                location.manager_id = managers[0].id
        
        print(f"Generated {len(employees)} employees")
        return employees
    
    def _generate_vehicles(self, num_vehicles, locations, employees):
        """Generate vehicle entities"""
        vehicles = []
        
        for i in range(num_vehicles):
            vehicle_type = random.choice(list(VehicleType))
            
            # Set capacity based on vehicle type
            if vehicle_type == VehicleType.TRUCK:
                capacity = random.uniform(50, 100)
                max_weight = random.uniform(20000, 40000)
            elif vehicle_type == VehicleType.SHIP:
                capacity = random.uniform(10000, 50000)
                max_weight = random.uniform(100000, 500000)
            elif vehicle_type == VehicleType.PLANE:
                capacity = random.uniform(500, 2000)
                max_weight = random.uniform(50000, 200000)
            else:  # TRAIN
                capacity = random.uniform(2000, 10000)
                max_weight = random.uniform(100000, 300000)
            
            vehicle = Vehicle(
                type=vehicle_type,
                capacity_m3=capacity,
                max_weight_kg=max_weight,
                current_location_id=random.choice(locations).id
            )
            
            # Assign driver
            drivers = [emp for emp in employees if emp.role == EmployeeRole.DRIVER]
            if drivers:
                vehicle.driver_id = random.choice(drivers).id
            
            vehicles.append(vehicle)
            self.ontology.add_entity(vehicle)
        
        print(f"Generated {len(vehicles)} vehicles")
        return vehicles
    
    def _generate_machines(self, num_machines, locations):
        """Generate machine entities"""
        machines = []
        machine_types = ["conveyor_belt", "packaging_robot", "sorting_machine", "forklift", "crane", "scanner"]
        
        for i in range(num_machines):
            machine = Machine(
                name=f"{random.choice(machine_types).replace('_', ' ').title()} #{i+1}",
                type=random.choice(machine_types),
                location_id=random.choice([loc for loc in locations if loc.type in [LocationType.WAREHOUSE, LocationType.FACTORY, LocationType.DISTRIBUTION_CENTER]]).id,
                capacity_per_hour=random.uniform(100, 2000),
                operational_status=random.choice(["operational", "operational", "operational", "maintenance", "broken"])  # Weighted towards operational
            )
            
            machines.append(machine)
            self.ontology.add_entity(machine)
        
        print(f"Generated {len(machines)} machines")
        return machines
    
    def _generate_inventory(self, products, locations):
        """Generate inventory entities"""
        inventory_items = []
        
        # Generate inventory for warehouses, distribution centers, and stores
        storage_locations = [loc for loc in locations if loc.type in [LocationType.WAREHOUSE, LocationType.DISTRIBUTION_CENTER, LocationType.RETAIL_STORE]]
        
        for location in storage_locations:
            # Each location has 60-80% of all products
            num_products_in_location = int(len(products) * random.uniform(0.6, 0.8))
            products_in_location = random.sample(products, num_products_in_location)
            
            for product in products_in_location:
                base_quantity = product.safety_stock_level * random.uniform(0.5, 3.0)
                
                # Adjust quantity based on location type
                if location.type == LocationType.DISTRIBUTION_CENTER:
                    quantity = int(base_quantity * random.uniform(5, 15))
                elif location.type == LocationType.WAREHOUSE:
                    quantity = int(base_quantity * random.uniform(2, 8))
                else:  # Retail store
                    quantity = int(base_quantity * random.uniform(0.5, 2))
                
                inventory = Inventory(
                    product_id=product.id,
                    location_id=location.id,
                    quantity=quantity,
                    reserved_quantity=int(quantity * random.uniform(0, 0.3)),
                    last_updated=datetime.now() - timedelta(hours=random.randint(0, 72))
                )
                
                inventory_items.append(inventory)
                self.ontology.add_entity(inventory)
        
        print(f"Generated {len(inventory_items)} inventory records")
        return inventory_items
    
    def _generate_orders(self, num_orders, customers, products):
        """Generate order entities"""
        orders = []
        
        for i in range(num_orders):
            order = Order(
                customer_id=random.choice(customers).id,
                order_date=datetime.now() - timedelta(days=random.randint(0, 30)),
                requested_delivery_date=datetime.now() + timedelta(days=random.randint(1, 14)),
                status=random.choice(list(OrderStatus))
            )
            
            # Add products to order
            num_products_in_order = random.randint(1, 8)
            selected_products = random.sample(products, num_products_in_order)
            
            total_value = 0
            for product in selected_products:
                quantity = random.randint(1, 20)
                order.product_quantities[product.id] = quantity
                total_value += product.cost_usd * quantity
            
            order.total_value_usd = round(total_value, 2)
            
            orders.append(order)
            self.ontology.add_entity(order)
        
        print(f"Generated {len(orders)} orders")
        return orders
    
    def _generate_shipments(self, orders, locations, vehicles):
        """Generate shipment entities"""
        shipments = []
        
        # Generate shipments for orders that are shipped or delivered
        shipped_orders = [order for order in orders if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]]
        
        for order in shipped_orders:
            shipment = Shipment(
                order_id=order.id,
                origin_location_id=random.choice([loc for loc in locations if loc.type in [LocationType.WAREHOUSE, LocationType.DISTRIBUTION_CENTER]]).id,
                destination_location_id=random.choice([loc for loc in locations if loc.type == LocationType.RETAIL_STORE]).id,
                vehicle_id=random.choice(vehicles).id,
                product_quantities=order.product_quantities,
                scheduled_departure=order.order_date + timedelta(days=random.randint(1, 3)),
                scheduled_arrival=order.requested_delivery_date,
                status=ShipmentStatus.DELIVERED if order.status == OrderStatus.DELIVERED else random.choice(list(ShipmentStatus))
            )
            
            # Set actual times for completed shipments
            if shipment.status == ShipmentStatus.DELIVERED:
                shipment.actual_departure = shipment.scheduled_departure + timedelta(hours=random.randint(-2, 4))
                shipment.actual_arrival = shipment.scheduled_arrival + timedelta(hours=random.randint(-12, 24))
            
            shipments.append(shipment)
            self.ontology.add_entity(shipment)
        
        print(f"Generated {len(shipments)} shipments")
        return shipments
    
    def _establish_relationships(self, suppliers, products, customers, orders, inventory, shipments, employees, locations, vehicles, machines):
        """Establish all relationships in the ontology"""
        
        # Supplier -> Product relationships
        for supplier in suppliers:
            for product_id in supplier.product_ids:
                self.ontology.add_relationship("supplies", supplier.id, product_id)
        
        # Order -> Product relationships
        for order in orders:
            for product_id in order.product_quantities:
                self.ontology.add_relationship("contains", order.id, product_id, 
                                             {"quantity": order.product_quantities[product_id]})
        
        # Location -> Inventory -> Product relationships
        for inv in inventory:
            self.ontology.add_relationship("stores", inv.location_id, inv.product_id, 
                                         {"quantity": inv.quantity, "available": inv.quantity - inv.reserved_quantity})
        
        # Shipment -> Order relationships
        for shipment in shipments:
            self.ontology.add_relationship("fulfills", shipment.id, shipment.order_id)
        
        # Employee -> Location relationships
        for employee in employees:
            self.ontology.add_relationship("works_at", employee.id, employee.location_id)
        
        # Vehicle -> Location relationships
        for vehicle in vehicles:
            if vehicle.current_location_id:
                self.ontology.add_relationship("located_at", vehicle.id, vehicle.current_location_id)
        
        # Machine -> Location relationships
        for machine in machines:
            self.ontology.add_relationship("located_at", machine.id, machine.location_id)
        
        # Employee -> Location management relationships
        for location in locations:
            if location.manager_id:
                self.ontology.add_relationship("manages", location.manager_id, location.id)
        
        # Employee -> Vehicle operation relationships
        for vehicle in vehicles:
            if vehicle.driver_id:
                self.ontology.add_relationship("operates", vehicle.driver_id, vehicle.id)
        
        print("Established all ontology relationships")
    
    def save_to_files(self, base_filename="walmart_supply_chain"):
        """Save the generated data to JSON files"""
        
        # Save complete ontology
        ontology_data = self.ontology.export_full_ontology()
        with open(f"{base_filename}_ontology.json", "w") as f:
            json.dump(ontology_data, f, indent=2, default=str)
        
        # Save entities by type for easier access
        entities_by_type = {}
        for entity in self.ontology.entities.values():
            entity_type = entity.ontology_class
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity.to_ontology_dict())
        
        with open(f"{base_filename}_entities.json", "w") as f:
            json.dump(entities_by_type, f, indent=2, default=str)
        
        # Save relationships separately
        with open(f"{base_filename}_relationships.json", "w") as f:
            json.dump(self.ontology.relationships, f, indent=2, default=str)
        
        print(f"Saved data to {base_filename}_*.json files")
        
        return {
            "ontology_file": f"{base_filename}_ontology.json",
            "entities_file": f"{base_filename}_entities.json", 
            "relationships_file": f"{base_filename}_relationships.json"
        }

# Example usage and testing
if __name__ == "__main__":
    generator = SupplyChainDataGenerator()
    ontology = generator.generate_complete_dataset(scale_factor=1.0)
    
    # Save data
    files = generator.save_to_files()
    
    # Print summary statistics
    print("\n=== ONTOLOGY SUMMARY ===")
    print(f"Total entities: {len(ontology.entities)}")
    
    entity_counts = {}
    for entity in ontology.entities.values():
        entity_type = entity.ontology_class
        entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
    
    for entity_type, count in sorted(entity_counts.items()):
        print(f"- {entity_type}: {count}")
    
    print(f"\nTotal relationships: {sum(len(relations) for relations in ontology.relationships.values())}")
    for rel_type, relations in ontology.relationships.items():
        if relations:
            print(f"- {rel_type}: {len(relations)}")
    
    print(f"\nFiles created: {', '.join(files.values())}")