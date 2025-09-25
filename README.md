# 🔥 FireMap v1.0
**Fire Incident Response and Emergency Management Analytics Platform**

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](https://github.com/lusandicpt024-sys/firemap_v1.0)

A comprehensive GIS-enhanced forest fire simulation and suppression platform for Table Mountain National Park, Cape Town, South Africa. This system combines real geospatial data, AI-powered optimization, and interactive visualizations to model fire behavior and optimize emergency response strategies.

## 🌟 Features

### Core Capabilities
- **🔥 Multi-Fire Coordination**: Advanced coordination system for simultaneous fire incidents with resource competition analysis
- **🎯 Multi-Front Fire Analysis**: Sophisticated analysis of head, flanking, and backing fire fronts with tactical deployment
- **🛡️ Critical Area Protection**: Real-time threat assessment for 13 protected zones (residential, forest, infrastructure)
- **🤖 AI-Powered Optimization**: Machine learning algorithms for suppression strategy optimization and priority management
- **🗺️ Interactive Visualizations**: Web-based maps with real-time fire tracking and multi-fire coordination display
- **🚒 Vehicle Fleet Management**: Comprehensive fire suppression vehicle deployment with resource strain analysis
- **🌍 GIS Integration**: OpenStreetMap data integration for realistic terrain modeling
- **⚡ Real-time Fire Simulation**: Advanced forest fire spread modeling with environmental factors
- **🏔️ Multi-terrain Analysis**: Support for road, rough terrain, coastal, and water access scenarios

### Advanced Features
- **🔄 Multi-Fire Coordination Engine**: Unified command structure for 3+ simultaneous fires with resource sharing protocols
- **⚠️ Inter-Fire Risk Assessment**: Automatic detection of fire convergence risks within 3km with barrier deployment recommendations
- **📊 Resource Competition Analysis**: Dynamic fire-to-station ratio calculations with mutual aid coordination
- **🏆 Priority-Based Allocation**: Intelligent fire prioritization using size, intensity, and proximity threat factors
- **🎯 Critical Area Monitoring**: Real-time threat assessment for residential areas, forests, and infrastructure
- **🚨 Emergency Response Optimization**: Advanced tactical deployment for head, flanking, and backing fire fronts

### Visualization Components
- **Interactive HTML Maps**: Click-to-start fire capability with real-time multi-fire coordination display
- **OSM Integration**: Real OpenStreetMap data overlay with fire stations and water sources
- **Multi-Fire Dashboard**: Live coordination status, resource strain levels, and convergence risk warnings
- **Vehicle Deployment Maps**: Live tracking of fire suppression vehicle positions with priority assignments
- **Statistical Dashboards**: Real-time metrics and performance analytics for multiple simultaneous incidents
- **Terrain Analysis**: Multi-layer geographical data visualization with tactical front analysis

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** (Required for optimal performance)
- **Git** (for repository management)
- **Web Browser** (for viewing HTML visualizations)
- **10GB+ free disk space** (for OSM data files)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/lusandicpt024-sys/firemap_v1.0.git
cd firemap_v1.0
```

2. **Set up Python environment**:
```bash
# Configure your Python environment (recommended: use the configured Python path)
python --version  # Should be 3.13+
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Download OSM Data File**:
The project requires the South Africa OSM data file for geographical analysis.

📥 **Download Link**: [South Africa OSM Data (250MB)](https://drive.google.com/file/d/1cVCmQ_140kByjgJS28iqr2xGmCL8up9i/view?usp=drive_link)

- Save as: `south-africa-250922.osm.pbf` in the project root directory
- File size: ~250MB (contains detailed South African geographical data)
- Required for: OSM integration and terrain analysis features

5. **Validate installation**:
```bash
python validate_environment.py
```

### Quick Test Run

```bash
# Multi-Fire Coordination System (NEW!)
python ai_vertex.py

# Quick component testing (recommended first run)
python quick_test.py

# Full pipeline execution
python run_pipeline_robust.py

# Simple pipeline (legacy)
python run_all_simple.py
```

### 🔥 Multi-Fire Coordination Demo

The new **ai_vertex.py** system demonstrates advanced multi-fire coordination:

```bash
python ai_vertex.py
```

**Features Demonstrated:**
- ✅ **3 simultaneous test fires** automatically started
- ✅ **Multi-fire coordination analysis** with resource competition
- ✅ **Inter-fire convergence risk assessment** (HIGH/MEDIUM risks detected)
- ✅ **Priority-based resource allocation** with scoring system
- ✅ **Interactive HTML map** with click-to-start fire capability
- ✅ **Real-time coordination display** showing command structure and mutual aid status

## 📊 System Architecture

### Core Components

#### 1. **Fire Data Generation** (`generate_forest_fire_data_Version2_precise.py`)
- Generates realistic fire spread data for Table Mountain area
- Incorporates weather conditions, terrain elevation, vegetation density
- Outputs: `simulated_forest_fire_table_mountain.csv`

#### 2. **GIS-Enhanced Simulation** (`gis_enhanced_forest_fire_simulation.py`)
- Core simulation engine with real geographical data
- Integrates fire station locations and water source access
- Calculates optimal response strategies based on terrain
- Outputs: `gis_enhanced_fire_suppression.csv`, `gis_enhanced_fire_map.html`

#### 3. **OSM Visualization** (`create_osm_fire_visualisation.py`)
- Creates interactive maps with OpenStreetMap integration
- Real-time fire spread visualization with geographical context
- Outputs: `osm_integrated_fire_map.html`

#### 4. **Vehicle Suppression System** (`suppress_and_visualise_forest_fire_vehicles_Version3.py`)
- Advanced fire suppression vehicle deployment simulation
- Multi-vehicle type support (engines, tankers, 4x4s, CAFS units)
- Terrain-based accessibility analysis
- Outputs: `fire_suppression_vehicles_map.html`

#### 5. **Multi-Fire Coordination System** (`ai_vertex.py`) 🔥🔥🔥
- **Enterprise-grade multi-fire coordination** with simultaneous incident management
- **Advanced multi-front analysis** (head, flanking, backing fires) with tactical resource deployment
- **Critical area protection** for 13 zones including residential areas, forests, and infrastructure
- **Inter-fire risk assessment** with convergence monitoring and barrier deployment recommendations
- **Resource competition analysis** with priority-based allocation and mutual aid coordination
- **Interactive HTML interface** with click-to-start fire capability and real-time coordination display
- **Unified command structure** automatically established for 3+ simultaneous fires
- **Real-time fire growth simulation** with suppression tracking and containment progress

#### 6. **AI Optimization** (`ai_fire_demo.py`)
- Machine learning-powered suppression strategy optimization
- Adaptive learning algorithms for improved response efficiency
- Real-time decision support system with multi-fire context

### Pipeline Scripts

- **`run_pipeline_robust.py`**: Enhanced pipeline with error handling and timeouts
- **`quick_test.py`**: Fast component testing for development
- **`validate_environment.py`**: Comprehensive system validation

## 🗺️ Geographic Coverage

**Primary Focus Area**: Table Mountain National Park, Cape Town
- **Coordinates**: -34.37° to -34.33°N, 18.40° to 18.47°E
- **Terrain Types**: Mountainous, coastal, urban interface
- **Fire Stations**: 5+ stations with varied vehicle fleets
- **Water Sources**: Multiple reservoirs and coastal access points

## 🚒 Vehicle Fleet Specifications

The system models a comprehensive fire suppression fleet:

| Vehicle Type | Count | Capacity | Speed | Terrain Access | Effectiveness |
|--------------|-------|----------|-------|----------------|---------------|
| Heavy-Duty Fire Engine | 4 | 4,000L | 40 km/h | Road | 40% |
| 4x4 Wildland Vehicle | 6 | 2,000L | 30 km/h | Road, Rough | 35% |
| Water Tanker | 2 | 10,000L | 30 km/h | Road | 20% |
| Rapid Intervention | 3 | 750L | 60 km/h | Road, Rough | 20% |
| CAFS Unit | 2 | 1,200L | 30 km/h | Road, Rough | 50% |
| Incident Command | 1 | 0L | 50 km/h | Road | 0% (Command) |
| Dive Vehicle | 2 | 0L | 40 km/h | Water, Coast | 15% |

## 📈 Output Files

The system generates multiple output files for analysis:

### Data Files
- `simulated_forest_fire_table_mountain.csv` - Base fire simulation data
- `gis_enhanced_fire_suppression.csv` - Enhanced simulation with GIS data
- `simulated_forest_fire_table_mountain_suppressed_vehicles.csv` - Post-suppression data

### Interactive Maps
- `gis_enhanced_fire_map.html` - Main GIS-integrated fire map
- `osm_integrated_fire_map.html` - OSM-integrated visualization
- `fire_suppression_vehicles_map.html` - Vehicle deployment tracking

## 🛠️ Development

### Project Structure
```
firemap_v1.0/
├── README.md                                    # This file
├── requirements.txt                             # Python dependencies
├── south-africa-250922.osm.pbf                # OSM data file (download required)
│
├── Core Components/
│   ├── generate_forest_fire_data_Version2_precise.py
│   ├── gis_enhanced_forest_fire_simulation.py
│   ├── create_osm_fire_visualisation.py
│   ├── suppress_and_visualise_forest_fire_vehicles_Version3.py
│   └── ai_fire_demo.py
│
├── Pipeline Scripts/
│   ├── run_pipeline_robust.py
│   ├── run_all_simple.py
│   ├── quick_test.py
│   └── validate_environment.py
│
├── Utilities/
│   ├── cleanup_codebase.py
│   ├── extract_osm_fast.py
│   ├── visualize_gis_enhanced_data.py
│   └── ai_fire_suppression_trainer.py
│
└── Generated Output/
    ├── *.csv (simulation data)
    └── *.html (interactive maps)
```

### Testing

```bash
# Environment validation
python validate_environment.py

# Quick component test
python quick_test.py

# Individual component testing
python gis_enhanced_forest_fire_simulation.py
python create_osm_fire_visualisation.py
python ai_fire_demo.py
```

## 📋 Dependencies

### Required Libraries
- **pandas 2.3.2+**: Data manipulation and analysis
- **numpy 2.3.3+**: Numerical computing
- **folium 0.20.0+**: Interactive map visualizations
- **matplotlib 3.10.6+**: Static plotting and charts
- **torch 2.8.0+**: Machine learning and AI optimization
- **osmium 4.1.1+**: OpenStreetMap data processing
- **branca 0.8.1+**: HTML/JavaScript map components

### System Requirements
- **RAM**: 8GB+ recommended (OSM processing can be memory-intensive)
- **Storage**: 10GB+ (OSM files and generated outputs)
- **CPU**: Multi-core recommended for faster processing
- **Network**: Required for initial setup and map tile loading

## 🎯 Use Cases

### Emergency Response Planning
- **Pre-incident Planning**: Model potential fire scenarios
- **Resource Allocation**: Optimize vehicle and personnel deployment
- **Response Time Analysis**: Calculate optimal station coverage
- **Training Simulations**: Safe environment for training exercises

### Research and Analysis
- **Fire Behavior Studies**: Understand spread patterns in Table Mountain terrain
- **Climate Impact Assessment**: Model effects of weather changes
- **Urban Interface Analysis**: Study fire risks in populated areas
- **Technology Integration**: Test new suppression technologies

### Operational Support
- **Real-time Decision Support**: Live fire incident assistance
- **Performance Metrics**: Track suppression effectiveness
- **Resource Planning**: Long-term fleet and infrastructure planning
- **Inter-agency Coordination**: Multi-department response optimization

## 🚧 Known Issues & Limitations

### Current Limitations
- **Geographic Scope**: Currently focused on Table Mountain area only
- **Real-time Data**: Simulated data only (no live fire feeds)
- **Weather Integration**: Basic weather modeling (can be enhanced)
- **Validation**: Models based on simulated scenarios

### Future Enhancements
- [ ] Real-time weather API integration
- [ ] Expanded geographic coverage (Western Cape region)
- [ ] Live fire incident data feeds
- [ ] Mobile app interface
- [ ] Advanced AI prediction models
- [ ] Multi-language support

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone and setup
git clone https://github.com/lusandicpt024-sys/firemap_v1.0.git
cd firemap_v1.0

# Install development dependencies
pip install -r requirements.txt

# Run tests
python validate_environment.py
python quick_test.py
```

## 📧 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/lusandicpt024-sys/firemap_v1.0/issues)
- **Discussions**: [GitHub Discussions](https://github.com/lusandicpt024-sys/firemap_v1.0/discussions)
- **Documentation**: See individual script docstrings and comments

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenStreetMap Contributors**: Geographic data foundation
- **Cape Town Fire & Rescue**: Operational insights and validation
- **Table Mountain National Park**: Geographic and environmental data
- **Python Community**: Excellent libraries and tools
- **Folium Project**: Interactive mapping capabilities

---

**⚠️ Important Note**: This is a simulation and training platform. For actual fire emergencies, contact your local emergency services immediately.

**🔥 FireMap v1.0** - *Advancing fire response through technology*
