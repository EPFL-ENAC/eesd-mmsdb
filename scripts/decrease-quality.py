import os
from pathlib import Path
import open3d as o3d
import numpy as np
from tqdm import tqdm

# Configurable parameters
TARGET_SIZE_MB = 1
TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024
SMOOTHING_ITERATIONS = 3  # Number of smoothing iterations
VERTEX_CLUSTERING_SIZE = 0.01  # Size for vertex clustering (smaller = less reduction)
NOISE_STRENGTH = 0.001  # Small noise to reduce precision

def get_all_ply_files(root_dir):
    return list(Path(root_dir).rglob("*.ply"))

def reduce_mesh_quality(file_path):
    try:
        mesh = o3d.io.read_triangle_mesh(str(file_path))

        if not mesh.has_triangles():
            print(f"Skipped (no triangles): {file_path}")
            return

        mesh.compute_vertex_normals()
        original_size = os.path.getsize(file_path)

        # Method 1: Vertex clustering (merges nearby vertices without creating holes)
        mesh = mesh.simplify_vertex_clustering(voxel_size=VERTEX_CLUSTERING_SIZE)
        mesh.compute_vertex_normals()

        # Method 2: Laplacian smoothing (reduces surface detail while preserving shape)
        mesh = mesh.filter_smooth_laplacian(number_of_iterations=SMOOTHING_ITERATIONS)
        mesh.compute_vertex_normals()

        # Method 3: Add small noise to reduce coordinate precision
        vertices = np.asarray(mesh.vertices)
        noise = np.random.normal(0, NOISE_STRENGTH, vertices.shape)
        mesh.vertices = o3d.utility.Vector3dVector(vertices + noise)

        # Method 4: Reduce coordinate precision by rounding
        vertices = np.asarray(mesh.vertices)
        vertices = np.round(vertices, 3)  # Round to 3 decimal places
        mesh.vertices = o3d.utility.Vector3dVector(vertices)

        # Remove duplicate vertices and triangles
        mesh.remove_duplicated_vertices()
        mesh.remove_duplicated_triangles()
        mesh.remove_unreferenced_vertices()

        # Save as binary PLY (reduces size significantly if it's ASCII)
        o3d.io.write_triangle_mesh(str(file_path), mesh, write_ascii=False)

        final_size = os.path.getsize(file_path)
        
        if original_size > 0:
            size_reduction = ((original_size - final_size) / original_size) * 100
        else:
            size_reduction = 0
        
        if final_size > original_size:
            print(f"⚠️ Size increased: {file_path} ({final_size / 1e6:.2f} MB, increased by {abs(size_reduction):.1f}%)")
        elif final_size > TARGET_SIZE_BYTES:
            print(f"⚠️ Still >1MB: {file_path} ({final_size / 1e6:.2f} MB, reduced by {size_reduction:.1f}%)")
        else:
            print(f"✅ Reduced: {file_path} ({final_size / 1e6:.2f} MB, reduced by {size_reduction:.1f}%)")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

def main(root_folder):
    ply_files = get_all_ply_files(root_folder)
    print(f"Found {len(ply_files)} .ply files.")

    for file in tqdm(ply_files, desc="Processing"):
        reduce_mesh_quality(file)

# Run it
main("/home/user/documents/mms/15044436")
