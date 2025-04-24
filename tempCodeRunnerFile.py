import traci
import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim

# Define the Q-learning agent
class QLearningAgent:
    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.5, exploration_decay=0.99, min_exploration_rate=0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = min_exploration_rate
        self.q_table = np.zeros((state_size, action_size))

    def choose_action(self, state):
        if np.random.rand() < self.exploration_rate:
            return np.random.randint(self.action_size)
        return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.discount_factor * self.q_table[next_state, best_next_action]
        td_error = td_target - self.q_table[state, action]
        self.q_table[state, action] += self.learning_rate * td_error
        self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate * self.exploration_decay)

# Function to extract traffic data from SUMO
def get_traffic_data():
    lane_ids = traci.lane.getIDList()
    traffic_data = []
    for lane_id in lane_ids:
        vehicle_count = traci.lane.getLastStepVehicleNumber(lane_id)
        emergency_vehicle_count = sum(1 for v in traci.lane.getLastStepVehicleIDs(lane_id) if traci.vehicle.getTypeID(v) == 'ambulance')
        traffic_data.append((vehicle_count, emergency_vehicle_count))
    return np.array(traffic_data)

# Function to run the simulation and adjust traffic lights
def run_rl_simulation(sumo_cfg, agent, steps=1000):
    try:
        traci.start(["sumo-gui", "-c", sumo_cfg])  # Using sumo-gui for real-time visualization
        total_reward = 0
        
        for step in range(steps):
            traci.simulationStep()
            traffic_data = get_traffic_data()
            state = traffic_data.sum(axis=0)  # Simplified state representation
            action = agent.choose_action(state[0])  # Use total vehicle count for action selection
            set_traffic_light(action, traffic_data)
            reward = -state[0]  # Reward is negative congestion
            next_traffic_data = get_traffic_data()
            next_state = next_traffic_data.sum(axis=0)
            agent.learn(state[0], action, reward, next_state[0])
            total_reward += reward
        
        traci.close()
        return total_reward
    except traci.exceptions.FatalTraCIError as e:
        print(f"FatalTraCIError: {e}")
        traci.close()

# Function to set traffic light based on action and prioritize ambulances
def set_traffic_light(action, traffic_data):
    tls_ids = ["J1", "J2"]  # Traffic light IDs
    states = [
        "GGGgrrrGGGgrrr",  # Green for main road
        "rrrrGGgrrrrGGg",  # Green for side road
        "yyyyrrryyyyrrr",  # Yellow for main road
        "rrrryyyrrrryyy"   # Yellow for side road
    ]
    for tls_id in tls_ids:
        if traffic_data[:, 1].sum() > 0:  # If there are any ambulances
            print(f"Traffic Light {tls_id}: Setting state to GGGgrrrGGGgrrr due to ambulance presence.")
            traci.trafficlight.setRedYellowGreenState(tls_id, "GGGgrrrGGGgrrr")  # Prioritize main road
            for lane_id in traci.trafficlight.getControlledLanes(tls_id):
                for veh_id in traci.lane.getLastStepVehicleIDs(lane_id):
                    if traci.vehicle.getTypeID(veh_id) == 'ambulance':
                        traci.vehicle.setSpeed(veh_id, traci.vehicle.getMaxSpeed(veh_id))  # Allow ambulance to go
                        # Make normal vehicles change lane
                        for veh in traci.lane.getLastStepVehicleIDs(lane_id):
                            if traci.vehicle.getTypeID(veh) != 'ambulance':
                                try:
                                    traci.vehicle.changeLane(veh, 1, 25.0)  # Change to the next lane with a duration of 25 seconds
                                    print(f"Vehicle {veh} changed lane to allow ambulance to pass.")
                                except traci.exceptions.TraCIException:
                                    print(f"Vehicle {veh} could not change lane.")
        elif traffic_data[:, 0].sum() == 0:  # If there is no traffic
            print(f"Traffic Light {tls_id}: Setting state to GGGgrrrGGGgrrr due to no traffic.")
            traci.trafficlight.setRedYellowGreenState(tls_id, "GGGgrrrGGGgrrr")  # Set lights to green
        else:
            print(f"Traffic Light {tls_id}: Setting state to {states[action]} based on traffic conditions.")
            traci.trafficlight.setRedYellowGreenState(tls_id, states[action])

# Main function
def main():
    sumo_cfg = "C:/Users/ankit/Desktop/Progress/V2V/DAY__05/sumocfg.sumo.cfg"  # Adjust the path to your SUMO config file
    steps = 1000  # Number of simulation steps

    # Initialize Q-learning agent
    state_size = 100  # Simplified state space size
    action_size = 4  # Four possible actions: "GGGgrrrGGGgrrr", "rrrrGGgrrrrGGg", "yyyyrrryyyyrrr", "rrrryyyrrrryyy"
    agent = QLearningAgent(state_size, action_size)

    # Run the simulation with reinforcement learning
    total_reward = run_rl_simulation(sumo_cfg, agent, steps)
    print(f"Total Reward: {total_reward}")

if __name__ == "__main__":
    main()