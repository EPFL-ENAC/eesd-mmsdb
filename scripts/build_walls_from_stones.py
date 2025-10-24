"""Rebuild wall mesh from stones."""

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


def build_wall_mesh(args: tuple[Path, list[Path]]):
    wall_path, stone_paths = args

    wall_mesh = o3d.geometry.TriangleMesh()

    for stone_path in stone_paths:
        stone_mesh = o3d.io.read_triangle_mesh(str(stone_path))
        wall_mesh += stone_mesh

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
                pool.imap_unordered(build_wall_mesh, tasks),
                total=len(tasks),
                desc="Processing",
            ):
                pass


if __name__ == "__main__":
    if len(sys.argv) < 2 or "--help" in sys.argv:
        print(
            "Usage: python build_walls_from_stones.py [--help] <dir_path> [--dry-run]"
        )
        sys.exit(1)

    dir_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    main(dir_path, dry_run=dry_run)
