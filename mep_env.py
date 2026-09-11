import numpy as np

class SimpleMEPEnvironment:
    def __init__(self):
        # 10cm grid cells for a 9.7m x 11.5m space
        self.grid_res = 0.10  # 10 cm in meters
        
        # Initial positions [Y, X] on grid
        self.mdb_pos = np.array([50, 48])      # Panel at center
        self.power_pos = np.array([50, 48])    # Power starts at MDB
        self.data_pos = np.array([50, 48])     # Data starts at MDB

    def check_emc_clearance(self):
        # Calculate distance between Power and Data cables in meters
        distance_cells = np.linalg.norm(self.power_pos - self.data_pos)
        distance_meters = distance_cells * self.grid_res
        
        print(f"Current Power-to-Data Clearance: {distance_meters:.2f} meters ({distance_meters * 1000:.0f} mm)")
        
        # IEC 60364-4-44 Rule: Must be >= 300mm (0.30 meters)
        if distance_meters < 0.30 and not np.array_equal(self.power_pos, self.data_pos):
            print("❌ VIOLATION: EMC clearance less than 300mm!")
            return False
        else:
            print("✅ COMPLIANT: Clearance is safe or at starting panel.")
            return True

if __name__ == "__main__":
    env = SimpleMEPEnvironment()
    
    # Test 1: Move Data agent 50cm to the right (5 grid cells)
    env.data_pos = np.array([50, 53])
    print("--- Test 1 (500mm separation) ---")
    env.check_emc_clearance()
    
    # Test 2: Move Data agent to 10cm from Power agent
    env.data_pos = np.array([50, 49])
    print("\n--- Test 2 (100mm separation) ---")
    env.check_emc_clearance()