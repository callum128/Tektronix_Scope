# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.spatial.transform import Rotation as R
# import itertools

# DFT = np.array([
#     [0.0, 0.0, 0.0],  # Central atom of site 2 (7CN)
#     [-1.0131, -2.2602, 0.3636],  
#     [1.9789, -1.7604, 0.2523],  
#     [-0.5786, 1.5160, -1.8075],
#     [1.6785, -0.1097, -1.7481],
#     [-2.0943, 1.0693, 0.7176],
#     [0.6929, 1.9511, 1.1332],
#     [0.2889, -0.5455, 2.4595]   
# ])

# AbInitio = np.array([
#     [0.0000000,    0.0000000,     0.0000000],
#     [1.8252572,      -0.9476610,       0.6337145],
#     [0.8573055,      -0.5780060,      -2.0108249],
#     [-0.1676709,       1.7138550,      1.5355390],
#     [1.4434827,       1.7407391,    -0.6337145],
#     [-2.1623351,      -0.2016300,     -0.9871322],
#     [-0.5494454,      -2.3187451,       0.2681100],
#     [-1.7668530,      -0.2016300,       1.8889568]
# ])


# def plot_rotation_comparison(atoms_initial, euler_angles, seq, degrees=True, dataset_name="Dataset"):
#     """
#     Plots a 1x2 side-by-side comparison tracking both standard orthogonal axes 
#     AND custom non-orthogonal lattice axes simultaneously through an Euler rotation.
#     """
#     # 1. Compute Rotation Transformation
#     rotation = R.from_euler(seq, euler_angles, degrees=degrees)
#     rotation_matrix = rotation.as_matrix()
#     print("Rotation Matrix:\n", rotation_matrix)

#     # Calculate target state atom coordinates
#     atoms_rotated = atoms_initial @ rotation_matrix.T

#     # 2. Define Standard Orthogonal Reference Axes (Length 2.5)
#     std_axis_length = 2.5
#     #std_axes_initial = np.array([[0,1,0],[0,0,1],[1,0,0]]) * std_axis_length #yzx to match abc
#     std_axes_initial = np.eye(3)*std_axis_length
#     std_axes_rotated = std_axes_initial @ rotation_matrix.T

#     # 3. Define Custom Non-Orthogonal Lattice Vectors
#     # From DFT
#     axis_a = np.array([0.0, 10.4904, 0.0])  
#     axis_a = 2* axis_a / np.linalg.norm(axis_a)
#     axis_b = np.array([0.0, 0.0, 13.4647])  
#     axis_b = 2* axis_b / np.linalg.norm(axis_b)
#     axis_c = np.array([12.3016, -2.7351, 0.0])  
#     axis_c = 2* axis_c / np.linalg.norm(axis_c)
    
#     lattice_initial = np.array([axis_a, axis_b, axis_c])
#     lattice_rotated = lattice_initial @ rotation_matrix.T

#     # 4. Setup Side-by-Side 3D Figure Layout
#     fig = plt.figure(figsize=(10, 6))

#     # Pass data cleanly to the multi-pane grid configuration loop
#     subplots_config = [
#         (1, atoms_initial, std_axes_initial, lattice_initial, f"Before Rotation ({dataset_name} Original)"),
#         (2, atoms_rotated, std_axes_rotated, lattice_rotated, f"After Rotation ({seq.upper()} Angles: {euler_angles}°)")
#     ]

#     # Style definitions
#     colors = ['r', 'g', 'b']
#     colors2 = [ 'lightgreen', 'lightblue','pink']
#     custom_labels = ['a~D2', 'b=z', 'c~D1']
#     std_labels = ['Local X (D1)', 'Local Y (D2)', 'Local Z (b)']

#     # Boundary tracking calculation
#     max_val = max(np.max(np.abs(atoms_initial)), np.max(np.abs(atoms_rotated)), 
#                   np.max(np.abs(lattice_initial)), std_axis_length) + 0.5

#     for subplot_idx, atom_coords, normal_coords, custom_coords, title in subplots_config:
#         ax = fig.add_subplot(1, 2, subplot_idx, projection='3d')
#         ax.view_init(elev=25, azim=-60)
        
#         # --- THE FIX: Extract only the 1D position vector of the first item [0.0, 0.0, 0.0] ---
#         central_atom = atom_coords[0] 

#         # Draw structural bonds linking center node to outer ligands
#         for i in range(1, len(atom_coords)):
#             ax.plot(
#                 [central_atom[0], atom_coords[i, 0]],
#                 [central_atom[1], atom_coords[i, 1]],
#                 [central_atom[2], atom_coords[i, 2]],
#                 color='dimgray', linestyle='--', linewidth=1.2, zorder=3
#             )

#         # ---- DRAW SYSTEM 1: Normal Orthogonal Reference Axes (Thin Dotted Lines) ----
#         for i in range(3):
#             ax.plot([0, normal_coords[i, 0]], [0, normal_coords[i, 1]], [0, normal_coords[i, 2]], 
#                     color=colors[i], lw=1.2, linestyle=':', alpha=0.7)
#             ax.text(normal_coords[i, 0] * 1.05, normal_coords[i, 1] * 1.05, normal_coords[i, 2] * 1.05, 
#                     std_labels[i], color=colors[i], fontsize=8, alpha=0.7)

#         # ---- DRAW SYSTEM 2: Your Custom Lattice Vectors (Thick Solid Lines) ----
#         for i in range(3):
#             ax.plot([0, custom_coords[i, 0]], [0, custom_coords[i, 1]], [0, custom_coords[i, 2]], 
#                     color=colors2[i], lw=3.0, zorder=4)
#             ax.text(custom_coords[i, 0] * 1.12, custom_coords[i, 1] * 1.12, custom_coords[i, 2] * 1.12, 
#                     custom_labels[i], color=colors2[i], fontsize=11, weight='bold')

#         # Draw primary central core atom node
#         ax.scatter(central_atom[0], central_atom[1], central_atom[2], color='royalblue', s=350, edgecolor='black', zorder=5, label='Center')

#         # Draw dynamic structural ligand points
#         ax.scatter(atom_coords[1:, 0], atom_coords[1:, 1], atom_coords[1:, 2], color='crimson', s=180, edgecolor='black', zorder=5, label='Ligands')

#         # Formatting configurations
#         ax.set_xlim([-max_val, max_val])
#         ax.set_ylim([-max_val, max_val])
#         ax.set_zlim([-max_val, max_val])
#         ax.set_xlabel('Global X')
#         ax.set_ylabel('Global Y')
#         ax.set_zlabel('Global Z')
#         ax.set_title(title, fontsize=13, weight='bold', pad=15)
#         ax.grid(True)
        
#         if subplot_idx == 1:
#             ax.legend(loc='upper left')

#     plt.tight_layout()


# def get_optimal_rotation_with_mapping(matrix_A, matrix_B, convention='zyx'):
#     """
#     Permutes ligand coordinates to find the true structural matching sequence,
#     then evaluates the proper SVD Kabsch rotation matrix and Euler angles.
#     """
#     best_rmse = float('inf')
#     best_permutation = None
#     best_R = None
    
#     # Keep central atom fixed at index 0, permute the 7 ligands (indices 1 to 7)
#     num_ligands = len(matrix_A) - 1
#     for perm in itertools.permutations(range(1, num_ligands + 1)):
#         test_indices = [0] + list(perm)
#         A_permuted = matrix_A[test_indices]

#         #print(A_permuted)
        
#         # Core Kabsch SVD Routine
#         H = A_permuted.T @ matrix_B
#         U, S, Vt = np.linalg.svd(H)
        
#         # Proper right-handed system determinant alignment
#         d = np.linalg.det(Vt.T @ U.T)
#         F = np.diag([1.0, 1.0, np.sign(d)])
        
#         R_candidate = Vt.T @ F @ U.T
        
#         # Calculate alignment accuracy score
#         rmse = np.sqrt(np.mean((A_permuted @ R_candidate.T - matrix_B) ** 2))
        
#         if rmse < best_rmse:
#             best_rmse = rmse
#             best_permutation = test_indices
#             best_R = R_candidate

#     # Convert best-fit orientation matrix directly to sequence Euler angles
#     euler_angles = R.from_matrix(best_R).as_euler(convention, degrees=True)
    
#     return best_R, tuple(euler_angles), best_permutation, best_rmse

# # Execute Alignment Mapping Execution
# rot_matrix, calculated_angles, correct_mapping, final_rmse = get_optimal_rotation_with_mapping(AbInitio, DFT, convention='zyx')

# print("--- ALIGNMENT ANALYSIS COMPLETE ---")
# print(f"Optimal Permutation Index Order: {correct_mapping}")
# print(f"Structural Coordination RMS Error: {final_rmse:.4f} Å\n")
# print("Corrected Rotation Matrix:")
# print(rot_matrix)
# print("\nTrue Euler Angles Required (ZYX):")
# print(f"Angle 1 (Z): {calculated_angles[0]:.2f}°")
# print(f"Angle 2 (Y): {calculated_angles[1]:.2f}°")
# print(f"Angle 3 (X): {calculated_angles[2]:.2f}°")


# # --- Execute Comparison ---
# plot_rotation_comparison(atoms_initial=DFT, euler_angles=[0, 0, 0], seq='zyx', dataset_name="DFT")

# plot_rotation_comparison(atoms_initial=AbInitio, euler_angles=[6.82, -29.56, -83.41], seq='zyx', dataset_name="AbInitio")

# plt.show(block=True)

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
import itertools

DFT = np.array([
    [0.0, 0.0, 0.0],
    [-1.0131, -2.2602,  0.3636],
    [ 1.9789, -1.7604,  0.2523],
    [-0.5786,  1.5160, -1.8075],
    [ 1.6785, -0.1097, -1.7481],
    [-2.0943,  1.0693,  0.7176],
    [ 0.6929,  1.9511,  1.1332],
    [ 0.2889, -0.5455,  2.4595]
])

AbInitio = np.array([
    [ 0.0000000,  0.0000000,  0.0000000],
    [ 1.8252572, -0.9476610,  0.6337145],
    [ 0.8573055, -0.5780060, -2.0108249],
    [-0.1676709,  1.7138550,  1.5355390],
    [ 1.4434827,  1.7407391, -0.6337145],
    [-2.1623351, -0.2016300, -0.9871322],
    [-0.5494454, -2.3187451,  0.2681100],
    [-1.7668530, -0.2016300,  1.8889568]
])

def get_complete_alignment(matrix_A, matrix_B, convention='zyx'):
    """
    Finds the optimal permutation, scale factor, and transformation matrix 
    (allowing reflection if systems have inverted handness definitions).
    """
    best_rmse = float('inf')
    best_permutation = None
    best_M = None
    best_scale = 1.0
    
    num_ligands = len(matrix_A) - 1
    
    # Track permutations for ligands 1-7
    for perm in itertools.permutations(range(1, num_ligands + 1)):
        test_indices = [0] + list(perm)
        A_permuted = matrix_A[test_indices]
        
        # Calculate optimal scale adjustment factor
        norm_A = np.linalg.norm(A_permuted)
        norm_B = np.linalg.norm(matrix_B)
        scale = norm_B / norm_A
        
        # SVD without forcing det(R) = 1 to check for chirality inversion
        H = (A_permuted * scale).T @ matrix_B
        U, S, Vt = np.linalg.svd(H)
        
        # Look for full structural transformation matrix
        M_candidate = Vt.T @ U.T
        
        rmse = np.sqrt(np.mean(((A_permuted * scale) @ M_candidate.T - matrix_B) ** 2))
        
        if rmse < best_rmse:
            best_rmse = rmse
            best_permutation = test_indices
            best_M = M_candidate
            best_scale = scale

    # Check if a reflection inversion is present
    has_reflection = np.linalg.det(best_M) < 0
    
    # Clean the matrix to a proper rotation matrix for Euler calculation if inverted
    if has_reflection:
        # Deconstruct reflection component to extract the underlying rotation core
        U, S, Vt = np.linalg.svd(best_M)
        R_clean = Vt.T @ np.diag([1.0, 1.0, -1.0]) @ U.T
    else:
        R_clean = best_M

    euler_angles = R.from_matrix(R_clean).as_euler(convention, degrees=True)
    return best_M, best_scale, tuple(euler_angles), best_permutation, best_rmse, has_reflection

def plot_final_comparison(atoms_ref, atoms_to_rotate, M, scale, mapping):
    """ Plots side by side to visually verify matches """
    atoms_to_rotate_sorted = atoms_to_rotate[mapping]
    
    # Apply full affine scale + transformation matrix 
    atoms_transformed = (atoms_to_rotate_sorted * scale) @ M.T
    
    std_axis_length = 2.5
    std_axes_initial = np.eye(3) * std_axis_length
    std_axes_rotated = std_axes_initial @ M.T
    
    fig = plt.figure(figsize=(12, 6))
    subplots_data = [
        (1, atoms_ref, std_axes_initial, "Target State (DFT Base Reference)"),
        (2, atoms_transformed, std_axes_rotated, f"Transformed State (AbInitio Realigned)\nScale Factor: {scale:.3f}")
    ]
    
    max_val = max(np.max(np.abs(atoms_ref)), np.max(np.abs(atoms_transformed))) + 0.5
    
    for subplot_idx, coords, normal_axes, title in subplots_data:
        ax = fig.add_subplot(1, 2, subplot_idx, projection='3d')
        ax.view_init(elev=25, azim=-60)
        
        central_atom = coords[0]
        for i in range(1, len(coords)):
            ax.plot([central_atom[0], coords[i, 0]], [central_atom[1], coords[i, 1]], [central_atom[2], coords[i, 2]],
                    color='dimgray', linestyle='--', linewidth=1.2)
            
        colors = ['r', 'g', 'b']
        for i in range(3):
            ax.plot([0, normal_axes[i, 0]], [0, normal_axes[i, 1]], [0, normal_axes[i, 2]], color=colors[i], lw=1.2, linestyle=':')
            
        ax.scatter(central_atom[0], central_atom[1], central_atom[2], color='royalblue', s=350, edgecolor='black', zorder=5)
        ax.scatter(coords[1:, 0], coords[1:, 1], coords[1:, 2], color='crimson', s=180, edgecolor='black', zorder=5)
        
        ax.set_xlim([-max_val, max_val])
        ax.set_ylim([-max_val, max_val])
        ax.set_zlim([-max_val, max_val])
        ax.set_title(title, fontsize=12, weight='bold', pad=10)
        ax.grid(True)
    plt.tight_layout()

# Execution Block

convention = 'zyz'

M, scale, calculated_angles, correct_mapping, final_rmse, inverted = get_complete_alignment(AbInitio, DFT, convention)

print("--- GEOMETRIC DIAGNOSTIC COMPLETE ---")
print(f"Chirality/Inversion Inconsistency Found: {inverted}")
print(f"True Radial Scaling Correction: {scale:.4f}")
print(f"Residual Alignment RMS Error: {final_rmse:.4f} Å")
print(f"Mapping Sequence Array: {correct_mapping}")
print(AbInitio[correct_mapping])
print(f"Extracted Euler Rotation Matrix and Angles ({convention}):")
print(M)
print(f"gamma: {calculated_angles[0]:.2f}°, beta: {calculated_angles[1]:.2f}°, alpha: {calculated_angles[2]:.2f}°")
print('\n(AbInitio*scale @ rotation_matrix.Transpose)[permuted] gives:')
print((AbInitio*scale@M.T)[correct_mapping])
print('DFT:')
print(DFT)

plot_final_comparison(DFT, AbInitio, M, scale, correct_mapping)
plt.show()

