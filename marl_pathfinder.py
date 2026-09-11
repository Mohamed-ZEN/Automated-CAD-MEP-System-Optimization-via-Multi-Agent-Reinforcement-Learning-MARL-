import heapq
import numpy as np

# 1. A* Pathfinding Algorithm
def astar_pathfind(start, goal, obstacles, grid_size=(100, 100)):
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: np.linalg.norm(np.array(start) - np.array(goal))}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start, None))
    
    while oheap:
        _, current, last_dir = heapq.heappop(oheap)

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            data.append(start)
            return data[::-1]

        close_set.add(current)
        for i, j in neighbors:
            neighbor = (current[0] + i, current[1] + j)
            move_dir = (i, j)
            
            if 0 <= neighbor[0] < grid_size[0] and 0 <= neighbor[1] < grid_size[1]:
                if neighbor in obstacles or neighbor in close_set:
                    continue
            else:
                continue
            
            turn_penalty = 0 if (last_dir is None or last_dir == move_dir) else 15
            tentative_g_score = gscore[current] + 1 + turn_penalty
            
            if neighbor not in [item[1] for item in oheap] or tentative_g_score < gscore.get(neighbor, float('inf')):
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + np.linalg.norm(np.array(neighbor) - np.array(goal))
                heapq.heappush(oheap, (fscore[neighbor], neighbor, move_dir))
                
    return None

def compress_path(path):
    if not path or len(path) < 3:
        return path
    compressed = [path[0]]
    for i in range(1, len(path) - 1):
        p_dir = (path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
        n_dir = (path[i+1][0] - path[i][0], path[i+1][1] - path[i][1])
        if p_dir != n_dir:
            compressed.append(path[i])
    compressed.append(path[-1])
    return compressed

# Calculate total length of polyline in meters
def calculate_length_meters(path, res=100):
    total_mm = 0
    for i in range(len(path)-1):
        total_mm += np.linalg.norm(np.array(path[i+1]) - np.array(path[i])) * res
    return round(total_mm / 1000.0, 2)

# Grid & Setup
grid_resolution = 100 
start_point = (48, 50)  
power_goal = (85, 21)   
data_goal = (91, 70)    

obstacles = set()
for y in range(35, 65):  
    obstacles.add((60, y))

# Compute Paths
raw_power_path = astar_pathfind(start_point, power_goal, obstacles)
clean_power_path = compress_path(raw_power_path)
power_length = calculate_length_meters(clean_power_path)

data_obstacles = obstacles.copy()
for pt in raw_power_path:
    if np.linalg.norm(np.array(pt) - np.array(start_point)) > 3:
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                data_obstacles.add((pt[0] + dx, pt[1] + dy))

raw_data_path = astar_pathfind(start_point, data_goal, data_obstacles)
clean_data_path = compress_path(raw_data_path)
data_length = calculate_length_meters(clean_data_path)

# Export Full CAD Contract
with open("layout_output.txt", "w") as f:
    # Power Route
    f.write("LAYER:E-POWR:1\n")
    for pt in clean_power_path:
        f.write(f"{pt[0]*grid_resolution},{pt[1]*grid_resolution}\n")
    f.write("END\n")
    
    # Data Route
    f.write("LAYER:E-DATA:5\n")
    for pt in clean_data_path:
        f.write(f"{pt[0]*grid_resolution},{pt[1]*grid_resolution}\n")
    f.write("END\n")
    
    # Symbols & Equipment Terminations
    f.write(f"SYMBOL:POWER_OUTLET:{power_goal[0]*grid_resolution},{power_goal[1]*grid_resolution}\n")
    f.write(f"SYMBOL:DATA_JACK:{data_goal[0]*grid_resolution},{data_goal[1]*grid_resolution}\n")
    
    # Annotations & Tags
    p_mid = clean_power_path[len(clean_power_path)//2]
    d_mid = clean_data_path[len(clean_data_path)//2]
    f.write(f"TEXT:E-POWR:{p_mid[0]*grid_resolution},{p_mid[1]*grid_resolution + 150}:CCT P1 (2.5mm²)\n")
    f.write(f"TEXT:E-DATA:{d_mid[0]*grid_resolution},{d_mid[1]*grid_resolution + 150}:CCT LV1 (Cat6)\n")

    # Schedule Data for Breaker Table
    f.write(f"SCHEDULE:P1,Power Ring 13A,20A MCB,3x2.5mm²,{power_length}m\n")
    f.write(f"SCHEDULE:LV1,IT Data Point,Cat6 RJ45,UTP Cable,{data_length}m\n")

print(f"✅ Generated Complete MEP Contract! Power: {power_length}m | Data: {data_length}m")