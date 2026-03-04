# UAV Development

A hands-on learning project for UAV (Unmanned Aerial Vehicle) development using industry-standard open-source tools. Starting from simulation and progressing toward real hardware implementation.

## 🎯 Project Goals

- Master UAV fundamentals through simulation-first approach
- Build proficiency with PX4, Gazebo, and MAVLink protocol
- Develop autonomous flight algorithms and mission planning
- Progress from simulation to real Pixhawk hardware (Holybro X500 V2)

## 🛠️ Development Environment

**Current Setup:**
- MacBook Pro M3 Pro, 36GB RAM, macOS Sequoia 15.3
- PX4 Autopilot v1.17.0alpha
- Gazebo Harmonic (gz-sim8)
- QGroundControl

**Target Hardware:**
- Holybro X500 V2 Kit with Pixhawk 6C (~£600)
- UK CAA registration required (>250g)

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────┐
│              MacBook Pro M3 (Development Machine)         │
│                                                           │
│  ┌─────────────────────┐                                 │
│  │   Gazebo Harmonic   │  ← 3D Physics Simulator         │
│  │                     │                                  │
│  │  • Physics engine   │    Gazebo Transport Protocol    │
│  │  • 3D visualization │           ↕                     │
│  │  • Sensor simulation│    ┌──────────────┐             │
│  │    - GPS            │    │ Gazebo-PX4   │             │
│  │    - IMU            │←───│   Plugin     │ (Bridge)    │
│  │    - Magnetometer   │    └──────────────┘             │
│  │    - Barometer      │           ↕                     │
│  │  • Motor dynamics   │    MAVLink over UDP             │
│  └─────────────────────┘           ↕                     │
│                              ┌──────────────────┐        │
│                              │  PX4 Autopilot   │        │
│                              │  (SITL Mode)     │        │
│                              │                  │        │
│                              │  • Flight control│        │
│                              │  • EKF2 (sensor  │        │
│                              │    fusion)       │        │
│                              │  • Mission logic │        │
│                              │  • 250 Hz loop   │        │
│                              └──────────────────┘        │
│                                      ↕                    │
│                              MAVLink UDP:14550            │
│                                      ↕                    │
│                              ┌──────────────────┐        │
│                              │ QGroundControl   │        │
│                              │                  │        │
│                              │  • Mission plan  │        │
│                              │  • Telemetry     │        │
│                              │  • Commands      │        │
│                              └──────────────────┘        │
└──────────────────────────────────────────────────────────┘
```

### Key Protocols

| Component | Protocol | Purpose |
|-----------|----------|---------|
| Gazebo ↔ Plugin | Gazebo Transport | Internal sensor/motor data |
| Plugin ↔ PX4 | MAVLink (UDP) | Sensor data + motor commands |
| PX4 ↔ QGC | MAVLink (UDP:14550) | Telemetry + user commands |

## 🚀 Quick Start

### Prerequisites

```bash
# Install Homebrew dependencies
brew tap osrf/simulation
brew install gz-harmonic qt@5 opencv protobuf

# Add to ~/.zshrc
export GZ_VERSION=harmonic
export GZ_SIM_SYSTEM_PLUGIN_PATH=/opt/homebrew/lib
export GZ_SIM_RESOURCE_PATH=/opt/homebrew/share/gz
export PATH="/opt/homebrew/opt/qt@5/bin:$PATH"
export CMAKE_PREFIX_PATH="/opt/homebrew/opt/qt@5:$CMAKE_PREFIX_PATH"
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
```

### Running the Simulation

```bash
# Navigate to PX4 directory
cd /Users/alex/dev/uav_dev/PX4-Autopilot

# Activate Python environment
source px4_venv/bin/activate

# Launch PX4 + Gazebo with X500 quadcopter
make px4_sitl gz_x500
```

This opens:
- Gazebo 3D simulator window
- PX4 console (pxh> prompt)
- QGroundControl auto-connects

### Running Autonomous Mission

```bash
# In a new terminal
cd ~/dev/uav_dev
source PX4-Autopilot/px4_venv/bin/activate
python3 scripts/missions/first_flight.py
```

### Basic Flight Commands

In PX4 console (pxh> prompt):

```bash
# Arm motors
commander arm

# Takeoff to 2.5m
commander takeoff

# Land
commander land

# Return to launch
commander mode rtl
```

### Useful Aliases

Add to `~/.zshrc`:

```bash
alias px4_sim='cd ~/dev/uav_dev/PX4-Autopilot && source px4_venv/bin/activate'
alias px4_gazebo='make px4_sitl gz_x500'
alias px4_clean='make clean && rm -rf build/px4_sitl_default'
```

## 📚 Essential Reading

### Getting Started
1. **[PX4 User Guide](https://docs.px4.io/)** - Official documentation
2. **[MAVLink Protocol](https://mavlink.io/en/)** - Communication protocol
3. **[Gazebo Tutorials](https://gazebosim.org/docs)** - Simulator basics

### Core Concepts
4. **"Small Unmanned Aircraft: Theory and Practice"** by Beard & McLain
   - THE textbook for UAV fundamentals
   - Control theory, estimation, path planning
   - Used in university courses worldwide

5. **[Quadcopter Dynamics (Gibiansky)](http://andrew.gibiansky.com/blog/physics/quadcopter-dynamics/)**
   - Free online resource
   - Motor dynamics, PID control, state estimation
   - Practical implementation focus

### Advanced Topics
6. **[PX4 Development Guide](https://dev.px4.io/)** - Architecture deep-dive
7. **"Estimation with Applications to Tracking and Navigation"** - Kalman filters
8. **Learning ROS 2** (Packt) - For advanced autonomy integration

## ✅ Achievements

**Week 1 (November 2025):**
- ✅ Complete PX4 development environment on macOS M3
- ✅ First autonomous flight in simulation
- ✅ Basic MAVLink communication and OFFBOARD mode

**Week 2 (March 2026):**
- ✅ Position monitoring via LOCAL_POSITION_NED messages
- ✅ Autonomous waypoint navigation with verification
- ✅ Multi-waypoint mission: 5 waypoints, 60m distance, 6min flight
- ✅ Waypoint accuracy: within 0.5m tolerance

## 🗺️ Learning Roadmap

### Phase 1: Simulation Fundamentals ✅ (Complete)
- [x] Set up PX4 + Gazebo + QGroundControl
- [x] First successful flight
- [x] Basic commands (arm, takeoff, land)
- [x] Waypoint navigation via QGC
- [x] Python scripts using pymavlink
- [x] Autonomous position control in OFFBOARD mode
- [x] Multi-waypoint mission execution

### Phase 2: Advanced Mission Planning (In Progress)
- [ ] Grid pattern generator for area coverage
- [ ] Mission abstraction and reusable patterns
- [ ] Velocity-based control for smoother flight
- [ ] Yaw control for camera pointing
- [ ] Computer vision integration (OpenCV)

### Phase 3: Advanced Autonomy
- [ ] Object detection and tracking
- [ ] Path planning algorithms
- [ ] ROS 2 integration
- [ ] Obstacle avoidance

### Phase 4: Hardware Deployment
- [ ] Purchase Holybro X500 V2 kit
- [ ] Hardware assembly and calibration
- [ ] UK CAA operator registration
- [ ] Outdoor flight testing

## 🎓 Key Concepts Learned

### Flight Control
- **MAVLink Protocol**: Universal communication standard for drones
- **OFFBOARD Mode**: Direct position/velocity control via external commands
- **NED Coordinates**: North-East-Down frame (Z positive = downward)
- **Type Mask**: Bit flags controlling which setpoint fields are used

### Position Control
- **LOCAL_POSITION_NED**: Real-time position updates from EKF2
- **Waypoint Verification**: Distance-based arrival detection with tolerances
- **Acceptance Radius**: Horizontal (XY) and vertical (Z) tolerance zones
- **Setpoint Streaming**: Continuous commands at >2Hz required by PX4

### System Architecture
- **EKF2**: Extended Kalman Filter for sensor fusion (GPS + IMU + barometer)
- **Flight Modes**: Manual, Altitude Hold, Position Hold, Mission, RTL, OFFBOARD
- **SITL**: Software-In-The-Loop simulation (no hardware needed)
- **250 Hz Control Loop**: PX4's real-time flight control frequency

## ⚠️ Important Notes

### Build System Modifications

Due to macOS M3 and newer dependency versions, the following modifications were made:

**CMakeLists.txt:**
```cmake
set(CMAKE_CXX_STANDARD 17)  # Changed from 14
```

**cmake/px4_add_common_flags.cmake:**
```cmake
-Wno-double-promotion  # Changed from -Wdouble-promotion
```

**src/modules/simulation/gz_plugins/CMakeLists.txt:**
```cmake
# add_subdirectory(optical_flow)  # Commented out (build issues)
# Removed OpticalFlowSystem from add_custom_target dependencies
```

### Library Symlink (GDAL)

```bash
cd /opt/homebrew/opt/gdal/lib
ln -s libgdal.38.dylib libgdal.37.dylib
```

### MAVLink Communication Ports

- **Port 14540**: Onboard companion computer (used by autonomous scripts)
- **Port 14550**: Ground control station (used by QGroundControl)

This separation allows scripts and QGC to communicate simultaneously without conflicts.

## 🤝 Resources & Community

- [PX4 Discuss Forum](https://discuss.px4.io/)
- [DroneCode Foundation](https://www.dronecode.org/)
- r/diydrones, r/Multicopter

## 📄 License

MIT License

---

**Status**: 🟢 Active Development  
**Last Updated**: March 4, 2026

*"From simulation to autonomous flight - the journey continues."*