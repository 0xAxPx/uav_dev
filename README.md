# UAV Development

Hands-on UAV development using open-source tools (PX4/ArduPilot). Goal: Master flight control algorithms and autonomous systems while building towards commercial inspection services.

## 🎯 Project Goals

- **Technical**: Master UAV fundamentals, flight control algorithms, computer vision, autonomous navigation
- **Commercial**: Build POC inspection system → Side business (6-12 months)
- **Platform**: Holybro X500 V2 with Pixhawk 6C
- **Differentiation**: Firmware-level expertise + AI-powered automation

## 🛠️ Development Environment

**Current Setup:**
- MacBook Pro M3 Pro, 36GB RAM, macOS Sequoia 15.3
- PX4 Autopilot v1.17.0alpha
- Gazebo Harmonic (gz-sim8)
- QGroundControl

**Hardware:**
- Holybro X500 V2 Kit with Pixhawk 6C (~£600)
- FlySky FS-i6X Radio (~£45)
- Camera: TBD (GoPro Hero 11 or DJI Action 4)
- Future: Raspberry Pi 4 for onboard CV

**Target Market:**
- UK residential/commercial roof inspections
- Automated damage detection via computer vision
- Premium pricing through AI automation

## 🗺️ Learning Roadmap (6-Month POC)

### Phase 1: Simulation + MAVLink (Months 1-2)
**Technical Focus:**
- [x] PX4 SITL environment setup
- [x] First autonomous flight
- [x] Basic waypoint navigation
- [ ] DroneKit Python scripting
- [ ] Grid pattern mission generator
- [ ] MAVLink protocol deep dive
- [ ] Telemetry logging and analysis
- [ ] Battery failsafe implementation
- [ ] Geofencing for safety

**Deliverables:**
- Configurable inspection mission scripts
- Safety systems (RTL, geofence, battery monitor)
- Mission time/coverage calculator

---

### Phase 2: Hardware + OpenCV Basics (Months 3-4)
**Technical Focus:**
- [ ] X500 V2 assembly and calibration
- [ ] Sensor calibration (IMU, compass, radio)
- [ ] First real flights (hover → loiter → autonomous)
- [ ] Real inspection mission execution
- [ ] OpenCV fundamentals (edge detection, contours, color segmentation)
- [ ] Basic damage detection algorithms
- [ ] Image dataset collection and labeling
- [ ] Flight log analysis and PID tuning

**Deliverables:**
- Working autonomous inspection missions on hardware
- Basic CV damage detection (70%+ accuracy)
- Flight performance data

**Business Parallel:**
- [ ] CAA A2 CofC certification
- [ ] Insurance and operator registration
- [ ] Market research

---

### Phase 3: Computer Vision + POC (Months 5-6)
**Technical Focus:**
- [ ] Roof defect detection pipeline
- [ ] Automated PDF report generation
- [ ] Raspberry Pi integration (optional)
- [ ] Real-time onboard processing
- [ ] Mission optimization
- [ ] 3D photogrammetry basics

**Deliverables:**
- End-to-end inspection system (flight → analysis → report)
- Professional PDF reports
- Portfolio: 10-15 real inspections
- Case studies and testimonials

**Business Parallel:**
- [ ] Free inspections for portfolio
- [ ] Website/landing page
- [ ] First 3-5 paid customers

---

### Phase 4: Advanced Algorithms (Months 7-12)
**Technical Deep Dives:**
- [ ] Custom flight controller modifications (C++)
- [ ] Advanced state estimation (EKF tuning)
- [ ] Path planning algorithms
- [ ] Obstacle avoidance (lidar integration)
- [ ] Machine learning deployment
- [ ] Thermal imaging integration
- [ ] SLAM

**Business Growth:**
- [ ] Scale to £5K-10K/month revenue
- [ ] Strategic partnerships
- [ ] Advanced services

---

## 📚 Core Technical Skills

### Flight Control & Autonomy
- MAVLink protocol
- PID control theory and tuning
- Extended Kalman Filter (sensor fusion)
- Mission planning and execution
- Failsafe systems and safety protocols
- Real-time control loops (250 Hz)

### Computer Vision
- OpenCV (image processing, feature detection)
- Object detection and classification
- Machine learning (TensorFlow/PyTorch)
- Real-time processing optimization

### Embedded Systems
- C++ firmware development (ArduPilot/PX4)
- Python scripting (DroneKit, MAVSDK, pymavlink)
- Raspberry Pi integration
- Serial communication (UART, I2C, SPI)

### Data Processing
- Flight log analysis
- Photogrammetry and 3D modeling
- Automated report generation

---

## ✅ Progress Log

### Week 1 (Nov 16, 2025) ✅
**Achieved:**
- Installed complete PX4 toolchain on macOS M3
- Resolved Gazebo Harmonic dependencies
- Fixed C++ standard compatibility issues
- **First autonomous flight in simulation**
- Executed waypoint mission via QGroundControl

**Learned:**
- MAVLink protocol basics
- PX4/Gazebo architecture
- EKF2 sensor fusion concepts
- Flight modes (Stabilize, AltHold, Loiter, Auto, RTL)

**Time invested:** ~15 hours

---

### Week 2 (Nov 23, 2025) - IN PROGRESS
**Goals:**
- [ ] Install DroneKit Python
- [ ] Write first grid mission script (3x3 pattern)
- [ ] Test in PX4 simulation
- [ ] Start OpenCV basics (edge detection)
- [ ] Research local roofing companies (3-5)
- [ ] Order X500 V2 hardware

**Target time:** 10-15 hours

---

### Week 2 (Nov 23, 2025) - IN PROGRESS
**Completed:**
- [x] Install DroneKit/pymavlink
- [x] Write first connection script
- [x] Read and parse telemetry (GPS, battery, altitude)

**Learned:**
- pymavlink connection and message handling
- MAVLink message types (GPS_RAW_INT, SYS_STATUS, VFR_HUD)
- Unit conversions (lat/lon 1e7, altitude mm→m, voltage mV→V)

**Time invested:** ~2 hours

---

## 🎓 Essential Resources

### Technical Foundation
- **"Small Unmanned Aircraft"** - Beard & McLain
- **[PX4 Development Guide](https://dev.px4.io/)**
- **[ArduPilot Documentation](https://ardupilot.org/dev/)**
- **[MAVLink Protocol](https://mavlink.io/en/)**
- **[Quadcopter Dynamics](http://andrew.gibiansky.com/blog/physics/quadcopter-dynamics/)** - Gibiansky

### Computer Vision
- OpenCV Python Tutorial (official docs)
- TensorFlow/PyTorch documentation

### Communities
- [ArduPilot Discourse](https://discuss.ardupilot.org/)
- [PX4 Slack](https://slack.px4.io/)
- [DIY Drones](https://diydrones.com/)
- r/diydrones, r/Multicopter

---

## 💼 Business Plan (Side Business Path)

**Timeline:** 6-12 months to revenue

**Service:** Automated roof inspections with AI damage detection

**Target Market:** 
- Residential homeowners
- Roofing companies (partnership model)
- Real estate agents
- Insurance adjusters

**Pricing (UK):**
- Residential roof: £150-250
- Small commercial: £400-600
- Premium (thermal + AI): £800-1200

**Differentiation:**
- Automated damage detection
- 24-hour report turnaround
- Professional PDF reports
- Open-source platform (fully customizable)

**Revenue Target:**
- Month 6: £600-1500
- Month 12: £5K-10K/month

**Regulatory:**
- CAA A2 CofC certification
- Operator registration (£10.33/year)
- Insurance (£300-800/year)
- BMFA membership (£38/year)

---

## 🚀 Quick Start

### Run Simulation
```bash
cd ~/dev/uav_dev/PX4-Autopilot
source px4_venv/bin/activate
make px4_sitl gz_x500
```

### Basic Flight Commands (pxh> prompt)
```bash
commander arm
commander takeoff
commander land
commander mode rtl
```

### Useful Aliases (~/.zshrc)
```bash
alias px4_sim='cd ~/dev/uav_dev/PX4-Autopilot && source px4_venv/bin/activate'
alias px4_gazebo='make px4_sitl gz_x500'
alias px4_clean='make clean && rm -rf build/px4_sitl_default'
```

---

## ⚠️ Build System Modifications (macOS M3)

**CMakeLists.txt:**
```cmake
set(CMAKE_CXX_STANDARD 17)
```

**cmake/px4_add_common_flags.cmake:**
```cmake
-Wno-double-promotion
```

**src/modules/simulation/gz_plugins/CMakeLists.txt:**
```cmake
# add_subdirectory(optical_flow)  # Commented out
```

**Library Symlink (GDAL):**
```bash
cd /opt/homebrew/opt/gdal/lib
ln -s libgdal.38.dylib libgdal.37.dylib
```

---

## 📊 Metrics & KPIs

### Technical Milestones
- [ ] 20+ hours simulation flight time
- [ ] 50+ autonomous missions executed
- [ ] CV damage detection accuracy >75%
- [ ] Report generation <30 min per inspection

### Business Milestones
- [ ] 10 portfolio inspections completed
- [ ] 5 customer testimonials
- [ ] CAA certification obtained
- [ ] First paid customer
- [ ] 10 paid inspections completed

---

## 📄 License

MIT License

---

**Status**: 🟢 Active Development  
**Current Phase**: Phase 1 - Simulation + MAVLink (Week 2)  
**Next Milestone**: Grid mission script + OpenCV basics  
**Last Updated**: November 23, 2025

*"Building technical expertise while creating commercial value."*