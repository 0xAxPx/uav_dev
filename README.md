# UAV Development

A hands-on learning project for UAV (Unmanned Aerial Vehicle) development using industry-standard open-source tools. Starting from simulation and progressing toward real hardware implementation.

## 🎯 Project Goals

- Master UAV fundamentals through simulation-first approach
- Build proficiency with PX4, Gazebo, and MAVLink protocol
- Develop autonomous flight algorithms and mission planning
- Build professional inspection reporting system
- Progress from simulation to real Pixhawk hardware (Holybro X500 V2)

## 🛠️ Development Environment

**Current Setup:**
- MacBook Pro M3 Pro, 36GB RAM, macOS Sequoia 15.3
- PX4 Autopilot v1.17.0alpha
- Gazebo Harmonic (gz-sim8)
- QGroundControl
- Python 3.14 with pymavlink, pandas, matplotlib, reportlab

**Target Hardware:**
- Holybro X500 V2 Kit with Pixhawk 6C (~£600)
- UK CAA registration required (>250g)

## 🚀 Quick Start

### Running an Autonomous Inspection Mission
```bash
# Terminal 1 - Launch PX4 + Gazebo
cd ~/dev/uav_dev/PX4-Autopilot
source px4_venv/bin/activate
make px4_sitl gz_x500

# Terminal 2 - Run autonomous grid mission with auto-reporting
cd ~/dev/uav_dev/scripts/missions
python3 grid_flight.py

# Automatically generates:
# - CSV telemetry data
# - PNG visualization plots
# - Professional PDF reports
```

### Generate Client Report
```bash
cd ~/dev/uav_dev/scripts/analysis
python3 generate_client_report.py
```

## ✅ Achievements

**Week 1 (November 2025):**
- ✅ Complete PX4 development environment on macOS M3
- ✅ First autonomous flight in simulation
- ✅ Basic MAVLink communication and OFFBOARD mode

**Week 2 (March 2026):**
- ✅ Position monitoring and waypoint navigation
- ✅ Multi-waypoint missions with 0.5m accuracy
- ✅ Grid pattern generator for systematic area coverage
- ✅ Boustrophedon (lawn mower) flight algorithm
- ✅ Real-time telemetry logging (2 Hz)
- ✅ Professional flight data visualization

**Week 3 (March 19, 2026):**
- ✅ Battery optimization analysis and flight profile testing
- ✅ Efficient flight profile (6 m/s) - 20-25% projected battery savings
- ✅ Enhanced technical reports with embedded visualizations
- ✅ Professional client-facing inspection reports
- ✅ Automated post-flight processing pipeline

### Flight Profile Comparison

Tested three flight profiles on 100m × 100m grid mission:

| Profile | Max Speed | Duration | Battery* | Accel Events | Use Case |
|---------|-----------|----------|----------|--------------|----------|
| **Aggressive** | 12 m/s | 11.4 min | 45% | 168 | Testing only |
| **Efficient** ✅ | 6 m/s | 11.8 min | 45%* | 139 | **Recommended** |
| **Conservative** | 3 m/s | 12.2 min | 45% | 61 | Maximum efficiency |

*Simulation shows same battery usage due to simplified model. Real hardware expected to show 20-25% savings with Efficient profile based on reduced acceleration events.

### Recent Mission Results

**100m × 100m Grid (Efficient Profile):**
- **Duration**: 11.8 minutes
- **Distance**: 1,370m
- **Coverage**: 10,000 m² (2.5 acres)
- **Waypoints**: 24 (22 grid + takeoff + landing)
- **Altitude**: 14.42m average (±0.78m precision)
- **Max Speed**: 6.17 m/s
- **Telemetry readings**: 1,403

**200m × 200m Grid (Baseline):**
- **Duration**: 21.5 minutes
- **Distance**: 4.75 km
- **Coverage**: 40,000 m² (4 hectares)
- **Waypoints**: 44 (42 grid + takeoff + landing)
- **Altitude accuracy**: ±0.24m from 15m target

## 📊 Professional Reporting System

### Automated Report Generation

Every flight automatically produces:
1. **CSV Telemetry** - Raw flight data (position, velocity, battery, waypoints)
2. **PNG Visualizations** - 4 charts (2D path, 3D path, altitude, speed)
3. **Enhanced Technical Report** - Multi-page PDF with performance analysis
4. **Client Inspection Report** - Professional deliverable with simplified language

### Report Features

**Technical Reports Include:**
- Executive summary with flight profile detection
- Key performance indicators with ratings
- Detailed statistics (mission, speed, altitude, battery)
- Embedded flight visualizations
- Performance analysis and recommendations
- Battery efficiency metrics

**Client Reports Include:**
- Property details and inspection metadata
- Weather conditions documentation
- Executive summary (non-technical language)
- Area surveyed (m² and acres, ft and meters)
- Inspection findings with severity ratings
- Flight path visualization
- Recommendations and next steps
- Professional disclaimer

## 🗺️ Learning Roadmap

### Phase 1: Simulation Fundamentals ✅ (Complete)
- [x] Set up PX4 + Gazebo + QGroundControl
- [x] Autonomous position control in OFFBOARD mode
- [x] Multi-waypoint mission execution
- [x] Grid pattern generation and execution
- [x] Telemetry logging and visualization
- [x] Battery optimization and flight profiles
- [x] Professional reporting system

### Phase 2: Advanced Capabilities (Next)
- [ ] Camera integration and image capture
- [ ] Geotagged imagery
- [ ] Computer vision for damage detection
- [ ] Real-time mission planning
- [ ] ROS 2 integration

### Phase 3: Hardware Deployment
- [ ] Holybro X500 V2 assembly
- [ ] UK CAA operator registration
- [ ] Hardware-in-the-loop (HITL) testing
- [ ] Real hardware battery validation
- [ ] Outdoor flight testing

## 🎓 Key Concepts Mastered

- **MAVLink Protocol**: OFFBOARD mode, position setpoints, parameter control
- **Grid Patterns**: Boustrophedon algorithm for efficient area coverage
- **NED Coordinates**: North-East-Down frame navigation
- **Telemetry Logging**: CSV-based flight data recording at 2 Hz
- **Data Visualization**: matplotlib for professional flight analysis
- **Threading**: Background setpoint streaming and telemetry capture
- **Flight Optimization**: Battery-efficient flight profile development
- **Report Generation**: Professional PDF creation with ReportLab

## 📁 Project Structure
```
uav_dev/
├── PX4-Autopilot/          # PX4 flight stack
├── scripts/
│   ├── missions/
│   │   ├── first_flight.py          # Basic autonomous flight
│   │   ├── grid_mission.py          # Grid pattern generator
│   │   ├── grid_flight.py           # Full grid mission (auto-reporting)
│   │   ├── telemetry_logging.py     # Flight data recorder
│   │   ├── test_grid_configs.py     # Mission planning analysis
│   │   └── logs/                    # Flight telemetry CSVs
│   └── analysis/
│       ├── visualize_flight.py              # Plot generation
│       ├── battery_analysis.py              # Battery optimization
│       ├── generate_report.py               # Technical reports (basic)
│       ├── generate_report_enhanced.py      # Technical reports (detailed)
│       ├── generate_client_report.py        # Client deliverables
│       ├── plots/                           # Generated visualizations
│       └── reports/                         # PDF outputs
└── README.md
```

## ⚡ Battery Optimization

### Flight Profile Configuration

Three profiles available in `grid_flight.py`:

```python
FLIGHT_PROFILE = "efficient"  # Options: aggressive, efficient, conservative

profiles = {
    "aggressive": {
        "max_speed": 12.0,
        "max_accel": 10.0,
        "description": "Fast, high battery consumption"
    },
    "efficient": {
        "max_speed": 6.0,
        "max_accel": 3.0,
        "description": "Balanced speed and efficiency (RECOMMENDED)"
    },
    "conservative": {
        "max_speed": 3.0,
        "max_accel": 1.5,
        "description": "Maximum battery efficiency"
    }
}
```

**Recommendation**: Use **Efficient** profile for optimal balance of speed and battery life.

### Expected Real Hardware Savings

Based on acceleration event analysis:
- **Efficient vs Aggressive**: 20-25% battery savings
- **Conservative vs Aggressive**: 30-35% battery savings
- Trade-off: 3-6% longer mission time

## ⚠️ Important Notes

### macOS M3 Build Modifications

**CMakeLists.txt:**
```cmake
set(CMAKE_CXX_STANDARD 17)  # Changed from 14
```

**cmake/px4_add_common_flags.cmake:**
```cmake
-Wno-double-promotion  # Changed from -Wdouble-promotion
```

### MAVLink Ports
- **14540**: Autonomous scripts (onboard computer)
- **14550**: QGroundControl (ground station)

### Running Scripts
- Always run from script's directory (e.g., `cd scripts/missions` then `python3 grid_flight.py`)
- Import paths are relative to working directory
- Logs and reports save relative to script location

## 🤝 Resources

- [PX4 Documentation](https://docs.px4.io/)
- [MAVLink Protocol](https://mavlink.io/en/)
- [PX4 Discuss Forum](https://discuss.px4.io/)
- [Beard & McLain - Small Unmanned Aircraft](http://uavbook.byu.edu/)

## 📄 License

MIT License

---

**Status**: 🟢 Active Development  
**Last Updated**: March 19, 2026

*"From theory to commercial-ready autonomous inspection platform."*