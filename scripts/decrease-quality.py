import os
import sys
from pathlib import Path
import open3d as o3d
import numpy as np
from tqdm import tqdm

# Configurable parameters
TARGET_SIZE_MB = 1
TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024
TARGET_NUMBER_OF_TRIANGLES_STONE = 5000
TARGET_NUMBER_OF_TRIANGLES_WALL = 20000
VOXEL_COUNT = 20

def get_all_ply_files(root_dir):
    return list(Path(root_dir).rglob("*.ply"))

def reduce_mesh_quality(file_path):
    try:
        original_size = os.path.getsize(file_path)
        mesh = o3d.io.read_triangle_mesh(str(file_path))
        mesh.compute_vertex_normals()

        # Remove duplicate vertices and triangles
        mesh.remove_duplicated_vertices()
        mesh.remove_duplicated_triangles()
        mesh.remove_unreferenced_vertices()

        # Simplification (reduces number of triangles)
        target_number_of_triangles = TARGET_NUMBER_OF_TRIANGLES_STONE if "stone" in str(file_path) else TARGET_NUMBER_OF_TRIANGLES_WALL
        if len(mesh.triangles) > target_number_of_triangles:
            mesh = mesh.simplify_quadric_decimation(target_number_of_triangles=target_number_of_triangles)
            mesh.compute_vertex_normals()

        # Vertex clustering (merges nearby vertices without creating holes)
        # bbox = mesh.get_axis_aligned_bounding_box()
        # largest_length = max(bbox.get_max_bound() - bbox.get_min_bound())
        # vertex_clustering_size = largest_length / VOXEL_COUNT
        # mesh = mesh.simplify_vertex_clustering(voxel_size=vertex_clustering_size)
        # mesh.compute_vertex_normals()

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

if __name__ == "__main__":
    if len(sys.argv) == 1:
        root_folder = os.getcwd()
    else:
        root_folder = sys.argv[1]

    main(root_folder)
