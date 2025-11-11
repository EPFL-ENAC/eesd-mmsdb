"""
Translated from https://github.com/eesd-epfl/MasonryIndex-3D/blob/main/02_line_minimum_trace/bwgraph.m.

Originally authored by George Abrahams and published under MIT License.
https://github.com/WD40andTape/bwgraph/
"""

import numpy as np
import networkx as nx
from typing import Optional, Tuple
from itertools import product


def bwgraph(
    bw: np.ndarray,
    node_weights: Optional[np.ndarray] = None,
    connectivity: Optional[int] = None,
    interface_weight: float = 1.0,
) -> nx.Graph:
    """
    Create a graph of connected pixels in 2D images or 3D volumes.

    This function constructs a graph representation of a binary image (2D or
    3D), where nodes correspond to pixels and edges represent connectivity
    between adjacent non-zero pixels. It can be used for shortest path
    analysis between points in the binary structure.

    MODIFICATION:
    This version extends the original function by incorporating an
    "interface_weight" parameter, which influences edge weights based on
    adjacency to the stone-mortar interface. This allows preference
    adjustments for travel paths near the interface:
      - interface_weight = 1: Higher preference for paths along the
        stone-mortar interface.
      - interface_weight < 1: Encourages paths that stay close to the
        stone-mortar interface but also consider shorter distances.

    Parameters
    ----------
    bw : np.ndarray
        Binary image, given as a 2D or 3D, numeric or boolean array.
        Non-zero pixels are considered as mortar (white), while zero
        pixels are stones (black).
    node_weights : np.ndarray, optional
        Node weights, provided as a numeric array of the same size as bw.
        If omitted, Euclidean distance is used as the default edge weight.
    connectivity : int, optional
        Pixel connectivity, defining whether pixels are connected via face,
        edge, or corner. For a 2D image, valid values are 4 (edge) and 8
        (corner), while in 3D, 6 (face), 18 (edge), and 26 (corner) are
        valid. Default is the maximum connectivity.
    interface_weight : float, default=1.0
        A scaling factor (0 to 1) applied to edges near the stone-mortar
        interface. A value of 1 gives equal preference to paths along the
        interface, while values below 1 prioritize paths near but not
        strictly on the interface.

    Returns
    -------
    nx.Graph
        A NetworkX graph object where nodes correspond to non-zero pixels
        in bw, and edges connect adjacent pixels based on the specified
        connectivity. Edge weights reflect either Euclidean distance or
        adjusted values influenced by interface_weight.

    Examples
    --------
    >>> import numpy as np
    >>> bw = np.array([[1, 1, 0], [1, 0, 1], [0, 1, 1]], dtype=bool)
    >>> G = bwgraph(bw, connectivity=4)
    >>> print(G.number_of_nodes(), G.number_of_edges())

    Notes
    -----
    This function is a Python translation of the MATLAB bwgraph function
    by George Abrahams, with modifications for interface weight handling.
    Original source: https://github.com/WD40andTape/bwgraph
    """

    # Validate inputs
    bw = np.asarray(bw, dtype=bool)
    if bw.ndim not in [2, 3]:
        raise ValueError("Input must be 2D or 3D array")

    if node_weights is not None:
        node_weights = np.asarray(node_weights)
        if node_weights.shape != bw.shape:
            raise ValueError("node_weights must have the same shape as bw")

    if interface_weight <= 0:
        raise ValueError("interface_weight must be positive")

    sz = bw.shape
    dim = len(sz)

    # Set default connectivity
    if connectivity is None:
        connectivity = 3**dim - 1

    # Validate connectivity
    if dim == 2 and connectivity not in [4, 8]:
        raise ValueError("Valid connectivities for 2D array are 4 and 8")
    elif dim == 3 and connectivity not in [6, 18, 26]:
        raise ValueError("Valid connectivities for 3D array are 6, 18, and 26")

    # Get connectivity matrix
    conn_matrix = _get_connectivity_matrix(connectivity, dim)

    # Create base offsets for neighbors
    base = _get_base_offsets(conn_matrix, dim)
    conn = len(base)

    # Find indices of all non-zero elements
    nonzero_indices = np.where(bw)
    if dim == 2:
        source = np.column_stack((nonzero_indices[0], nonzero_indices[1]))
    else:
        source = np.column_stack(
            (nonzero_indices[0], nonzero_indices[1], nonzero_indices[2])
        )

    # Generate all neighbor pairs
    n = len(source)
    source_expanded = np.repeat(source, conn, axis=0)
    base_tiled = np.tile(base, (n, 1))
    neighbors = source_expanded + base_tiled

    # Remove invalid neighbors (outside boundaries)
    valid_mask = np.all((neighbors >= 0) & (neighbors < np.array(sz)), axis=1)
    source_valid = source_expanded[valid_mask]
    neighbors_valid = neighbors[valid_mask]

    # Calculate weights if not provided
    if node_weights is None:
        weights = np.linalg.norm(base, axis=1)
        weights_expanded = np.tile(weights, n)
        weights_valid = weights_expanded[valid_mask]

    # Convert to linear indices
    source_linear = np.ravel_multi_index(source_valid.T, sz)
    neighbors_linear = np.ravel_multi_index(neighbors_valid.T, sz)

    # Keep only neighbors that are non-zero in bw
    neighbor_nonzero_mask = bw.flat[neighbors_linear]
    source_final = source_linear[neighbor_nonzero_mask]
    neighbors_final = neighbors_linear[neighbor_nonzero_mask]

    # Calculate final weights
    if node_weights is None:
        weights_final = weights_valid[neighbor_nonzero_mask]
    else:
        # Average of connecting node weights
        weights_final = (
            node_weights.flat[source_final] + node_weights.flat[neighbors_final]
        ) / 2

    # Adjust weights for interface edges
    for i in range(len(source_final)):
        if _is_interface(bw, source_final[i], sz, dim) or _is_interface(
            bw, neighbors_final[i], sz, dim
        ):
            weights_final[i] *= interface_weight

    # Create NetworkX graph
    G = nx.Graph()

    # Add edges with weights
    edges = [
        (int(s), int(n), {"weight": float(w)})
        for s, n, w in zip(source_final, neighbors_final, weights_final)
    ]
    G.add_edges_from(edges)

    return G


def _get_connectivity_matrix(connectivity: int, dim: int) -> np.ndarray:
    """Get binary connectivity matrix based on connectivity type and dimension."""
    if dim == 2:
        if connectivity == 4:
            # 4-connectivity (face-connected)
            matrix = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=bool)
        elif connectivity == 8:
            # 8-connectivity (corner-connected)
            matrix = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=bool)
        # Apply mask to avoid calculating edges twice
        mask = np.array([[0, 0, 1], [0, 0, 1], [0, 1, 1]], dtype=bool)
        matrix = matrix & mask
    else:  # dim == 3, not tested against MATLAB
        if connectivity == 6:
            # 6-connectivity (face-connected)
            matrix = np.zeros((3, 3, 3), dtype=bool)
            matrix[1, 1, 0] = matrix[1, 1, 2] = True  # z-neighbors
            matrix[1, 0, 1] = matrix[1, 2, 1] = True  # y-neighbors
            matrix[0, 1, 1] = matrix[2, 1, 1] = True  # x-neighbors
        elif connectivity == 18:
            # 18-connectivity (edge-connected)
            matrix = np.zeros((3, 3, 3), dtype=bool)
            # Face neighbors
            matrix[1, 1, 0] = matrix[1, 1, 2] = True
            matrix[1, 0, 1] = matrix[1, 2, 1] = True
            matrix[0, 1, 1] = matrix[2, 1, 1] = True
            # Edge neighbors
            for i, j, k in product([0, 2], repeat=3):
                if sum([i == 1, j == 1, k == 1]) == 1:
                    matrix[i, j, k] = True
        elif connectivity == 26:
            # 26-connectivity (corner-connected)
            matrix = np.ones((3, 3, 3), dtype=bool)
            matrix[1, 1, 1] = False  # Center pixel
        # Apply 3D mask
        mask = np.zeros((3, 3, 3), dtype=bool)
        mask[:, :, 0] = [[0, 0, 1], [0, 0, 1], [0, 1, 1]]
        mask[:, :, 1] = [[0, 0, 1], [0, 0, 1], [0, 1, 1]]
        mask[:, :, 2] = [[0, 0, 1], [0, 1, 1], [0, 1, 1]]
        matrix = matrix & mask

    return matrix


def _get_base_offsets(conn_matrix: np.ndarray, dim: int) -> np.ndarray:
    """Get base offset vectors for neighbors."""
    if dim == 2:
        base_i, base_j = np.mgrid[-1:2, -1:2]
        indices = np.where(conn_matrix.T)  # Transpose to match MATLAB order
        base = np.column_stack((base_i.T[indices], base_j.T[indices]))
    else:  # dim == 3, not tested against MATLAB
        base_i, base_j, base_k = np.mgrid[-1:2, -1:2, -1:2]
        indices = np.where(conn_matrix)
        base = np.column_stack((base_i[indices], base_j[indices], base_k[indices]))

    return base


def _is_interface(bw: np.ndarray, idx: int, sz: Tuple[int, ...], dim: int) -> bool:
    """Check if a pixel is at the stone-mortar interface."""
    # Convert linear index to subscripts
    coords = np.unravel_index(idx, sz)

    neighbors: list[tuple[int, int]] | list[tuple[int, int, int]]

    if dim == 2:
        i, j = coords
        # Check 4-connected neighbors
        neighbors = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
    else:  # dim == 3
        i, j, k = coords
        # Check 6-connected neighbors
        neighbors = [
            (i - 1, j, k),
            (i + 1, j, k),
            (i, j - 1, k),
            (i, j + 1, k),
            (i, j, k - 1),
            (i, j, k + 1),
        ]

    # Check if any neighbor is outside bounds or is zero (stone)
    for neighbor in neighbors:
        # Check bounds
        if any(n < 0 or n >= s for n, s in zip(neighbor, sz)):
            continue

        # Check if neighbor is stone (zero)
        if not bw[neighbor]:
            return True

    return False


# Example usage and testing
if __name__ == "__main__":
    # Test with a simple 2D binary image
    bw_2d = np.array([[1, 1, 0], [1, 0, 1], [0, 1, 1]], dtype=bool)

    print("2D Example:")
    G_2d = bwgraph(bw_2d, connectivity=4)
    print(f"Nodes: {G_2d.number_of_nodes()}, Edges: {G_2d.number_of_edges()}")

    # Test with interface weighting
    G_2d_weighted = bwgraph(bw_2d, connectivity=4, interface_weight=0.5)
    print(
        f"With interface weighting - Nodes: {G_2d_weighted.number_of_nodes()}, "
        f"Edges: {G_2d_weighted.number_of_edges()}"
    )

    # Test with 3D data
    bw_3d = np.zeros((3, 3, 3), dtype=bool)
    bw_3d[1, :, :] = True  # Middle slice all mortar
    bw_3d[0, 1, 1] = True  # One connection to previous slice
    bw_3d[2, 1, 1] = True  # One connection to next slice

    print("\n3D Example:")
    G_3d = bwgraph(bw_3d, connectivity=6)
    print(f"Nodes: {G_3d.number_of_nodes()}, Edges: {G_3d.number_of_edges()}")
