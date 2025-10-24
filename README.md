# UAV Development

A comprehensive learning project focused on UAV (Unmanned Aerial Vehicle) development, starting from simulation and progressing toward real hardware implementation.

## 🎯 Project Goals

- Master UAV development fundamentals through hands-on practice
- Build proficiency with industry-standard tools (PX4, QGroundControl, MAVLink)
- Develop autonomous flight algorithms and mission planning capabilities
- Progress from simulation environment to real-world drone operations
- Document the entire learning journey for personal reference and community benefit

## 🛠️ Development Environment

**Hardware:**
- MacBook Pro 16-inch (Nov 2023)
- Apple M3 Pro chip
- 36 GB RAM
- macOS Sequoia 15.3

**Planned Physical Hardware:**
- Holybro X500 V2 Kit with Pixhawk 6C (~£600)
- *To be purchased after mastering simulation environment*

## 🧪 Current Lab Setup

Our simulation environment consists of three main components running locally:

```
┌─────────────────────────┐
│   MacBook Pro M3 Pro    │
│                         │
│  ┌──────────────────┐  │     MAVLink Protocol
│  │  PX4 Autopilot   │◄─┼────► (UDP Port 14550)
│  │  (Flight Control)│  │
│  │                  │  │     • Telemetry data
│  │  • 250 Hz loop   │  │     • Commands
│  │  • Sensor fusion │  │     • Parameters
│  │  • Motor control │  │
│  └────────┬─────────┘  │
│           │             │
│           ▼             │
│  ┌──────────────────┐  │
│  │  SIH Simulator   │  │
│  │  (Physics Engine)│  │
│  │                  │  │
│  │  • Virtual IMU   │  │
│  │  • Virtual GPS   │  │
│  │  • Virtual motors│  │
│  └──────────────────┘  │
│                         │
│  ┌──────────────────┐  │
│  │ QGroundControl   │  │
│  │ (Ground Station) │  │
│  │                  │  │
│  │  • Mission plan  │  │
│  │  • Telemetry view│  │
│  │  • Calibration   │  │
│  └──────────────────┘  │
└─────────────────────────┘
```

**What's Running:**
- **PX4 SITL** - Complete autopilot software in simulation mode
- **SIH (Simulation-In-Hardware)** - Lightweight built-in physics simulator
- **QGroundControl** - Mission planning and monitoring interface
- **Communication** - MAVLink protocol over UDP localhost

## 📚 Technology Stack

### Current Focus (Simulation Phase)
- **PX4 Autopilot** - Open-source flight control software
- **SITL (Software In The Loop)** - Simulation without hardware
- **jMAVSim/Gazebo** - Physics-based drone simulators
- **QGroundControl** - Ground control station for mission planning
- **Python** - Primary programming language for custom scripts
- **MAVLink** - Communication protocol between drone and ground station

### Future Additions
- **ROS 2 (Robot Operating System)** - Advanced robotics middleware
- **Computer Vision** - Object detection and tracking
- **Path Planning Algorithms** - Autonomous navigation
- **Real Sensor Integration** - GPS, IMU, cameras, lidar

## 🗺️ Learning Roadmap

### Phase 1: Simulation Setup ✅ (In Progress)
- [x] Choose development platform (macOS native)
- [x] Create GitHub repository
- [x] Install Homebrew and dependencies
- [x] Install PX4 toolchain and build system
- [x] Install QGroundControl
- [x] Configure Python virtual environment
- [x] Successfully build and run PX4 SITL
- [x] Connect QGroundControl to simulated drone
- [ ] Calibrate simulated sensors
- [ ] Execute first test flight
- [ ] Understand PX4 architecture

### Phase 2: Basic Flight Operations
- [ ] Manual flight control in simulation
- [ ] Create and execute simple missions
- [ ] Understand flight modes (Manual, Altitude, Position, Mission)
- [ ] Learn MAVLink protocol basics
- [ ] Write first Python script to control drone

### Phase 3: Autonomous Navigation
- [ ] Waypoint navigation
- [ ] Return-to-launch functionality
- [ ] Geofencing and safety features
- [ ] Path planning algorithms
- [ ] Obstacle avoidance (simulated)

### Phase 4: Advanced Programming
- [ ] Custom flight modes
- [ ] Sensor fusion understanding
- [ ] Computer vision integration
- [ ] Real-time data processing
- [ ] ROS 2 integration

### Phase 5: Hardware Transition
- [ ] Purchase Holybro X500 V2 kit
- [ ] Hardware assembly and calibration
- [ ] Outdoor flight preparation
- [ ] Safety procedures and checklists
- [ ] Real-world flight testing

## 🚀 Quick Start

### Prerequisites
- macOS (Sequoia 15.3 or later)
- Homebrew package manager
- 20+ GB free disk space
- Basic terminal/command line knowledge

### Running the Simulation

```bash
# Navigate to PX4 directory
cd /Users/alex/dev/uav_dev/PX4-Autopilot

# Activate Python virtual environment
source px4_venv/bin/activate

# Start PX4 simulation with SIH (headless mode)
HEADLESS=1 make px4_sitl_default none

# In another terminal, launch QGroundControl
open /Applications/QGroundControl.app
```

### Automated Setup (Optional)

Add this to your `~/.zshrc` to automatically activate the virtual environment:

```bash
# PX4 Development aliases
alias px4_sim='cd /Users/alex/dev/uav_dev/PX4-Autopilot && source px4_venv/bin/activate && HEADLESS=1 make px4_sitl_default none'
alias px4_env='cd /Users/alex/dev/uav_dev/PX4-Autopilot && source px4_venv/bin/activate'
```

Then you can simply type `px4_sim` to start the simulation!

*Detailed installation instructions in `docs/setup-guide-macos.md`*

## 📖 Learning Resources

### Official Documentation
- [PX4 User Guide](https://docs.px4.io/)
- [QGroundControl User Guide](https://docs.qgroundcontrol.com/)
- [MAVLink Protocol](https://mavlink.io/)

### Tutorials & Courses
- PX4 Developer Guide
- ArduPilot documentation (for comparison)
- YouTube channels for UAV development

### Communities
- PX4 Discuss Forum
- DroneCode Foundation
- Reddit: r/diydrones, r/Multicopter

*More resources to be added as I discover them*

## 🎓 Key Concepts to Master

- **Flight Control Systems**: PID controllers, stabilization
- **Sensor Fusion**: IMU, GPS, barometer integration
- **State Estimation**: Kalman filters, position estimation
- **Mission Planning**: Waypoints, geofencing, safety protocols
- **Communication Protocols**: MAVLink, telemetry
- **Coordinate Systems**: NED, ENU, geographic coordinates
- **Battery Management**: Flight time estimation, failsafes

## 📝 Progress Log

### October 2025
- **Oct 23**: Project initiated, GitHub repository created
- **Oct 23**: Decided on Holybro X500 V2 with Pixhawk 6C as target hardware
- **Oct 23**: Chose simulation-first approach for cost-effective learning
- **Oct 23**: Configured development environment (MacBook Pro M3 Pro)
- **Oct 24**: Successfully installed PX4 toolchain and dependencies
- **Oct 24**: Resolved Java compatibility issues for jMAVSim (upgraded to OpenJDK 25)
- **Oct 24**: Configured Python virtual environment for PX4
- **Oct 24**: First successful PX4 SITL build and execution with SIH simulator
- **Oct 24**: Installed and connected QGroundControl to simulated drone
- **Oct 24**: Understanding PX4 control loop (250 Hz) and MAVLink communication
- **Oct 24**: Ready for sensor calibration and first flight test

*Regular updates to be added as project progresses*

## ⚠️ Safety Considerations

Even in simulation, developing good safety habits is crucial:

- Always understand what code does before executing
- Implement emergency stop/kill switch mechanisms
- Test in simulation extensively before hardware
- Follow local drone regulations and laws
- Never fly near people, airports, or restricted areas
- Maintain visual line of sight (VLOS) when flying real hardware
- Keep batteries and equipment in good condition

## 🤝 Contributing

This is primarily a personal learning project, but suggestions and advice are welcome! Feel free to:
- Open issues for questions or discussions
- Share useful resources
- Suggest improvements to code or documentation

## 📄 License

MIT License - Feel free to use this repository as a template for your own UAV learning journey.

## 🙏 Acknowledgments

- PX4 Development Team
- DroneCode Foundation
- Open-source UAV community
- Everyone sharing knowledge and tutorials online

---

**Status**: 🟢 Active Development  
**Last Updated**: October 23, 2025  
**Contact**: [Your contact info or leave blank]

*"The journey of a thousand flights begins with a single simulation."*