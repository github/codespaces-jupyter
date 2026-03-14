import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

print("Initiating Universal UFT: Massive Mode Resonance Matrix...")

# --- Setup the Dimensions ---
# r represents the distance from the center of the galactic mass
r = np.linspace(0.1, 5.0, 500)

def calculate_warp(alpha, m_massive):
    """Calculates both the standard well and the stretched QAG well."""
    # Standard Newtonian Gravity Well (Baseline)
    newton = -1.0 / r
    
    # QAG Massive Mode Resonance (The Stretch and Warp)
    # The exponential function creates the extended 'Ghost Halo'
    qag_warp = (-1.0 / r) * (1 + alpha * np.exp(-m_massive * r))
    return newton, qag_warp

# Initial Resonance States
init_alpha = 3.0  # The strength of the affinity field
init_m = 1.0      # The mass mode (how far the stretch reaches)
newton_baseline, qag_initial = calculate_warp(init_alpha, init_m)

# --- Paint the Canvas ---
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(bottom=0.35) # Make room for the dimension controls

# Plot the standard baseline vs the stretched QAG peak
line_newton, = ax.plot(r, newton_baseline, color='magenta', linestyle='--', linewidth=2, label='Standard Gravity Well (No Dark Matter)')
line_qag, = ax.plot(r, qag_initial, color='cyan', linewidth=3, label='QAG Massive Mode Resonance')

# Formatting the sacred geometry
ax.set_title('Gravitational Peaks Stretch & Warp', color='cyan', fontsize=14, pad=15)
ax.set_xlabel('Distance from Mass Center (r)', fontsize=12)
ax.set_ylabel('Gravitational Potential Depth', fontsize=12)
ax.legend(loc='lower right', framealpha=0.8)
ax.grid(True, color='gray', alpha=0.2)
ax.set_ylim(-15, 0)

# --- Interactive Matrix Controls ---
# Sliders to manually stretch and warp the gravitational peaks
ax_alpha = plt.axes([0.15, 0.15, 0.7, 0.03])
ax_m = plt.axes([0.15, 0.08, 0.7, 0.03])

slider_alpha = Slider(ax_alpha, 'Affinity Load (alpha)', 0.0, 10.0, valinit=init_alpha, color='cyan')
slider_m = Slider(ax_m, 'Mode Mass (m)', 0.1, 5.0, valinit=init_m, color='lime')

def update(val):
    """Dynamically updates the well when you shift the dimensions."""
    _, new_qag = calculate_warp(slider_alpha.val, slider_m.val)
    line_qag.set_ydata(new_qag)
    fig.canvas.draw_idle()

# Listen for the universe shifting
slider_alpha.on_changed(update)
slider_m.on_changed(update)

# Reveal the truth
plt.show()

print("Massive Mode Matrix loaded. Ready to stretch dimensions.")
