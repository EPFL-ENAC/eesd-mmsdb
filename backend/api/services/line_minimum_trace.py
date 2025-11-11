#!/usr/bin/env python3
"""
line_minimum_trace.py

This script calculates the Line of Minimum Trace for:
- Vertical joints staggering properties
- Horizontal bed joint characteristics
- Wall leaf connections of a masonry wall

Requirements:
- Binary format image (stones labeled as black pixels, mortar as white)
- Wall dimensions (ensure consistent units)

Authors: Mati Ullah Shah, Savvas Saloustros, and Katrin Beyer
Contact: mati.shah@epfl.ch
Last modified: 13 March 2025
Original repository (MATLAB): https://github.com/eesd-epfl/MasonryIndex-3D

Python translation by: GitHub Copilot
Translation date: July 2025

Note:
- The shortest path calculation uses the `bwgraph` function, originally published by
  George Abrahams under the MIT License.
- A slight modification has been made to include the alpha weighing factor,
  which accounts for the ratio of fracture energies of the stone-mortar interface to mortar.
- For further details on the `bwgraph` function, visit:
  https://github.com/WD40andTape/
"""

import base64
import hashlib
import os
from io import BytesIO

import networkx as nx
import numpy as np
from cachetools import TTLCache, cached
from PIL import Image

from .bwgraph import bwgraph


def calculate_line_minimum_trace(
    image_file_path: str,
    start_coords: list,
    end_coords: list,
    real_length: float = 149.0,
    real_height: float = 140.0,
    calculate_LMT: int = 1,
    interface_weight: float = 1.0,
    boundary_margin: int = 5,
    return_plot: bool = True,
) -> dict:
    """
    Calculate Line of Minimum Trace for masonry analysis.

    Parameters
    ----------
    image_file_path : str
        Path to the binary image file
    start_coords : list
        [row, col] coordinates for start point
    end_coords : list
        [row, col] coordinates for end point
    real_length : float
        Real-world length of the masonry panel
    real_height : float
        Real-world height of the masonry panel
    calculate_LMT : int
        Type of analysis: 0=vertical joints, 1=horizontal bed joints, 2=wall leaf connections
    interface_weight : float
        Alpha value for interface weighting (0.1 to 1.0)
    boundary_margin : int
        Boundary margin in pixels
    return_plot : bool
        Whether to return plot image as base64 string

    Returns
    -------
    dict
        Results containing LMT values, path coordinates, and optional plot
    """

    try:
        # Read the binary image
        if not os.path.exists(image_file_path):
            return {
                "error": f"Image file not found at {image_file_path}",
                "success": False,
            }

        image = np.array(Image.open(image_file_path).convert("L"))
        # Convert to binary (assuming white=255 is mortar, black=0 is stone)
        image = (image > 128).astype(bool)

        # Apply boundary conditions based on LMT type
        if boundary_margin:
            if calculate_LMT == 1:  # Horizontal bed joint
                image[:, :boundary_margin] = 1
                image[:, -boundary_margin:] = 1
                image[:boundary_margin, :] = 0
                image[-boundary_margin:, :] = 0
            else:  # Vertical joints or wall leaf connections
                image[:, :boundary_margin] = 0
                image[:, -boundary_margin:] = 0
                image[:boundary_margin, :] = 1
                image[-boundary_margin:, :] = 1

        # Create the graph
        G = bwgraph_cached(image, interface_weight=interface_weight)
        sz = image.shape

        pixel_length = sz[1]  # corresponding length in pixels
        pixel_height = sz[0]  # corresponding height in pixels

        # Calculate the scale factors for length and height
        length_scale_factor = real_length / pixel_length
        height_scale_factor = real_height / pixel_height

        # Validate and adjust coordinates
        start_point = [
            max(0, min(start_coords[1], pixel_height - 1)),
            max(0, min(start_coords[0], pixel_length - 1)),
        ]
        end_point = [
            max(0, min(end_coords[1], pixel_height - 1)),
            max(0, min(end_coords[0], pixel_length - 1)),
        ]

        # Check if points are on valid mortar (white) regions and find nearest if needed
        start_point = _find_nearest_mortar(
            image, start_point, pixel_height, pixel_length
        )
        end_point = _find_nearest_mortar(image, end_point, pixel_height, pixel_length)

        if start_point is None:
            return {"error": "No mortar found near start point", "success": False}

        if end_point is None:
            return {"error": "No mortar found near end point", "success": False}

        # Convert to linear indices
        source = np.ravel_multi_index((start_point[0], start_point[1]), sz)
        target = np.ravel_multi_index((end_point[0], end_point[1]), sz)

        # Check if nodes exist in graph
        if source not in G.nodes or target not in G.nodes:
            return {
                "error": "Start or end point not accessible in mortar network",
                "success": False,
            }

        # Calculate shortest path between start and end points
        try:
            path_nodes = nx.shortest_path(
                G, source=source, target=target, weight="weight"
            )
        except nx.NetworkXNoPath:
            return {"error": "No path found between selected points", "success": False}

        # Convert linear indices back to 2D coordinates
        path_coords = [np.unravel_index(node, sz) for node in path_nodes]
        pi = [coord[0] for coord in path_coords]
        pj = [coord[1] for coord in path_coords]

        # Scale the path coordinates to real-world units
        pi_scaled = np.array(pi) * height_scale_factor
        pj_scaled = np.array(pj) * length_scale_factor

        # Combine x and y coordinates into a matrix
        zigzag_coordinates = np.column_stack((pj_scaled, pi_scaled))

        # Calculate the Euclidean distances between consecutive points
        distances = np.sqrt(np.sum(np.diff(zigzag_coordinates, axis=0) ** 2, axis=1))

        # Sum up the distances to get the total length
        total_length = np.sum(distances)

        # Compute LMT based on the selected option
        if calculate_LMT == 0:
            LMT_type = "vertical"
            LMT_result = total_length / real_height
        elif calculate_LMT == 1:
            LMT_type = "horizontal"
            LMT_result = total_length / real_length
        else:
            LMT_type = "wall_leaf_connection"
            LMT_result = total_length / real_height

        # Ensure LMT values are not less than 1
        LMT_result = max(LMT_result, 1.0)

        # Prepare results
        results = {
            "success": True,
            "lmt_type": LMT_type,
            "lmt_result": float(LMT_result),
            "total_length": float(total_length),
            "path_coordinates": {
                "pixel_coordinates": [[int(pj[i]), int(pi[i])] for i in range(len(pi))],
                "real_world_coordinates": zigzag_coordinates.tolist(),
            },
            "start_point_used": start_point,
            "end_point_used": end_point,
            "image_dimensions": {"width": pixel_length, "height": pixel_height},
            "scale_factors": {
                "length_scale": float(length_scale_factor),
                "height_scale": float(height_scale_factor),
            },
        }

        # Generate plot if requested
        if return_plot:
            plot_base64 = _generate_plot(
                image, pi, pj, start_point, end_point, LMT_type
            )
            results["plot_image"] = plot_base64

        return results

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "success": False}


_bwgraph_cache: TTLCache = TTLCache(maxsize=32, ttl=600)  # Cache for 10 minutes


@cached(
    _bwgraph_cache,
    key=lambda bw, node_weights=None, connectivity=None, interface_weight=1.0: (
        _array_checksum(bw),
        _array_checksum(node_weights),
        connectivity,
        interface_weight,
    ),
)
def bwgraph_cached(
    bw: np.ndarray,
    node_weights: np.ndarray | None = None,
    connectivity: int | None = None,
    interface_weight: float = 1.0,
) -> nx.Graph:
    """Cached version of bwgraph function."""
    return bwgraph(
        bw,
        node_weights=node_weights,
        connectivity=connectivity,
        interface_weight=interface_weight,
    )


def _array_checksum(arr: np.ndarray | None) -> str | None:
    """Compute SHA256 checksum of a numpy array, or None if arr is None."""
    if arr is None:
        return None
    return hashlib.sha256(arr.tobytes()).hexdigest()


def _find_nearest_mortar(image, point, pixel_height, pixel_length, max_radius=10):
    """Find the nearest mortar pixel within a given radius."""
    if image[point[0], point[1]] == 1:
        return point

    # Find nearest mortar pixel within a small radius
    for radius in range(1, max_radius + 1):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                new_y = point[0] + dy
                new_x = point[1] + dx
                if (
                    0 <= new_y < pixel_height
                    and 0 <= new_x < pixel_length
                    and image[new_y, new_x] == 1
                ):
                    return [new_y, new_x]

    return None


def _generate_plot(image, pi, pj, start_point, end_point, lmt_type):
    """Generate plot and return as base64 string."""
    import matplotlib.pyplot as plt

    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.imshow(image, cmap="gray")

        # Plot the shortest path
        ax.plot(pj, pi, "r-", linewidth=4, label="LMT Path")
        ax.plot(
            start_point[1],
            start_point[0],
            "go",
            markersize=10,
            linewidth=2,
            label="Start",
        )
        ax.plot(
            end_point[1], end_point[0], "ro", markersize=10, linewidth=2, label="End"
        )

        ax.legend()
        ax.set_title(f"{lmt_type.title()} Line of Minimum Trace")
        ax.set_xlabel("Pixel X")
        ax.set_ylabel("Pixel Y")

        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
        buffer.seek(0)
        plot_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return plot_base64
    except Exception:
        return None


def main():
    """Main function for standalone testing - can be removed in API usage."""

    # Test parameters
    image_file_path = "/mnt/c/Users/eschmann/Downloads/test_eesd.png"
    start_coords = [5, 100]
    end_coords = [780, 400]

    # Call the API function
    result = calculate_line_minimum_trace(
        image_file_path=image_file_path,
        start_coords=start_coords,
        end_coords=end_coords,
        real_length=149,
        real_height=140,
        calculate_LMT=1,
        interface_weight=1.0,
        boundary_margin=5,
        return_plot=True,
    )

    # Print results
    if result["success"]:
        print("\n" + "=" * 50)
        print("RESULTS SUMMARY")
        print("=" * 50)
        print(f"LMT Type: {result['lmt_type']}")
        print(f"LMT Result: {result['lmt_result']:.3f}")
        print(f"Total Length: {result['total_length']:.2f} units")
        print(f"Start Point Used: {result['start_point_used']}")
        print(f"End Point Used: {result['end_point_used']}")
        print(
            f"Path Length: {len(result['path_coordinates']['pixel_coordinates'])} points"
        )
        print(f"Image: {result['plot_image']}")
        print("=" * 50)

        # Show plot if available
        if "plot_image" in result and result["plot_image"]:
            print("Plot generated successfully")

    else:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()
