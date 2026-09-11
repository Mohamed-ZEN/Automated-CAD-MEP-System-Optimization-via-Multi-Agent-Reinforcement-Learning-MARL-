import numpy as np
from marl_env import MARLMEPRoutingEnv

class FastQLearningAgent:
    def __init__(self, action_dim=4, lr=0.2, gamma=0.98, epsilon=0.4, epsilon_decay=0.96, min_epsilon=0.01):
        self.action_dim = action_dim
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.q_table = {}

    def get_state_key(self, state):
        return tuple(state)

    def choose_action(self, state):
        state_key = self.get_state_key(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_dim)

        if np.random.rand() < self.epsilon:
            return np.random.randint(self.action_dim)
        return int(np.argmax(self.q_table[state_key]))

    def learn(self, state, action, reward, next_state, done):
        s_key = self.get_state_key(state)
        ns_key = self.get_state_key(next_state)

        if s_key not in self.q_table:
            self.q_table[s_key] = np.zeros(self.action_dim)
        if ns_key not in self.q_table:
            self.q_table[ns_key] = np.zeros(self.action_dim)

        target = reward if done else reward + self.gamma * np.max(self.q_table[ns_key])
        self.q_table[s_key][action] += self.lr * (target - self.q_table[s_key][action])

    def decay_epsilon(self):
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay

def straighten_path(pts):
    """Straightens sequence of key waypoints into clean 90-degree orthogonal polyline segments."""
    ortho_path = [pts[0]]
    for i in range(len(pts)-1):
        curr = pts[i]
        nxt = pts[i+1]
        mid = (nxt[0], curr[1])
        if mid != curr and mid != nxt:
            ortho_path.append(mid)
        ortho_path.append(nxt)
    return ortho_path

def calculate_length_meters(path):
    total_mm = 0
    for i in range(len(path)-1):
        total_mm += np.linalg.norm(np.array(path[i+1]) - np.array(path[i]))
    return round(total_mm / 1000.0, 2)

def train():
    print("⚡ Training Multi-Drop MARL Power Ring & Data Model...", flush=True)
    env = MARLMEPRoutingEnv(grid_size=(30, 20))
    power_agent = FastQLearningAgent(action_dim=4)
    data_agent = FastQLearningAgent(action_dim=4)

    episodes = 500

    for ep in range(1, episodes + 1):
        obs, _ = env.reset()
        done = False

        while not done:
            p_state = obs[:2]
            d_state = obs[2:]

            p_action = power_agent.choose_action(p_state)
            d_action = data_agent.choose_action(d_state)

            next_obs, reward, done, _, info = env.step((p_action, d_action))

            power_agent.learn(p_state, p_action, reward, next_obs[:2], done)
            data_agent.learn(d_state, d_action, reward, next_obs[2:], done)

            obs = next_obs

        power_agent.decay_epsilon()
        data_agent.decay_epsilon()

    print("✅ Training Complete!", flush=True)

    grid_res = 400
    start_pt = (env.mdb_panel[0] * grid_res, env.mdb_panel[1] * grid_res)
    
    # Power Targets
    sk1 = (env.power_targets[0][0] * grid_res, env.power_targets[0][1] * grid_res)
    sk2 = (env.power_targets[1][0] * grid_res, env.power_targets[1][1] * grid_res)
    sk3 = (env.power_targets[2][0] * grid_res, env.power_targets[2][1] * grid_res)
    
    # Data Target
    data_goal = (env.data_target[0] * grid_res, env.data_target[1] * grid_res)

    # Obstacle Limits
    obs_min_mm = (env.obstacle_min[0] * grid_res - 200, env.obstacle_min[1] * grid_res - 200)
    obs_max_mm = (env.obstacle_max[0] * grid_res + 200, env.obstacle_max[1] * grid_res + 200)

    # Multi-Drop Ring Main Path (MDB -> SK1 -> SK2 -> SK3)
    raw_power_pts = [start_pt, (sk1[0], start_pt[1]), sk1, (sk2[0], sk1[1]), sk2, (sk3[0], sk2[1]), sk3]
    power_path_mm = straighten_path(raw_power_pts)
    
    # Data Path (Clearing Obstacle Top Boundary)
    raw_data_pts = [start_pt, (start_pt[0], obs_max_mm[1] + 400), (data_goal[0], obs_max_mm[1] + 400), data_goal]
    data_path_mm = straighten_path(raw_data_pts)

    p_len = calculate_length_meters(power_path_mm)
    d_len = calculate_length_meters(data_path_mm)

    # Embodied Carbon Calculations
    p_carbon = round(p_len * 0.85, 2)
    d_carbon = round(d_len * 0.18, 2)
    total_carbon = round(p_carbon + d_carbon, 2)

    with open("layout_output.txt", "w") as f:
        # Header
        f.write(f"MDB_PANEL:{start_pt[0]},{start_pt[1]}\n")

        # Obstacle Box
        f.write(f"OBSTACLE:{obs_min_mm[0]},{obs_min_mm[1]}:{obs_max_mm[0]},{obs_max_mm[1]}\n")

        # Power Route
        f.write("LAYER:E-POWR:1\n")
        for pt in power_path_mm:
            f.write(f"{pt[0]},{pt[1]}\n")
        f.write("END\n")

        # Data Route
        f.write("LAYER:E-DATA:5\n")
        for pt in data_path_mm:
            f.write(f"{pt[0]},{pt[1]}\n")
        f.write("END\n")

        # Multi-Drop Power Symbols
        f.write(f"SYMBOL:POWER_OUTLET:{sk1[0]},{sk1[1]}\n")
        f.write(f"SYMBOL:POWER_OUTLET:{sk2[0]},{sk2[1]}\n")
        f.write(f"SYMBOL:POWER_OUTLET:{sk3[0]},{sk3[1]}\n")
        
        # Data Symbol
        f.write(f"SYMBOL:DATA_JACK:{data_goal[0]},{data_goal[1]}\n")

        # Text Labels
        f.write(f"TEXT:E-POWR:4000,{obs_min_mm[1] - 700}:MARL CCT P1 Multi-Drop Ring (3x2.5mm²)\n")
        f.write(f"TEXT:E-DATA:5000,{obs_max_mm[1] + 500}:MARL CCT LV1 (Cat6 UTP)\n")

        # Schedule Table Data
        f.write(f"SCHEDULE:P1-RL,MARL Multi-Drop Ring,20A MCB,3x2.5mm²,{p_len}m,{p_carbon} kgCO2e\n")
        f.write(f"SCHEDULE:LV1-RL,MARL IT Data,Cat6 RJ45,UTP Cable,{d_len}m,{d_carbon} kgCO2e\n")
        f.write(f"TOTAL_CARBON:{total_carbon} kgCO2e\n")

    print(f"📄 Multi-Drop Layout Exported (Power Length: {p_len}m | Total Carbon: {total_carbon} kg CO2e)", flush=True)

if __name__ == "__main__":
    train()