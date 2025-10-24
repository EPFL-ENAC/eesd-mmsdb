"""Aggregate the bounding boxes of stones, the shift the center of the wall mesh accordingly."""

import multiprocessing
import sys
from pathlib import Path

import numpy as np
import open3d as o3d
from tqdm import tqdm


def get_all_wall_paths(source_dir: str) -> list[Path]:
    return list(Path(source_dir).rglob("*02_Wall_data/**/*.ply"))


def get_stone_paths_for_wall(wall_path: Path) -> list[Path]:
    stone_dir = wall_path.parent.parent / "01_Stones_data"
    stone_paths = list(stone_dir.rglob("*.ply"))
    return stone_paths


def shift_wall_mesh(args: tuple[Path, list[Path]]):
    wall_path, stone_paths = args

    corners = None

    for stone_path in stone_paths:
        stone_mesh = o3d.io.read_triangle_mesh(str(stone_path))
        stone_bbox = stone_mesh.get_axis_aligned_bounding_box()
        stone_corners = np.asarray(stone_bbox.get_box_points())
        if corners is None:
            corners = stone_corners
        else:
            corners = np.vstack((corners, stone_corners))

    stones_bbox = o3d.geometry.AxisAlignedBoundingBox.create_from_points(
        o3d.utility.Vector3dVector(corners)
    )

    wall_mesh = o3d.io.read_triangle_mesh(str(wall_path))
    wall_bbox = wall_mesh.get_axis_aligned_bounding_box()
    wall_center = wall_bbox.get_center()
    stones_center = stones_bbox.get_center()
    wall_mesh.translate(stones_center - wall_center)

    o3d.io.write_triangle_mesh(
        str(wall_path), wall_mesh, write_ascii=False, compressed=True
    )


def main(dir_path: str, dry_run: bool = False):
    wall_paths = get_all_wall_paths(dir_path)
    print(f"Found {len(wall_paths)} walls.")

    tasks = []
    for wall_path in wall_paths:
        stone_paths = get_stone_paths_for_wall(wall_path)
        if dry_run:
            print(f"Would process: {wall_path} with {len(stone_paths)} stones")
        else:
            tasks.append((wall_path, stone_paths))

    if not dry_run and tasks:
        with multiprocessing.Pool() as pool:
            for _ in tqdm(
                pool.imap_unordered(shift_wall_mesh, tasks),
                total=len(tasks),
                desc="Processing",
            ):
                pass


if __name__ == "__main__":
    if len(sys.argv) < 2 or "--help" in sys.argv:
        print("Usage: python fix_wall_shift.py [--help] <dir_path> [--dry-run]")
        sys.exit(1)

    dir_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    main(dir_path, dry_run=dry_run)
