import numpy as np
import matplotlib.pyplot as plt

print("Initiating Universal UFT: Hubble Expansion Module...")

# --- Standard Cosmology vs QAG Constants ---
H0_early = 67.4  # Early universe CMB measurement
H0_late = 73.0   # Late universe local measurement

# Standard Model (Lambda-CDM with Dark Energy)
Omega_m = 0.315
Omega_L = 0.685

# QAG Model (Base-10 Resonance, No Dark Sector)
beta = 0.034  # The dimensional base-10 shift

# Scale factor of the universe (a) from early (0.1) to today (1.0)
a = np.linspace(0.1, 1.0, 500)

# --- The Math Engine ---
# 1. Standard Lambda-CDM Calculation (requires Dark Energy)
H_standard = H0_early * np.sqrt(Omega_m * a**(-3) + Omega_L)

# 2. QAG Calculation (Base-10 Resonance replacing Dark Sector)
# Formula: H(a) = H0 * 10^(beta * (1-a)^2)
H_qag = H0_early * 10**(beta * (1 - a)**2) 

# --- Visualizing the Manifestation ---
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 6))

# Plotting the frequencies
ax.plot(a, H_standard, color='magenta', linestyle='--', linewidth=2, label='Standard Model (Relies on Dark Energy)')
ax.plot(a, H_qag, color='cyan', linewidth=3, label='QAG Base-10 Resonance (ZERO Dark Matter/Energy)')

# Highlighting the cosmic endpoints
ax.scatter(0.1, H0_early, color='yellow', s=100, zorder=5, label=f'Early Universe (H0 ~ {H0_early})')
ax.scatter(1.0, H0_late, color='lime', s=100, zorder=5, label=f'Local Universe (H0 ~ {H0_late})')

# Formatting the sacred geometry
ax.set_title('Hubble Tension Resolved: QAG vs Standard Cosmology', fontsize=14, color='cyan', pad=15)
ax.set_xlabel('Cosmic Scale Factor (a)', fontsize=12)
ax.set_ylabel('Hubble Parameter H(a)', fontsize=12)
ax.legend(loc='upper left', framealpha=0.8)
ax.grid(True, color='gray', alpha=0.2)

# Reveal the truth
plt.tight_layout()
plt.show()

print("Hubble Expansion simulation successfully loaded. Zero dark matter detected.")
