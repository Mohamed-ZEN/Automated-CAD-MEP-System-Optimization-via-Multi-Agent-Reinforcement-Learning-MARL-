import gymnasium as gym
from gymnasium import spaces
import numpy as np

class MARLMEPRoutingEnv(gym.Env):
    """
    Multi-Agent MEP Routing Environment: Multi-Drop Power Ring & Data Outlet
    """
    def __init__(self, grid_size=(30, 20), emc_clearance=2):
        super(MARLMEPRoutingEnv, self).__init__()
        
        self.grid_size = grid_size
        self.emc_clearance = emc_clearance
        
        self.action_space = spaces.Tuple([
            spaces.Discrete(4),
            spaces.Discrete(4)
        ])
        
        self.observation_space = spaces.Box(
            low=0, high=max(grid_size), shape=(4,), dtype=np.int32
        )
        
        self.action_to_direction = {
            0: np.array([0, 1]),   # Up
            1: np.array([1, 0]),   # Right
            2: np.array([0, -1]),  # Down
            3: np.array([-1, 0])   # Left
        }
        
        # Grid Coordinates aligned with CAD layout
        self.mdb_panel = np.array([3, 10])        # MDB Panel (Left)
        self.power_targets = [
            np.array([10, 3]),                    # Socket 1 (Bottom Left)
            np.array([25, 4]),                    # Socket 2 (Bottom Right)
            np.array([25, 12])                    # Socket 3 (Mid Right)
        ]
        self.data_target = np.array([25, 17])     # Data Outlet (Top Right)
        
        # Central Architectural Obstacle (Grid Coordinates)
        self.obstacle_min = np.array([12, 6])
        self.obstacle_max = np.array([16, 14])

    def is_in_obstacle(self, pos):
        return (self.obstacle_min[0] <= pos[0] <= self.obstacle_max[0]) and \
               (self.obstacle_min[1] <= pos[1] <= self.obstacle_max[1])
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self.agent0_pos = self.mdb_panel.copy()
        self.agent1_pos = self.mdb_panel.copy()
        
        self.p_target_idx = 0
        
        self.power_path = [tuple(self.agent0_pos)]
        self.data_path = [tuple(self.agent1_pos)]
        
        self.power_done = False
        self.data_done = False
        
        obs = np.hstack([self.agent0_pos, self.agent1_pos])
        return obs, {}

    def step(self, actions):
        p_action, d_action = actions
        
        curr_p_target = self.power_targets[self.p_target_idx] if not self.power_done else self.power_targets[-1]
        
        p_prev_dist = np.sum(np.abs(self.agent0_pos - curr_p_target))
        d_prev_dist = np.sum(np.abs(self.agent1_pos - self.data_target))

        # --- Power Agent (Sequential Multi-Drop Routing) ---
        if not self.power_done:
            p_move = self.action_to_direction[p_action]
            next_p = np.clip(self.agent0_pos + p_move, [0, 0], [self.grid_size[0]-1, self.grid_size[1]-1])
            
            if self.is_in_obstacle(next_p):
                r_power_obs = -20.0
            else:
                self.agent0_pos = next_p
                r_power_obs = 0.0
                
            self.power_path.append(tuple(self.agent0_pos))
            
            # Check drop achievement
            if np.array_equal(self.agent0_pos, curr_p_target):
                self.p_target_idx += 1
                if self.p_target_idx >= len(self.power_targets):
                    self.power_done = True
                else:
                    curr_p_target = self.power_targets[self.p_target_idx]
        else:
            r_power_obs = 0.0

        # --- Data Agent ---
        if not self.data_done:
            d_move = self.action_to_direction[d_action]
            next_d = np.clip(self.agent1_pos + d_move, [0, 0], [self.grid_size[0]-1, self.grid_size[1]-1])
            
            if self.is_in_obstacle(next_d):
                r_data_obs = -20.0
            else:
                self.agent1_pos = next_d
                r_data_obs = 0.0
                
            self.data_path.append(tuple(self.agent1_pos))
            if np.array_equal(self.agent1_pos, self.data_target):
                self.data_done = True
        else:
            r_data_obs = 0.0

        p_curr_dist = np.sum(np.abs(self.agent0_pos - curr_p_target))
        d_curr_dist = np.sum(np.abs(self.agent1_pos - self.data_target))

        r_power = (p_prev_dist - p_curr_dist) * 10.0 - 0.5 + r_power_obs
        r_data = (d_prev_dist - d_curr_dist) * 10.0 - 0.5 + r_data_obs

        if self.power_done: r_power += 200.0
        if self.data_done: r_data += 150.0

        # EMC Clearance Penalty
        emc_violation = False
        for p_pt in self.power_path:
            dist = np.linalg.norm(np.array(self.agent1_pos) - np.array(p_pt))
            if dist < self.emc_clearance:
                emc_violation = True
                break
                
        if emc_violation:
            r_data -= 10.0  

        total_reward = r_power + r_data
        done = self.power_done and self.data_done
        truncated = len(self.power_path) > 120
        
        obs = np.hstack([self.agent0_pos, self.agent1_pos])
        return obs, total_reward, done or truncated, False, {}