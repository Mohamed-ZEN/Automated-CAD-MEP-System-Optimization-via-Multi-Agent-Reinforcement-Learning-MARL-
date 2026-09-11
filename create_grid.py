import numpy as np
import matplotlib.pyplot as plt

# 1. Set grid size (9.7m x 11.5m room split into 10cm cells)
width_cells = 97   # 9.7 meters
height_cells = 115 # 11.5 meters

# 2. Create an empty grid (0 = open floor space)
grid = np.zeros((height_cells, width_cells))

# 3. Add outer walls (1 = wall boundary)
grid[0, :] = 1   # Bottom wall
grid[-1, :] = 1  # Top wall
grid[:, 0] = 1   # Left wall
grid[:, -1] = 1  # Right wall

# 4. Save a visual preview image
plt.imshow(grid, cmap='binary')
plt.title("Step 1: Base Floorplan Grid")
plt.savefig("room_grid.png")

print("Grid created successfully! Saved as room_grid.png")