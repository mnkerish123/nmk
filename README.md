# 🏪 Supply Chain Management System - Walmart Scale

A comprehensive supply chain management system with **ontology mapping**, **AI-powered agents**, and **interactive visualization**. This system demonstrates a complete Walmart-scale supply chain network with intelligent query processing and reasoning capabilities.

## 🌟 Features

### 📊 Data Model & Ontology Layer
- **Complete Entity Mapping**: Products, Locations, Suppliers, Customers, Orders, Shipments, Inventory, Vehicles, Machines, Employees
- **Rich Relationships**: Semantic relationships between all entities with full traceability
- **Ontology Export**: Complete knowledge graph export with metadata

### 🤖 AI Agent Framework
- **Simple Reflex Agent**: Rule-based responses using predefined patterns
- **Model-Based Reflex Agent**: Maintains internal world model with context awareness
- **Goal-Based Agent**: Plans actions to achieve specific supply chain objectives
- **Agent Thinking Visualization**: See how agents reason through problems step-by-step

### 🌐 Interactive Web Interface
- **Network Visualization**: Interactive D3.js network graph with zoom/pan
- **Multiple Views**: Network topology, inventory heatmap, flow analysis
- **Real-time Metrics**: KPI dashboard with performance charts
- **Chat Interface**: Natural language queries with agent selection
- **Responsive Design**: Works on desktop and mobile devices

### 📈 Analytics & Insights
- **Performance Monitoring**: Order fulfillment, delivery times, utilization rates
- **Inventory Optimization**: Stock level analysis with reorder recommendations
- **Capacity Planning**: Utilization analysis with efficiency scoring
- **Cost Analysis**: Supplier optimization and transportation efficiency

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   AI Agents     │
│   (HTML/JS)     │◄──►│   (Python)      │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Ontology      │
                       │   Layer         │
                       │   (Python)      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Sample Data   │
                       │   Generator     │
                       │   (Python)      │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
supply-chain-system/
├── app.py                      # Flask web server
├── supply_chain_ontology.py    # Core data model & ontology
├── sample_data_generator.py    # Walmart-scale data generator
├── ai_agents.py               # AI agent framework
├── requirements.txt           # Python dependencies
├── templates/
│   └── index.html            # Web interface
└── README.md                 # This file
```

## 🎯 Usage Examples

### Chat Queries
Try these example queries with different AI agents:

**Inventory Queries:**
- "How many items are in Walmart Supercenter #1?"
- "What are the inventory levels at all retail stores?"
- "Show me products that need reordering"

**Performance Queries:**
- "What is the performance of our supply chain network?"
- "Which locations have the highest utilization?"
- "Show me delivery performance metrics"

**Location Queries:**
- "Where is the Dallas Distribution Center located?"
- "What is the capacity of all warehouses?"
- "Show me all locations in Texas"

**Supplier & Order Queries:**
- "Who supplies Great Value products?"
- "What are the current order statuses?"
- "Show me supplier reliability scores"

### API Endpoints

The system provides several REST API endpoints:

- `GET /api/data/network` - Network visualization data
- `GET /api/data/metrics` - Key performance indicators
- `POST /api/chat` - Process natural language queries
- `GET /api/inventory/<location_id>` - Location-specific inventory
- `GET /api/ontology/export` - Complete ontology export
- `GET /api/analytics/performance` - Detailed performance analytics

## 🧠 AI Agent Types

### 1. Simple Reflex Agent
- **Behavior**: Acts based on current environment state using predefined rules
- **Best For**: Direct, factual queries about current state
- **Example**: "How many items are in store X?"

### 2. Model-Based Reflex Agent
- **Behavior**: Maintains internal model of world state with context awareness
- **Best For**: Queries requiring historical context and trend analysis
- **Example**: "What are the performance trends for location X?"

### 3. Goal-Based Agent
- **Behavior**: Plans actions to achieve specific supply chain objectives
- **Best For**: Optimization queries and strategic planning
- **Example**: "How can we optimize inventory levels?"

## 📊 Sample Data

The system generates realistic Walmart-scale sample data including:

- **17 Locations**: Distribution centers, warehouses, factories, retail stores, ports
- **50 Products**: Great Value, Equate, Mainstays, and other Walmart brands
- **16 Suppliers**: Major suppliers like P&G, Unilever, Nestle, etc.
- **100+ Orders**: Various order statuses and delivery schedules
- **500+ Inventory Records**: Realistic stock levels across locations
- **30 Vehicles**: Trucks, ships, planes, trains for transportation
- **60 Employees**: Managers, operators, drivers, analysts

## 🔧 Customization

### Adding New Entity Types
1. Define the entity class in `supply_chain_ontology.py`
2. Add generation logic in `sample_data_generator.py`
3. Update agent processing in `ai_agents.py`

### Creating Custom Agents
1. Inherit from `BaseAgent` class
2. Implement `process_query()` method
3. Add to `AgentFactory`

### Extending the Frontend
1. Add new visualization views in `templates/index.html`
2. Create corresponding API endpoints in `app.py`
3. Update JavaScript to handle new data types

## 🎨 Visualization Features

### Network View
- **Interactive Graph**: Drag nodes, zoom, pan
- **Color Coding**: Different colors for location types
- **Size Scaling**: Node size reflects capacity
- **Tooltips**: Hover for detailed information

### Inventory Heatmap
- **Color Intensity**: Red (high utilization) to Green (low utilization)
- **Real-time Updates**: Reflects current inventory levels
- **Capacity Visualization**: Shows utilization percentages

### Flow Analysis
- **Connection Thickness**: Reflects flow volume
- **Direction Arrows**: Shows product movement
- **Flow Metrics**: Quantified throughput data

## 📈 Performance Metrics

The system tracks and visualizes key supply chain KPIs:

- **Order Completion Rate**: Percentage of delivered orders
- **On-Time Delivery**: Delivery performance metrics
- **Inventory Turnover**: Stock movement efficiency
- **Capacity Utilization**: Warehouse and facility usage
- **Supplier Reliability**: Vendor performance scores
- **Cost Efficiency**: Transportation and storage costs

## 🔍 Ontology Structure

The system uses a comprehensive ontology with the following key relationships:

- **supplies**: Supplier → Product
- **contains**: Order → Product
- **stores**: Location → Inventory → Product
- **transports**: Shipment → Product
- **manages**: Employee → Location
- **operates**: Employee → Vehicle/Machine
- **fulfills**: Shipment → Order

## 🛠️ Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Generating New Sample Data
The system automatically generates fresh sample data on startup. To regenerate:
```bash
# Restart the application
python app.py
```

### Testing Agents
```bash
# Run the AI agents test suite
python ai_agents.py
```

## 📝 License

This project is for educational and demonstration purposes. Feel free to use and modify as needed.

## 🤝 Contributing

This is a demonstration project, but suggestions and improvements are welcome!

## 📞 Support

For questions or issues, please refer to the code comments and documentation within each module.

---

**Built with ❤️ for supply chain optimization and AI agent demonstration**