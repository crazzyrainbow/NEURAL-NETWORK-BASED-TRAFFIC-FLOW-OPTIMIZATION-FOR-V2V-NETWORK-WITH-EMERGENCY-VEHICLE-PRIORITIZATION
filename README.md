# 🚗 NEURAL-NETWORK-BASED TRAFFIC FLOW OPTIMIZATION FOR V2V NETWORK WITH EMERGENCY VEHICLE PRIORITIZATION

This project presents a simulation-based solution using **Graph Neural Networks (GNNs)** and **V2V communication** to optimize traffic flow and prioritize emergency vehicles in urban environments. Built using **SUMO (Simulation of Urban Mobility)** and controlled through **Python TraCI**, this system intelligently reroutes traffic and manages traffic lights in real-time.

---

## 🧠 Key Features

- **🚨 Emergency Vehicle Prioritization:** Real-time detection and handling of emergency vehicles using TraCI.
- **🔁 Dynamic Vehicle Rerouting:** Automatically reroutes nearby vehicles to clear paths for emergency vehicles.
- **🚦 Adaptive Traffic Signal Control:** Updates traffic light phases based on traffic flow and emergency priorities.
- **📡 V2V Communication Simulation:** Models cooperative vehicle behavior using V2V principles.
- **📊 Graph Neural Network Integration:** Predicts optimal traffic paths and flow using a trained GNN model.

---

## 📁 Directory Structure

```
📦 NEURAL-NETWORK-BASED-TRAFFIC-FLOW-OPTIMIZATION
│
├── sumo_config/                  # SUMO network and route configuration files
│   ├── network.net.xml
│   ├── routes.rou.xml
│   ├── simulation.sumocfg
│
├── traci_control/                # Python scripts for TraCI-based control
│   ├── launch_simulation.py
│   ├── traffic_light_controller.py
│   ├── reroute_logic.py
│
├── emergency_vehicle_logic/      # Emergency vehicle detection and handling
│   ├── ev_detector.py
│   ├── clear_lane_for_ev.py
│
├── gnn_model/                    # Graph Neural Network training and prediction
│   ├── model.py
│   ├── train.py
│   ├── dataset_handler.py
│
├── utils/                        # Common utility functions and logging
│
├── results/                      # Graphs, logs, and analysis reports
│
└── README.md                     # Project documentation
```

---

## ⚙️ Technologies Used

- Python 3.8+
- SUMO (Simulation of Urban Mobility)
- TraCI (Traffic Control Interface)
- PyTorch & PyTorch Geometric (for GNN)
- NumPy, Pandas, Matplotlib

---

## 🚀 Getting Started

### 🔧 Prerequisites

Install dependencies:
```bash
pip install traci torch torch-geometric numpy pandas matplotlib
```

Install and configure [SUMO](https://sumo.dlr.de/docs/Downloads.html).

---

### ▶️ Running the Simulation

```bash
# Step 1: Train the GNN model
cd gnn_model/
python train.py

# Step 2: Launch SUMO simulation with Python TraCI
cd ../traci_control/
python launch_simulation.py
```

---

## 📊 Sample Results

- **35% reduction** in emergency vehicle response time.
- **Improved throughput** and flow stability under high-density traffic.
- **Minimal disruption** to non-emergency vehicles due to dynamic rerouting.

Graphs and logs can be found in the `/results` folder.

---

## 🎯 Research Objectives

- Design an intelligent urban traffic system using ML-based flow optimization.
- Prioritize emergency vehicles with minimum delay to public traffic.
- Create a scalable simulation for smart cities using open-source tools.

---

## 🧩 Future Enhancements

- Real-time video input integration using OpenCV for vehicle classification.
- Edge deployment on Raspberry Pi for real-world traffic poles or drones.
- Expand GNN to handle pedestrian crossings and multi-agent scenarios.

---

## 👨‍💻 Author

**Ankit Kumar**  
_Developer & Researcher in Intelligent Transportation Systems_  
GitHub: [https://github.com/crazzyrainbow]
Email: [ankitkumarsuman6@gmail.com]

---

## 🙌 Contributions

Pull requests, bug reports, and improvement suggestions are always welcome!
