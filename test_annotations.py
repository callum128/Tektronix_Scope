import numpy as np
import matplotlib.pyplot as plt
from rex_utils import load_rex_data
from scipy.signal import find_peaks
from adjustText import adjust_text
from pathlib import Path
from scipy.interpolate import PchipInterpolator 


s1_3P0 = 'Outputs/Excitation/S1/EX_S1_3P0_from_1D2-1G4_excitation_C481_27_08_2026_15_04_57_328.toml'
def ex_loader(filename, initial_wavelength, final_wavelength):
        data_path = Path(__file__).parent / filename
        data = load_rex_data(data_path, "polars")

        areas = np.array(data['DPO7104_TekTronix_scope_area'])
        #print(f'First 10 areas from the scope: {areas[:5]}')


        #wavelengths = np.arange(initial_wavelength, final_wavelength + n*step_size, step_size)
        wavelengths = np.linspace(initial_wavelength, final_wavelength, len(areas))
        #print(f'Laser wavelength range: {wavelengths[0]} - {wavelengths[-1]}')

        wavenumbers = 1e7 / wavelengths

        return wavelengths, areas


x, y = ex_loader(s1_3P0, 465, 495)

# 2. Automatically find the peaks
peaks, _ = find_peaks(y, distance=10, prominence=0.0002)

# 3. Initialize the plot
fig, ax = plt.subplots(figsize=(10, 6))
spectrum_line, = ax.plot(x, y, label="Spectrum", color='navy', lw=1.5, marker='.')
#ax.plot(x[peaks], y[peaks], "o", color='crimson', markersize=5)

# 4. Create text objects for adjustText to manipulate
texts = []
for i, peak_idx in enumerate(peaks):
    p_x = x[peak_idx]
    p_y = y[peak_idx]
    
    # Place initial labels directly on the peaks (adjustText will move them)
    t = ax.text(p_x, p_y, f"{p_x:.1f}", ha='center', va='center', fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.8)
                )
    texts.append(t)


# 5. Automatically resolve overlaps and draw lines
# adjustText handles the collisions and links text to (x[peaks], y[peaks])
adjust_text(
    texts, 
    x=x,
    y=y,
    # x=x[peaks],
    # y=y[peaks],
    #objects=[spectrum_line],
    only_move={
        "text": "y+",
        "static": "y+",
        "explode": "y+",
        "pull": "y+",
    },
    arrowprops=dict(
        arrowstyle="-",     # Direct line without massive arrowheads
        color='k',    # Muted color for clean look across crowded spectra
        lw=0.5,
        alpha=0.9,          # Slightly transparent for subtlety
        shrinkA=15,           # Ensures line connects cleanly to the peak point
        shrinkB=3 
    ),
    #expand=(1.0, 1.0),      # Forces labels to spread out vertically/horizontally
    #force_text=(1.0, 1.0)   # Tweak how strongly text repels text
)

ax.set_title("Automated Spectral Peak Annotation")
ax.set_xlabel("Wavelength / Wavenumber")
ax.set_ylabel("Intensity")
ax.set_ylim(bottom=0, top=max(y) * 1.3) # Leave header room for shifted labels

plt.show()




'''
import numpy as np
import matplotlib.pyplot as plt
from rex_utils import load_rex_data
from scipy.signal import find_peaks
from adjustText import adjust_text
from pathlib import Path


# ================================================================
# Load spectrum
# ================================================================

s1_3P0 = (
    'Outputs/Excitation/S1/'
    'EX_S1_3P0_from_1D2-1G4_excitation_C481_27_08_2026_15_04_57_328.toml'
)


def ex_loader(filename, initial_wavelength, final_wavelength):
    data_path = Path(__file__).parent / filename
    data = load_rex_data(data_path, "polars")

    areas = np.array(data['DPO7104_TekTronix_scope_area'])

    wavelengths = np.linspace(
        initial_wavelength,
        final_wavelength,
        len(areas)
    )

    return wavelengths, areas


x, y = ex_loader(s1_3P0, 465, 495)


# ================================================================
# Find peaks
# ================================================================

peaks, properties = find_peaks(
    y,
    distance=10,
    prominence=0.0002
)


# ================================================================
# Plot spectrum
# ================================================================

fig, ax = plt.subplots(figsize=(10, 6))

spectrum_line, = ax.plot(
    x,
    y,
    label="Spectrum",
    color="navy",
    lw=1.5
)


# ================================================================
# Label parameters
# ================================================================

y_range = np.max(y) - np.min(y)

# Minimum vertical distance between a peak and its label.
#
# Increase this if labels are too close to the spectrum.
label_offset = 0.025 * y_range

# Extra space above the spectrum for labels.
top_margin = 0.30 * y_range


# ================================================================
# Create labels
# ================================================================

texts = []

# Store the actual peak location associated with each label
peak_positions = {}

# Store where each label started
initial_positions = {}

for peak_idx in peaks:

    peak_x = x[peak_idx]
    peak_y = y[peak_idx]

    # Start above the peak
    label_x = peak_x
    label_y = peak_y + label_offset

    text = ax.text(
        label_x,
        label_y,
        f"{peak_x:.1f}",
        ha="center",
        va="bottom",
        fontsize=9,
        zorder=5,
    )

    texts.append(text)

    peak_positions[text] = (peak_x, peak_y)
    initial_positions[text] = (label_x, label_y)


# ================================================================
# Set limits BEFORE adjustText
# ================================================================

ax.set_ylim(
    bottom=0,
    top=np.max(y) + top_margin
)


# ================================================================
# Adjust labels
# ================================================================

adjust_text(
    texts,

    # Peak coordinates
    x=x[peaks],
    y=y[peaks],

    # Avoid the spectrum
    objects=[spectrum_line],

    # Allow BOTH horizontal and vertical movement
    direction="xy",

    # Allow movement in both directions
    only_move={
        "text": "xy",
        "static": "xy",
        "explode": "xy",
        "pull": "xy",
    },

    # Repulsion between labels
    force_text=(1.5, 5.0),

    # Repulsion from the spectrum
    force_static=(1.0, 2.0),

    # Initial "explosion" of overlapping labels
    force_explode=(1.0, 1.0),

    # Pull labels back towards their associated peaks
    # when there is no collision.
    force_pull=(0.1, 0.2),

    # Increase this if labels are still too close together.
    expand=(1.5, 2.0),

    # Don't let adjustText draw the connectors.
    arrowprops=None,

    # Keep labels inside the axes.
    ensure_inside_axes=True,
)


# ================================================================
# Make sure labels NEVER end up below their peak
# ================================================================

for text in texts:

    peak_x, peak_y = peak_positions[text]

    text_x, text_y = text.get_position()

    # If adjustText has pushed the label below its peak,
    # force it back above the peak.
    minimum_y = peak_y + label_offset

    if text_y < minimum_y:
        text_y = minimum_y

    text.set_position((text_x, text_y))


# ================================================================
# Draw connector lines ONLY for labels that moved
# ================================================================

for text in texts:

    peak_x, peak_y = peak_positions[text]

    initial_x, initial_y = initial_positions[text]

    text_x, text_y = text.get_position()

    # How far did the label move from its original position?
    dx = abs(text_x - initial_x)
    dy = abs(text_y - initial_y)

    # Only draw a connector if the label actually moved.
    if dx > 1e-4 or dy > 1e-4:

        ax.plot(
            [peak_x, text_x],
            [peak_y, text_y],
            color="black",
            lw=0.5,
            alpha=0.8,
            zorder=2
        )


# ================================================================
# Formatting
# ================================================================

ax.set_title("Automated Spectral Peak Annotation")

ax.set_xlabel("Wavelength")
ax.set_ylabel("Intensity")

ax.legend()

plt.tight_layout()
plt.show()

'''