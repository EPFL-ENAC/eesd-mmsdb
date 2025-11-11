import networkx as nx
import numpy as np
import pytest


@pytest.fixture
def image() -> np.ndarray:
    return np.array(
        [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ]
    )


def test_get_connectivity_matrix():
    from api.services.bwgraph import _get_connectivity_matrix

    dim = 2
    connectivity = 3**dim - 1
    conn_matrix = _get_connectivity_matrix(connectivity, dim)
    np.testing.assert_array_equal(
        conn_matrix, np.array([[0, 0, 1], [0, 0, 1], [0, 1, 1]], dtype=bool)
    )


def test_get_base_offsets():
    from api.services.bwgraph import _get_base_offsets

    dim = 2
    conn_matrix = np.array([[0, 0, 1], [0, 0, 1], [0, 1, 1]], dtype=bool)
    base = _get_base_offsets(conn_matrix, dim)
    np.testing.assert_array_equal(base, np.array([[1, 0], [-1, 1], [0, 1], [1, 1]]))
    # np.testing.assert_array_equal(base, np.array([[0, 1], [1, -1], [1, 0], [1, 1]]))


def test_is_interface(image: np.ndarray):
    from api.services.bwgraph import _is_interface

    expected_interfaces = np.array(
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ],
        dtype=bool,
    )
    sz = image.shape
    dim = len(sz)

    interfaces = np.zeros_like(image, dtype=bool)

    for idx in range(image.size):
        i, j = np.unravel_index(idx, image.shape)
        coords = (np.array([i]), np.array([j]))
        interfaces[i, j] = _is_interface(image, coords, sz, dim)

    np.testing.assert_array_equal(interfaces, expected_interfaces)


def test_bwgraph(image: np.ndarray):
    from api.services.bwgraph import bwgraph

    interface_weight = 0.1
    G = bwgraph(image, interface_weight=interface_weight)
    assert G is not None


def test_shortest_path(image: np.ndarray):
    from api.services.bwgraph import bwgraph

    start_point = (0, 3)
    end_point = (5, 3)
    interface_weight = 0.1
    sz = image.shape

    source = np.ravel_multi_index((start_point[0], start_point[1]), sz)
    target = np.ravel_multi_index((end_point[0], end_point[1]), sz)
    G = bwgraph(image, interface_weight=interface_weight)

    path_nodes = nx.shortest_path(G, source=source, target=target, weight="weight")
    expected_path_nodes = [3, 10, 16, 22, 30, 38]
    assert np.array_equal(path_nodes, expected_path_nodes)
