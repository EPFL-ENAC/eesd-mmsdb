import numpy as np
import pytest


@pytest.fixture
def image() -> np.ndarray:
    return np.array(
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
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

    interfaces = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ],
        dtype=bool,
    )
    sz = image.shape
    dim = len(sz)

    for idx in range(image.size):
        i, j = np.unravel_index(idx, image.shape)
        assert _is_interface(image, idx, sz, dim) == interfaces[i, j]


def test_bwgraph(image: np.ndarray):
    from api.services.bwgraph import bwgraph

    interface_weight = 0.1
    G = bwgraph(image, interface_weight=interface_weight)
    assert G is not None
