"""
Flask Web Server for Supply Chain Management System
Integrates ontology, sample data generation, and AI agents with the frontend
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import time
from datetime import datetime
import logging

# Import our custom modules
from supply_chain_ontology import SupplyChainOntology
from sample_data_generator import SupplyChainDataGenerator
from ai_agents import AgentFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables for caching
ontology = None
generator = None
agents = {}

def initialize_system():
    """Initialize the supply chain system with sample data"""
    global ontology, generator, agents
    
    logger.info("Initializing Supply Chain Management System...")
    
    # Generate sample data
    generator = SupplyChainDataGenerator()
    ontology = generator.generate_complete_dataset(scale_factor=1.0)
    
    # Save data to files
    files = generator.save_to_files()
    logger.info(f"Generated data files: {files}")
    
    # Initialize AI agents
    agent_types = AgentFactory.get_available_agents()
    for agent_type in agent_types:
        agents[agent_type] = AgentFactory.create_agent(agent_type, ontology)
        logger.info(f"Initialized {agent_type} agent")
    
    logger.info("System initialization complete!")

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/initialize', methods=['POST'])
def api_initialize():
    """Initialize or reinitialize the system"""
    try:
        initialize_system()
        return jsonify({
            'success': True,
            'message': 'System initialized successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/data/network', methods=['GET'])
def api_network_data():
    """Get network visualization data"""
    try:
        if not ontology:
            return jsonify({'error': 'System not initialized'}), 400
        
        # Get locations
        locations = []
        location_entities = ontology.query_by_type("Location")
        
        for location in location_entities:
            # Calculate current utilization
            utilization = calculate_location_utilization(location.id)
            
            locations.append({
                'id': location.id,
                'name': location.name,
                'type': location.type.value,
                'lat': location.latitude,
                'lon': location.longitude,
                'capacity': location.capacity_m3,
                'utilization': utilization,
                'address': location.address,
                'operational_hours': location.operational_hours
            })
        
        # Get connections (based on shipments)
        connections = []
        shipments = ontology.query_by_type("Shipment")
        
        # Aggregate flows between locations
        flow_map = {}
        for shipment in shipments:
            key = f"{shipment.origin_location_id}->{shipment.destination_location_id}"
            if key not in flow_map:
                flow_map[key] = 0
            
            # Calculate flow based on product quantities
            total_quantity = sum(shipment.product_quantities.values())
            flow_map[key] += total_quantity
        
        for flow_key, flow_value in flow_map.items():
            source_id, target_id = flow_key.split('->')
            connections.append({
                'source': source_id,
                'target': target_id,
                'flow': flow_value
            })
        
        return jsonify({
            'locations': locations,
            'connections': connections
        })
        
    except Exception as e:
        logger.error(f"Network data error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/metrics', methods=['GET'])
def api_metrics_data():
    """Get key performance metrics"""
    try:
        if not ontology:
            return jsonify({'error': 'System not initialized'}), 400
        
        # Calculate metrics
        locations = ontology.query_by_type("Location")
        orders = ontology.query_by_type("Order")
        shipments = ontology.query_by_type("Shipment")
        inventory_items = ontology.query_by_type("Inventory")
        
        completed_orders = len([o for o in orders if o.status.value in ["delivered"]])
        active_shipments = len([s for s in shipments if s.status.value in ["in_transit", "scheduled"]])
        
        # Calculate average utilization
        total_utilization = 0
        utilization_count = 0
        for location in locations:
            if location.type.value in ["warehouse", "distribution_center", "retail_store"]:
                util = calculate_location_utilization(location.id)
                total_utilization += util
                utilization_count += 1
        
        avg_utilization = total_utilization / utilization_count if utilization_count > 0 else 0
        
        # Calculate on-time delivery rate
        delivered_shipments = [s for s in shipments if s.actual_arrival and s.scheduled_arrival]
        on_time_deliveries = len([
            s for s in delivered_shipments 
            if s.actual_arrival <= s.scheduled_arrival
        ])
        on_time_rate = on_time_deliveries / len(delivered_shipments) if delivered_shipments else 0
        
        # Calculate total inventory value
        total_inventory_value = 0
        for inv in inventory_items:
            product = ontology.entities.get(inv.product_id)
            if product:
                total_inventory_value += inv.quantity * product.cost_usd
        
        return jsonify({
            'totalLocations': len(locations),
            'totalOrders': len(orders),
            'completedOrders': completed_orders,
            'activeShipments': active_shipments,
            'avgUtilization': avg_utilization,
            'onTimeDelivery': on_time_rate,
            'totalInventoryValue': total_inventory_value,
            'totalInventoryItems': len(inventory_items)
        })
        
    except Exception as e:
        logger.error(f"Metrics data error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Process chat queries through AI agents"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        agent_type = data.get('agent_type', 'simple_reflex')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        if not ontology:
            return jsonify({'error': 'System not initialized'}), 400
        
        if agent_type not in agents:
            return jsonify({'error': f'Unknown agent type: {agent_type}'}), 400
        
        logger.info(f"Processing query with {agent_type}: {query}")
        
        # Process query with selected agent
        agent = agents[agent_type]
        result = agent.process_query(query)
        
        # Convert thoughts to serializable format
        thoughts_data = []
        for thought in result.thoughts:
            thoughts_data.append({
                'step': thought.step,
                'thought': thought.thought,
                'action': thought.action,
                'observation': thought.observation,
                'confidence': thought.confidence
            })
        
        response = {
            'query': result.query,
            'answer': result.answer,
            'agent_type': result.agent_type,
            'thoughts': thoughts_data,
            'confidence': result.confidence,
            'execution_time_ms': result.execution_time_ms,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Query processed successfully in {result.execution_time_ms:.1f}ms")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/<location_id>', methods=['GET'])
def api_inventory_by_location(location_id):
    """Get inventory details for a specific location"""
    try:
        if not ontology:
            return jsonify({'error': 'System not initialized'}), 400
        
        # Get location info
        location = ontology.entities.get(location_id)
        if not location:
            return jsonify({'error': 'Location not found'}), 404
        
        # Get inventory for this location
        inventory_items = [inv for inv in ontology.query_by_type("Inventory") if inv.location_id == location_id]
        
        inventory_data = []
        total_value = 0
        
        for inv in inventory_items:
            product = ontology.entities.get(inv.product_id)
            if product:
                item_value = inv.quantity * product.cost_usd
                total_value += item_value
                
                inventory_data.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_sku': product.sku,
                    'category': product.category,
                    'quantity': inv.quantity,
                    'available': inv.quantity - inv.reserved_quantity,
                    'reserved': inv.reserved_quantity,
                    'unit_cost': product.cost_usd,
                    'total_value': item_value,
                    'safety_stock_level': product.safety_stock_level,
                    'last_updated': inv.last_updated.isoformat()
                })
        
        return jsonify({
            'location': {
                'id': location.id,
                'name': location.name,
                'type': location.type.value,
                'capacity': location.capacity_m3,
                'utilization': calculate_location_utilization(location_id)
            },
            'inventory': inventory_data,
            'summary': {
                'total_items': len(inventory_data),
                'total_quantity': sum(item['quantity'] for item in inventory_data),
                'total_value': total_value,
                'available_quantity': sum(item['available'] for item in inventory_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Inventory query error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ontology/export', methods=['GET'])
def api_export_ontology():
    """Export the complete ontology"""
    try:
        if not ontology:
            return jsonify({'error': 'System not initialized'}), 400
        
        ontology_data = ontology.export_full_ontology()
        return jsonify(ontology_data)
        
    except Exception as e:
        logger.error(f"Ontology export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/performance', methods=['GET'])
def api_performance_analytics():
    """Get detailed performance analytics"""
    try:
        if not ontology:
            return jsonify({'error': 'System not initialized'}), 400
        
        # Location performance analysis
        locations = ontology.query_by_type("Location")
        location_performance = []
        
        for location in locations:
            if location.type.value in ["warehouse", "distribution_center", "retail_store"]:
                utilization = calculate_location_utilization(location.id)
                
                # Count orders/shipments for this location
                incoming_shipments = len([s for s in ontology.query_by_type("Shipment") if s.destination_location_id == location.id])
                outgoing_shipments = len([s for s in ontology.query_by_type("Shipment") if s.origin_location_id == location.id])
                
                location_performance.append({
                    'location_id': location.id,
                    'name': location.name,
                    'type': location.type.value,
                    'utilization': utilization,
                    'capacity': location.capacity_m3,
                    'incoming_shipments': incoming_shipments,
                    'outgoing_shipments': outgoing_shipments,
                    'efficiency_score': calculate_efficiency_score(utilization)
                })
        
        # Overall network health
        orders = ontology.query_by_type("Order")
        shipments = ontology.query_by_type("Shipment")
        
        order_fulfillment_rate = len([o for o in orders if o.status.value in ["shipped", "delivered"]]) / len(orders) if orders else 0
        
        delivered_shipments = [s for s in shipments if s.actual_arrival and s.scheduled_arrival]
        on_time_deliveries = len([
            s for s in delivered_shipments 
            if s.actual_arrival <= s.scheduled_arrival
        ])
        on_time_rate = on_time_deliveries / len(delivered_shipments) if delivered_shipments else 0
        
        avg_utilization = sum(loc['utilization'] for loc in location_performance) / len(location_performance) if location_performance else 0
        
        overall_health = (order_fulfillment_rate + on_time_rate + min(avg_utilization * 1.25, 1.0)) / 3
        
        return jsonify({
            'location_performance': location_performance,
            'network_health': {
                'overall_health_score': overall_health,
                'order_fulfillment_rate': order_fulfillment_rate,
                'on_time_delivery_rate': on_time_rate,
                'avg_utilization': avg_utilization,
                'health_status': 'excellent' if overall_health > 0.8 else 'good' if overall_health > 0.6 else 'needs_attention'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Performance analytics error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def calculate_location_utilization(location_id):
    """Calculate utilization for a specific location"""
    location = ontology.entities.get(location_id)
    if not location or location.capacity_m3 == 0:
        return 0.0
    
    inventory_items = [inv for inv in ontology.query_by_type("Inventory") if inv.location_id == location_id]
    total_volume = 0
    
    for inv in inventory_items:
        product = ontology.entities.get(inv.product_id)
        if product:
            total_volume += product.volume_m3 * inv.quantity
    
    return min(total_volume / location.capacity_m3, 1.0)

def calculate_efficiency_score(utilization):
    """Calculate efficiency score based on utilization (optimal around 80%)"""
    if utilization <= 0.8:
        return utilization / 0.8
    else:
        return max(0, 1.0 - (utilization - 0.8) / 0.2)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize system on startup
    initialize_system()
    
    # Run the Flask app
    print("🏪 Supply Chain Management System Starting...")
    print("📊 Ontology Layer: ✓ Loaded")
    print("🤖 AI Agents: ✓ Initialized")
    print("🌐 Web Interface: ✓ Ready")
    print("\n🚀 Server running on http://localhost:5000")
    print("💡 Try asking: 'How many items are in Walmart Supercenter #1?'")
    
    app.run(debug=True, host='0.0.0.0', port=5000)