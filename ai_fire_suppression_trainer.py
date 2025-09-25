#!/usr/bin/env python3
"""
AI Fire Suppression Training System
Uses Reinforcement Learning to optimize fire truck deployment and suppression strategies
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
import json
from datetime import datetime
import csv
from gis_enhanced_forest_fire_simulation import VEHICLE_TYPES, TableMountainGIS

class FireSuppressionEnvironment:
    """
    Reinforcement Learning environment for fire suppression training
    """
    def __init__(self):
        self.gis = TableMountainGIS()
        self.grid_size = 20  # 20x20 grid representation
        self.max_fires = 50
        self.max_vehicles = 20
        self.time_steps = 96  # 24 hours in 15-min intervals
        self.current_step = 0
        self.reset()
        
    def reset(self):
        """Reset environment for new episode"""
        self.current_step = 0
        self.fires = []  # List of active fires
        self.vehicles = []  # List of deployed vehicles
        self.suppressed_fires = 0
        self.total_damage = 0
        self.fuel_used = 0
        self.response_times = []
        
        # Generate initial fires
        self._generate_initial_fires()
        return self._get_state()
    
    def _generate_initial_fires(self):
        """Generate random initial fire locations"""
        num_fires = random.randint(5, 15)
        for _ in range(num_fires):
            lat = random.uniform(-33.977523, -33.937334)
            lon = random.uniform(18.391285, 18.437977)
            intensity = random.uniform(300, 800)  # Fire temperature
            spread_rate = random.uniform(0.1, 0.8)
            
            self.fires.append({
                'id': len(self.fires),
                'lat': lat,
                'lon': lon,
                'intensity': intensity,
                'spread_rate': spread_rate,
                'age': 0,
                'suppressed': False
            })
    
    def _get_state(self):
        """Convert environment to state vector for AI"""
        state = np.zeros((self.grid_size, self.grid_size, 6))  # 6 channels
        
        # Grid bounds
        lat_min, lat_max = -33.977523, -33.937334
        lon_min, lon_max = 18.391285, 18.437977
        
        # Channel 0: Fire intensity
        # Channel 1: Fire spread rate
        # Channel 2: Fire age
        # Channel 3: Vehicle presence
        # Channel 4: Vehicle capacity
        # Channel 5: Distance to nearest station
        
        for fire in self.fires:
            if not fire['suppressed']:
                # Convert lat/lon to grid coordinates
                grid_lat = int((fire['lat'] - lat_min) / (lat_max - lat_min) * (self.grid_size - 1))
                grid_lon = int((fire['lon'] - lon_min) / (lon_max - lon_min) * (self.grid_size - 1))
                
                grid_lat = max(0, min(self.grid_size - 1, grid_lat))
                grid_lon = max(0, min(self.grid_size - 1, grid_lon))
                
                state[grid_lat, grid_lon, 0] = min(1.0, fire['intensity'] / 1000)  # Normalized intensity
                state[grid_lat, grid_lon, 1] = fire['spread_rate']
                state[grid_lat, grid_lon, 2] = min(1.0, fire['age'] / 24)  # Normalized age
        
        # Add vehicle information
        for vehicle in self.vehicles:
            grid_lat = int((vehicle['lat'] - lat_min) / (lat_max - lat_min) * (self.grid_size - 1))
            grid_lon = int((vehicle['lon'] - lon_min) / (lon_max - lon_min) * (self.grid_size - 1))
            
            grid_lat = max(0, min(self.grid_size - 1, grid_lat))
            grid_lon = max(0, min(self.grid_size - 1, grid_lon))
            
            state[grid_lat, grid_lon, 3] = 1.0  # Vehicle present
            state[grid_lat, grid_lon, 4] = min(1.0, vehicle['capacity'] / 20000)  # Normalized capacity
        
        # Add fire station distances
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Convert grid back to lat/lon
                lat = lat_min + (i / (self.grid_size - 1)) * (lat_max - lat_min)
                lon = lon_min + (j / (self.grid_size - 1)) * (lon_max - lon_min)
                
                # Find nearest station
                nearest_station, distance = self.gis.get_nearest_fire_station(lat, lon)
                state[i, j, 5] = min(1.0, distance / 50)  # Normalized distance (max 50km)
        
        return state.flatten()
    
    def step(self, action):
        """Execute action and return new state, reward, done"""
        reward = 0
        done = False
        
        # Decode action: [vehicle_type, target_fire, deploy/redeploy]
        vehicle_type_idx = action % len(VEHICLE_TYPES)
        fire_idx = (action // len(VEHICLE_TYPES)) % len(self.fires)
        deploy_action = (action // (len(VEHICLE_TYPES) * len(self.fires))) % 2
        
        vehicle_type = list(VEHICLE_TYPES.keys())[vehicle_type_idx]
        
        if fire_idx < len(self.fires) and not self.fires[fire_idx]['suppressed']:
            target_fire = self.fires[fire_idx]
            
            # Deploy vehicle if action is deploy
            if deploy_action == 1:
                success = self._deploy_vehicle(vehicle_type, target_fire)
                if success:
                    reward += 10  # Reward for successful deployment
                else:
                    reward -= 2   # Penalty for failed deployment
        
        # Update fire spread and suppression
        self._update_fires()
        
        # Update vehicles
        self._update_vehicles()
        
        # Calculate reward based on performance
        reward += self._calculate_reward()
        
        self.current_step += 1
        done = (self.current_step >= self.time_steps) or (len([f for f in self.fires if not f['suppressed']]) == 0)
        
        return self._get_state(), reward, done
    
    def _deploy_vehicle(self, vehicle_type, target_fire):
        """Deploy vehicle to target fire"""
        # Find nearest station
        nearest_station, distance = self.gis.get_nearest_fire_station(target_fire['lat'], target_fire['lon'])
        
        # Check if vehicle is available and within range
        vehicle_specs = VEHICLE_TYPES[vehicle_type]
        if distance <= vehicle_specs['max_range_km']:
            # Deploy vehicle
            vehicle = {
                'type': vehicle_type,
                'lat': target_fire['lat'],
                'lon': target_fire['lon'],
                'target_fire': target_fire['id'],
                'capacity': vehicle_specs['capacity'],
                'effectiveness': vehicle_specs['effective_rate'],
                'arrival_time': self.current_step + (distance / vehicle_specs['speed']),
                'suppression_time': 0
            }
            self.vehicles.append(vehicle)
            self.fuel_used += distance * 2  # Round trip fuel cost
            return True
        return False
    
    def _update_fires(self):
        """Update fire spread and intensity"""
        for fire in self.fires:
            if not fire['suppressed']:
                # Fire spreads and intensifies over time
                fire['age'] += 1
                fire['intensity'] *= (1 + fire['spread_rate'] * 0.1)  # Growth rate
                fire['intensity'] = min(fire['intensity'], 1200)  # Max intensity cap
                
                # Check for suppression by nearby vehicles
                for vehicle in self.vehicles:
                    if (vehicle['target_fire'] == fire['id'] and 
                        vehicle['arrival_time'] <= self.current_step):
                        
                        # Calculate suppression effectiveness
                        suppression_power = vehicle['effectiveness'] * (vehicle['capacity'] / 10000)
                        fire['intensity'] *= (1 - suppression_power * 0.3)
                        
                        vehicle['suppression_time'] += 1
                        
                        # Check if fire is extinguished
                        if fire['intensity'] < 100:
                            fire['suppressed'] = True
                            self.suppressed_fires += 1
                            break
    
    def _update_vehicles(self):
        """Update vehicle status and remove completed vehicles"""
        self.vehicles = [v for v in self.vehicles if v['suppression_time'] < 20]  # Remove after 20 time steps
    
    def _calculate_reward(self):
        """Calculate reward based on fire suppression performance"""
        reward = 0
        
        # Reward for suppressed fires
        reward += self.suppressed_fires * 50
        
        # Penalty for active fires
        active_fires = len([f for f in self.fires if not f['suppressed']])
        reward -= active_fires * 2
        
        # Penalty for high intensity fires
        total_intensity = sum(f['intensity'] for f in self.fires if not f['suppressed'])
        reward -= total_intensity * 0.01
        
        # Efficiency bonus (fewer vehicles, less fuel)
        reward -= len(self.vehicles) * 1
        reward -= self.fuel_used * 0.1
        
        return reward

class FireSuppressionDQN(nn.Module):
    """
    Deep Q-Network for fire suppression strategy
    """
    def __init__(self, state_size, action_size, hidden_size=512):
        super(FireSuppressionDQN, self).__init__()
        
        self.conv1 = nn.Conv1d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv1d(64, 128, kernel_size=3, padding=1)
        
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, action_size)
        
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout(x)
        x = torch.relu(self.fc3(x))
        x = self.fc4(x)
        return x

class FireSuppressionAgent:
    """
    AI Agent for learning optimal fire suppression strategies
    """
    def __init__(self, state_size, action_size, learning_rate=0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=10000)
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = learning_rate
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Neural networks
        self.q_network = FireSuppressionDQN(state_size, action_size).to(self.device)
        self.target_network = FireSuppressionDQN(state_size, action_size).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Training metrics
        self.training_scores = []
        self.training_losses = []
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        """Choose action using epsilon-greedy policy"""
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        q_values = self.q_network(state_tensor)
        return np.argmax(q_values.cpu().data.numpy())
    
    def replay(self, batch_size=32):
        """Train the agent on a batch of experiences"""
        if len(self.memory) < batch_size:
            return
        
        batch = random.sample(self.memory, batch_size)
        states = torch.FloatTensor([e[0] for e in batch]).to(self.device)
        actions = torch.LongTensor([e[1] for e in batch]).to(self.device)
        rewards = torch.FloatTensor([e[2] for e in batch]).to(self.device)
        next_states = torch.FloatTensor([e[3] for e in batch]).to(self.device)
        dones = torch.BoolTensor([e[4] for e in batch]).to(self.device)
        
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (0.95 * next_q_values * ~dones)
        
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss.item()
    
    def update_target_network(self):
        """Update target network with current network weights"""
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def save_model(self, filename):
        """Save trained model"""
        torch.save({
            'q_network': self.q_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_scores': self.training_scores,
            'training_losses': self.training_losses
        }, filename)
    
    def load_model(self, filename):
        """Load trained model"""
        checkpoint = torch.load(filename, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['q_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint['epsilon']
        self.training_scores = checkpoint.get('training_scores', [])
        self.training_losses = checkpoint.get('training_losses', [])

def train_fire_suppression_ai(episodes=1000):
    """
    Train AI agent to optimize fire suppression strategies
    """
    env = FireSuppressionEnvironment()
    state_size = env.grid_size * env.grid_size * 6  # Flattened grid with 6 channels
    action_size = len(VEHICLE_TYPES) * env.max_fires * 2  # Vehicle types × fires × deploy actions
    
    agent = FireSuppressionAgent(state_size, action_size)
    
    print("🤖 STARTING AI FIRE SUPPRESSION TRAINING")
    print(f"State size: {state_size}")
    print(f"Action space: {action_size}")
    print(f"Training episodes: {episodes}")
    print("="*60)
    
    scores = []
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        steps = 0
        
        while True:
            action = agent.act(state)
            next_state, reward, done = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            
            state = next_state
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        scores.append(total_reward)
        agent.training_scores.append(total_reward)
        
        # Train the agent
        if len(agent.memory) > 32:
            loss = agent.replay()
            if loss:
                agent.training_losses.append(loss)
        
        # Update target network periodically
        if episode % 100 == 0:
            agent.update_target_network()
        
        # Print progress
        if episode % 100 == 0:
            avg_score = np.mean(scores[-100:])
            print(f"Episode {episode:4d} | Avg Score: {avg_score:8.2f} | Epsilon: {agent.epsilon:.3f} | "
                  f"Fires Suppressed: {env.suppressed_fires:2d} | Steps: {steps:3d}")
    
    # Save trained model
    model_filename = f"fire_suppression_ai_model_{datetime.now().strftime('%Y%m%d_%H%M')}.pth"
    agent.save_model(model_filename)
    
    print(f"\n🎯 TRAINING COMPLETE!")
    print(f"Model saved as: {model_filename}")
    print(f"Final average score: {np.mean(scores[-100:]):.2f}")
    
    return agent, env

def test_ai_performance(agent, episodes=10):
    """
    Test trained AI agent performance
    """
    env = FireSuppressionEnvironment()
    agent.epsilon = 0  # No exploration during testing
    
    results = []
    
    print("\n🔬 TESTING AI PERFORMANCE")
    print("="*40)
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        initial_fires = len(env.fires)
        
        while True:
            action = agent.act(state)
            state, reward, done = env.step(action)
            total_reward += reward
            
            if done:
                break
        
        suppression_rate = env.suppressed_fires / initial_fires if initial_fires > 0 else 0
        
        results.append({
            'episode': episode,
            'total_reward': total_reward,
            'initial_fires': initial_fires,
            'suppressed_fires': env.suppressed_fires,
            'suppression_rate': suppression_rate,
            'fuel_used': env.fuel_used,
            'vehicles_deployed': len(env.vehicles)
        })
        
        print(f"Test {episode+1:2d} | Reward: {total_reward:8.1f} | "
              f"Suppressed: {env.suppressed_fires:2d}/{initial_fires:2d} ({suppression_rate:.1%}) | "
              f"Fuel: {env.fuel_used:.1f}")
    
    # Performance summary
    avg_suppression_rate = np.mean([r['suppression_rate'] for r in results])
    avg_reward = np.mean([r['total_reward'] for r in results])
    avg_fuel = np.mean([r['fuel_used'] for r in results])
    
    print(f"\n📊 PERFORMANCE SUMMARY:")
    print(f"Average Suppression Rate: {avg_suppression_rate:.1%}")
    print(f"Average Reward: {avg_reward:.1f}")
    print(f"Average Fuel Used: {avg_fuel:.1f}")
    
    return results

if __name__ == "__main__":
    print("🔥 AI Fire Suppression Training System")
    print("Choose an option:")
    print("1. Train new AI model")
    print("2. Test existing model")
    print("3. Quick demo training (100 episodes)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        episodes = int(input("Enter number of training episodes (default 1000): ") or "1000")
        agent, env = train_fire_suppression_ai(episodes)
        test_ai_performance(agent)
        
    elif choice == "2":
        model_file = input("Enter model filename: ").strip()
        try:
            env = FireSuppressionEnvironment()
            state_size = env.grid_size * env.grid_size * 6
            action_size = len(VEHICLE_TYPES) * env.max_fires * 2
            agent = FireSuppressionAgent(state_size, action_size)
            agent.load_model(model_file)
            test_ai_performance(agent)
        except FileNotFoundError:
            print(f"Model file '{model_file}' not found!")
            
    elif choice == "3":
        print("Running quick demo training...")
        agent, env = train_fire_suppression_ai(100)
        test_ai_performance(agent, 5)
    
    else:
        print("Invalid choice!")