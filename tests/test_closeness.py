"""Tests for :func:`opsahl_centrality.closeness_centrality`.

Expected values are computed by hand and shown alongside each
assertion, so a reviewer can check them without running the code.
"""

# pylint: disable=missing-function-docstring,redefined-outer-name

from __future__ import annotations

import networkx as nx
import pytest

from opsahl_centrality import closeness_centrality


@pytest.fixture(scope="module")
def path_graph() -> nx.Graph:
    """Three nodes in a line: A-B-C."""
    return nx.Graph([("A", "B"), ("B", "C")])


@pytest.fixture(scope="module")
def star_graph() -> nx.Graph:
    """One centre, three leaves."""
    return nx.Graph([("S", "X"), ("S", "Y"), ("S", "Z")])


@pytest.fixture(scope="module")
def two_components() -> nx.Graph:
    """Two disjoint edges plus one isolated node."""
    graph = nx.Graph([("A", "B"), ("C", "D")])
    graph.add_node("K")
    return graph


def test_closeness_centrality_path(path_graph: nx.Graph) -> None:
    # N = 3, so normalised scores divide by N - 1 = 2.
    # A: 1/1 + 1/2 = 1.5 -> 0.75
    # B: 1/1 + 1/1 = 2.0 -> 1.00
    result = closeness_centrality(path_graph)

    assert result["A"] == pytest.approx(0.75)
    assert result["B"] == pytest.approx(1.0)
    assert result["C"] == pytest.approx(0.75)


def test_closeness_centrality_star(star_graph: nx.Graph) -> None:
    # N = 4, divisor 3.
    # S: 1/1 * 3        = 3.0     -> 1.0
    # X: 1/1 + 1/2 + 1/2 = 2.0    -> 2/3
    result = closeness_centrality(star_graph)

    assert result["S"] == pytest.approx(1.0)
    assert result["X"] == pytest.approx(2 / 3)


def test_closeness_centrality_complete_graph() -> None:
    # Every node reaches every other at distance 1, so the sum is
    # N - 1 and the normalised score is exactly 1.0 for all nodes.
    result = closeness_centrality(nx.complete_graph(4))

    assert all(score == pytest.approx(1.0) for score in result.values())


def test_closeness_centrality_unnormalised(path_graph: nx.Graph) -> None:
    # Same sums as above, without the 1 / (N - 1) scaling.
    result = closeness_centrality(path_graph, normalized=False)

    assert result["A"] == pytest.approx(1.5)
    assert result["B"] == pytest.approx(2.0)


def test_closeness_centrality_disconnected(
    two_components: nx.Graph,
) -> None:
    # N = 5, divisor 4. Unreachable nodes contribute 1/inf = 0.
    # A: reaches only B, at distance 1 -> 1.0 -> 0.25
    result = closeness_centrality(two_components)

    assert result["A"] == pytest.approx(0.25)
    assert result["C"] == pytest.approx(0.25)


def test_closeness_centrality_isolated_node(
    two_components: nx.Graph,
) -> None:
    # K reaches nobody, so its sum of reciprocals is 0.
    result = closeness_centrality(two_components)

    assert result["K"] == 0.0


def test_closeness_centrality_weighted() -> None:
    # A-B weight 2, B-C weight 3, so A reaches C at distance 5.
    # A: 1/2 + 1/5 = 0.7 -> N = 3, divisor 2 -> 0.35
    graph = nx.Graph()
    graph.add_edge("A", "B", weight=2)
    graph.add_edge("B", "C", weight=3)

    result = closeness_centrality(graph, distance="weight")

    assert result["A"] == pytest.approx(0.35)


def test_closeness_centrality_single_node_returns_float(
    path_graph: nx.Graph,
) -> None:
    result = closeness_centrality(path_graph, u="B")

    assert isinstance(result, float)
    assert result == pytest.approx(1.0)


def test_closeness_centrality_single_node_graph() -> None:
    # A lone node has nothing to reach and no N - 1 to divide by.
    result = closeness_centrality(nx.Graph([(1, 1)]))

    assert result[1] == 0.0


def test_closeness_centrality_empty_graph() -> None:
    assert closeness_centrality(nx.Graph()) == {}


def test_closeness_centrality_matches_networkx_on_complete_graph() -> None:
    # The two measures agree only when every distance is 1.
    graph = nx.complete_graph(5)

    ours = closeness_centrality(graph)
    theirs = nx.closeness_centrality(graph)

    assert ours == pytest.approx(theirs)


def test_closeness_centrality_beats_networkx_on_small_components(
    two_components: nx.Graph,
) -> None:
    """The reason this package exists.

    NetworkX scores a node in a two-node component as highly as one
    in the largest component. Opsahl's reciprocal sum does not.
    """
    ours = closeness_centrality(two_components)
    theirs = nx.closeness_centrality(two_components, wf_improved=False)

    assert theirs["A"] == pytest.approx(1.0)
    assert ours["A"] < 1.0
