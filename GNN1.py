import xml.etree.ElementTree as ET
import networkx as nx
import torch
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
import matplotlib.pyplot as plt
import traci

# Parse the XML file
tree = ET.parse('C:/Users/ankit/Desktop/Progress/V2V/DAY__04/test_network.net.xml')
root = tree.getroot()

# Create a graph
G = nx.DiGraph()

# Add nodes (junctions) and edges (roads)
for junction in root.findall('junction'):
    G.add_node(junction.get('id'), pos=(float(junction.get('x')), float(junction.get('y'))))

for edge in root.findall('edge'):
    from_node = edge.get('from')
    to_node = edge.get('to')
    if from_node and to_node:
        G.add_edge(from_node, to_node)

# Map node identifiers to integers for PyTorch Geometric
node_mapping = {node: i for i, node in enumerate(G.nodes)}
G = nx.relabel_nodes(G, node_mapping)

# Convert to PyTorch Geometric format
edge_index = torch.tensor(list(G.edges)).t().contiguous()
x = torch.tensor([G.nodes[node]['pos'] for node in G.nodes], dtype=torch.float)
data = Data(x=x, edge_index=edge_index)

# Define a simple GNN model
class GNN(torch.nn.Module):
    def __init__(self):
        super(GNN, self).__init__()
        self.conv1 = GCNConv(2, 16)
        self.conv2 = GCNConv(16, 2)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index)
        x = torch.relu(x)
        x = self.conv2(x, edge_index)
        return x

# Initialize and train the model (dummy training)
model = GNN()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
criterion = torch.nn.MSELoss()

for epoch in range(100):
    model.train()
    optimizer.zero_grad()
    out = model(data)
    loss = criterion(out, data.x)
    loss.backward()
    optimizer.step()

# Visualize the graph
pos = {node: G.nodes[node]['pos'] for node in G.nodes}
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray')
plt.savefig("graph.jpg")  # Save graph visualization
plt.show()

# SUMO Simulation Setup
sumoCmd = ["sumo-gui", "-c", "C:/Users/ankit/Desktop/Progress/V2V/DAY__05/sumocfg.sumo.cfg"]

try:
    traci.start(sumoCmd)
    print("SUMO simulation started successfully.")
except Exception as e:
    print(f"Error starting SUMO simulation: {e}")
    exit()

# Initialize dictionaries to track waiting time and speed per junction
junction_waiting_times = {}
junction_speeds = {}
emergency_vehicle_count = 0
emergency_vehicle_waiting_time = 0
total_reward = 0

# Lane-to-junction mapping (you need to update this manually based on your network)
lane_to_junction = {
    "-E6": "J1",
    "-E1": "J1",
    "E0": "J2",
    "E1": "J2",
    "E6": "J2",
}

# Initialize junction data storage
for junction in set(lane_to_junction.values()):
    junction_waiting_times[junction] = []
    junction_speeds[junction] = []

# Simulation loop
step = 0
while step < 50:  # Run for 50 simulation steps
    traci.simulationStep()

    for tls_id in traci.trafficlight.getIDList():
        current_phase = traci.trafficlight.getPhase(tls_id)
        phase_color = {0: "Green", 1: "Yellow", 2: "Red"}.get(current_phase, "Unknown")
        print(f"Traffic light {tls_id} is {phase_color}")

    # Compute waiting time and speed per junction
    for lane_id in traci.lane.getIDList():
        if lane_id in lane_to_junction:
            junction = lane_to_junction[lane_id]

            # Get waiting times
            waiting_time = sum(traci.vehicle.getWaitingTime(veh) for veh in traci.lane.getLastStepVehicleIDs(lane_id))
            junction_waiting_times[junction].append(waiting_time)

            # Get speed
            speed = sum(traci.vehicle.getSpeed(veh) for veh in traci.lane.getLastStepVehicleIDs(lane_id))
            vehicle_count = len(traci.lane.getLastStepVehicleIDs(lane_id))
            junction_speeds[junction].append(speed / vehicle_count if vehicle_count else 0)

    # Count emergency vehicles and their waiting time
    for veh_id in traci.vehicle.getIDList():
        if traci.vehicle.getTypeID(veh_id) == 'ambulance':
            emergency_vehicle_count += 1
            waiting_time = traci.vehicle.getWaitingTime(veh_id)
            emergency_vehicle_waiting_time += waiting_time
            print(f"Emergency vehicle {veh_id} waiting time: {waiting_time}")

    # Calculate reward based on congestion (negative reward for congestion)
    total_reward -= sum(traci.lane.getLastStepVehicleNumber(lane_id) for lane_id in traci.lane.getIDList())

    step += 1

# Compute averages
average_waiting_time_per_junction = {
    junc: (sum(times) / len(times) if times else 0) for junc, times in junction_waiting_times.items()
}
average_speed_per_junction = {
    junc: (sum(speeds) / len(speeds) if speeds else 0) for junc, speeds in junction_speeds.items()
}
average_emergency_vehicle_waiting_time = (
    emergency_vehicle_waiting_time / emergency_vehicle_count if emergency_vehicle_count else 0
)

# Stop simulation
traci.close()
print("SUMO simulation ended.")

# Print the final results
print(f"Total Reward: {total_reward}")
print("Average Waiting Time Per Junction:")
for junc, avg_time in average_waiting_time_per_junction.items():
    print(f"  Junction {junc}: {avg_time:.2f} sec")

print("Average Speed Per Junction:")
for junc, avg_speed in average_speed_per_junction.items():
    print(f"  Junction {junc}: {avg_speed:.2f} m/s")

print(f"Emergency Vehicles Detected: {emergency_vehicle_count}")
print(f"Average Emergency Vehicle Waiting Time: {average_emergency_vehicle_waiting_time:.2f} sec")
