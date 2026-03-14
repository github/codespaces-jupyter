import numpy as np
import matplotlib.pyplot as plt

print("Initiating Universal UFT Local Shield Visualizer...")

# --- 1. Set Up the Cosmic Canvas ---
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 8))

# Map the Local Space (A grid of 100,000 km around Earth)
grid_size = 100000 
x = np.linspace(-grid_size, grid_size, 300)
y = np.linspace(-grid_size, grid_size, 300)
X, Y = np.meshgrid(x, y)

# --- 2. Calculate the Universal UFT Math ---
# Calculate the distance from Earth (r) for every pixel
R = np.sqrt(X**2 + Y**2)
R[R == 0] = 0.1 # Prevent dividing by zero at the exact center

# The Local Shield Math: Scaling the distance down for the tensor math
r_scaled = R / 1e8

# The Shielding Effect: 
# Approaches 0 near Earth (Pure Newton), approaches 1 far away (Full QAG Variance)
shielding_effect = 1.0 - np.exp(-r_scaled * 1000.0)

# --- 3. Paint the QAG Affinity Field ---
# We use a contour map to show the massive modes relaxing
contour = ax.contourf(X, Y, shielding_effect, levels=50, cmap='magma', alpha=0.7)
cbar = plt.colorbar(contour)
cbar.set_label('QAG Variance Shielding (0 = Pure Newton)', color='cyan', fontsize=11)

# --- 4. Draw Earth and the Asteroid ---
# Draw the Earth right in the center
earth = plt.Circle((0, 0), 6371, color='dodgerblue', label='Earth (Screening Center)')
ax.add_patch(earth)

# Plot a simulated parabolic flyby for our verified asteroid
t = np.linspace(-grid_size, grid_size, 100)
asteroid_x = t
asteroid_y = 0.0001 * t**2 + 25000  # A close approach 25,000 km away
ax.plot(asteroid_x, asteroid_y, color='lime', linestyle='--', linewidth=2, label='Asteroid Trajectory')

# Mark the exact moment of closest approach
ax.plot(0, 25000, marker='*', color='yellow', markersize=15, label='Closest Approach')

# --- 5. Formatting the Output ---
ax.set_title('Universal UFT: Local Shield Active Around Earth', fontsize=14, color='cyan', pad=15)
ax.set_xlabel('Distance X (km)', fontsize=12)
ax.set_ylabel('Distance Y (km)', fontsize=12)
ax.legend(loc='upper right', framealpha=0.8)
ax.grid(True, color='gray', alpha=0.2)

# Ensure Earth is perfectly round
ax.set_aspect('equal', adjustable='box')

# Reveal the truth
plt.tight_layout()
plt.show()

print("Visualizer successfully manifested on screen.")
