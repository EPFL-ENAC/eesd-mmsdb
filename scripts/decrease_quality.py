import multiprocessing
import os
from pathlib import Path
import sys

import open3d as o3d
from tqdm import tqdm

# Configurable parameters
TARGET_SIZE_MB = 1
TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024
TARGET_NUMBER_OF_TRIANGLES_STONE = 5000
TARGET_NUMBER_OF_TRIANGLES_WALL = 100000
VOXEL_COUNT = 20


def get_all_mesh_paths(source_dir: str) -> list[Path]:
    return list(Path(source_dir).rglob("*.ply"))


def reduce_mesh_quality_task(args: tuple[Path, Path]):
    source_path, target_path = args

    try:
        original_size = os.path.getsize(source_path)
        mesh = o3d.io.read_triangle_mesh(str(source_path))
        mesh.compute_vertex_normals()

        # Remove duplicate vertices and triangles
        mesh.remove_duplicated_vertices()
        mesh.remove_duplicated_triangles()
        mesh.remove_unreferenced_vertices()

        # Simplification (reduces number of triangles)
        target_number_of_triangles = (
            TARGET_NUMBER_OF_TRIANGLES_STONE
            if "stone" in str(source_path)
            else TARGET_NUMBER_OF_TRIANGLES_WALL
        )
        if len(mesh.triangles) > target_number_of_triangles:
            mesh = mesh.simplify_quadric_decimation(
                target_number_of_triangles=target_number_of_triangles
            )
            # Fix inside-out stones
            mesh.orient_triangles()
            mesh.compute_vertex_normals()

        # Vertex clustering (merges nearby vertices without creating holes)
        # bbox = mesh.get_axis_aligned_bounding_box()
        # largest_length = max(bbox.get_max_bound() - bbox.get_min_bound())
        # vertex_clustering_size = largest_length / VOXEL_COUNT
        # mesh = mesh.simplify_vertex_clustering(voxel_size=vertex_clustering_size)
        # mesh.compute_vertex_normals()

        # Save as binary PLY (reduces size significantly if it's ASCII)
        o3d.io.write_triangle_mesh(
            str(target_path), mesh, write_ascii=False, compressed=True
        )
        final_size = os.path.getsize(target_path)

        if original_size > 0:
            size_reduction = ((original_size - final_size) / original_size) * 100
        else:
            size_reduction = 0

        if final_size > original_size:
            print(
                f"⚠️ Size increased: {target_path} ({final_size / 1e6:.2f} MB, increased by {abs(size_reduction):.1f}%)"
            )
        elif final_size > TARGET_SIZE_BYTES:
            print(
                f"⚠️ Still >1MB: {target_path} ({final_size / 1e6:.2f} MB, reduced by {size_reduction:.1f}%)"
            )
        else:
            print(
                f"✅ Reduced: {target_path} ({final_size / 1e6:.2f} MB, reduced by {size_reduction:.1f}%)"
            )

    except Exception as e:
        print(f"❌ Error processing {source_path}: {e}")


def main(source_dir: str, target_dir: str, dry_run: bool = False):
    os.makedirs(target_dir, exist_ok=True)

    mesh_paths = get_all_mesh_paths(source_dir)
    print(f"Found {len(mesh_paths)} .ply files.")

    tasks = []
    for source_path in mesh_paths:
        target_path = Path(target_dir) / source_path.relative_to(source_dir)
        if dry_run:
            print(f"Would process: {source_path} -> {target_path}")
        else:
            os.makedirs(target_path.parent, exist_ok=True)
            tasks.append((source_path, target_path))

    if not dry_run and tasks:
        with multiprocessing.Pool() as pool:
            for _ in tqdm(
                pool.imap_unordered(reduce_mesh_quality_task, tasks),
                total=len(tasks),
                desc="Processing",
            ):
                pass


if __name__ == "__main__":
    if len(sys.argv) < 3 or "--help" in sys.argv:
        print(
            "Usage: python decrease_quality.py [--help] <source_dir> <target_dir> [--dry-run]"
        )
        sys.exit(1)

    source_dir = sys.argv[1]
    target_dir = sys.argv[2]
    dry_run = "--dry-run" in sys.argv

    main(source_dir, target_dir, dry_run=dry_run)
