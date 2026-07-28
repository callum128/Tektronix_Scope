import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

DFT = np.array([
    [0.0, 0.0, 0.0],  # Central atom of site 2 (7CN)
    [-1.0131, -2.2602, 0.3636],  
    [1.9789, -1.7604, 0.2523],  
    [-0.5786, 1.5160, -1.8075],
    [1.6785, -0.1097, -1.7481],
    [-2.0943, 1.0693, 0.7176],
    [0.6929, 1.9511, 1.1332],
    [0.2889, -0.5455, 2.4595]   
])

AbInitio = np.array([
    [0.0000000,    0.0000000,     0.0000000],
    [1.8252572,      -0.9476610,       0.6337145],
    [0.8573055,      -0.5780060,      -2.0108249],
    [-0.1676709,       1.7138550,      1.5355390],
    [1.4434827,       1.7407391,    -0.6337145],
    [-2.1623351,      -0.2016300,     -0.9871322],
    [-0.5494454,      -2.3187451,       0.2681100],
    [-1.7668530,      -0.2016300,       1.8889568]
])

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

def plot_multi_view_system(euler_angles, atoms_initial, seq='zyx', degrees=True):
    # 1. Calculate Rotations
    rotation = R.from_euler(seq, euler_angles, degrees=degrees)
    rotation_matrix = rotation.as_matrix()

    atoms_rotated = atoms_initial @ rotation_matrix.T
    central_atom = atoms_rotated[0]

    # Define coordinate axes
    axis_length = 2.0
    axes_initial = np.eye(3) * axis_length
    axes_rotated = axes_initial @ rotation_matrix.T

    # 2. Setup 2x2 Grid Figure
    fig = plt.figure(figsize=(14, 11))
    
    # Define our 4 view configurations: (Subplot Index, Elevation, Azimuth, View Title)
    views = [
        (1, 30, -60, "Standard 3D Perspective (Interactive)"),
        (2, 90, -90, "Top-Down View (XY Plane Projection)"),
        (3, 0, -90,  "Front View (XZ Plane Projection)"),
        (4, 0, 0,    "Side View (YZ Plane Projection)")
    ]

    colors = ['r', 'g', 'b']
    labels = ['X-axis', 'Y-axis', 'Z-axis']

    for subplot_idx, elev, azim, title in views:
        ax = fig.add_subplot(2, 2, subplot_idx, projection='3d')
        
        # --- Set the Camera Viewing Angle ---
        ax.view_init(elev=elev, azim=azim)

        # Plot Bonds
        for i in range(1, len(atoms_rotated)):
            ax.plot(
                [central_atom[0], atoms_rotated[i, 0]],
                [central_atom[1], atoms_rotated[i, 1]],
                [central_atom[2], atoms_rotated[i, 2]],
                color='dimgray', linestyle='--', linewidth=2, zorder=3
            )

        # Plot Atoms
        ax.scatter(central_atom[0], central_atom[1], central_atom[2], 
                   color='royalblue', s=350, edgecolor='black', zorder=5)
        ax.scatter(atoms_rotated[1:, 0], atoms_rotated[1:, 1], atoms_rotated[1:, 2], 
                   color='crimson', s=180, edgecolor='black', zorder=5)

        # Plot Reference Axes
        for i in range(3):
            ax.plot([0, axes_rotated[i, 0]], [0, axes_rotated[i, 1]], [0, axes_rotated[i, 2]], 
                    color=colors[i], lw=2.5)
            ax.text(axes_rotated[i, 0] * 1.15, axes_rotated[i, 1] * 1.15, axes_rotated[i, 2] * 1.15, 
                    labels[i], color=colors[i], fontsize=10, weight='bold')

        # Formatting each subplot
        ax.set_xlim([-2.5, 2.5])
        ax.set_ylim([-2.5, 2.5])
        ax.set_zlim([-2.5, 2.5])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(title, fontsize=12, pad=10)
        ax.grid(True)

    # Global window configuration
    angle_str = ", ".join(map(str, euler_angles))
    fig.suptitle(f"Multi-View Molecular Projection\nSequence: {seq.upper()} | Angles: [{angle_str}]°", 
                 fontsize=16, weight='bold', y=0.98)
    
    plt.tight_layout()
    plt.show(block=True)

# Run layout setup
plot_multi_view_system(euler_angles=[0, 0, 0], atoms_initial=CN7, seq='zyx')

