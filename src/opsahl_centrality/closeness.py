"""Closeness centrality via Tore Opsahl's reciprocal-distance sum."""

from __future__ import annotations

import functools
from typing import Any, Callable, Dict, Hashable, Union, overload

import networkx as nx

PathLengths = Callable[[nx.Graph, Any], Any]


@overload
def closeness_centrality(
    G: nx.Graph,
    u: None = None,
    distance: str | None = None,
    normalized: bool = True,
) -> Dict[Any, float]: ...


@overload
def closeness_centrality(
    G: nx.Graph,
    u: Hashable,
    distance: str | None = None,
    normalized: bool = True,
) -> float: ...


# pylint: disable=too-many-statements
def closeness_centrality(
    G: nx.Graph,
    u: Any | None = None,
    distance: str | None = None,
    normalized: bool = True,
) -> Union[float, Dict[Any, float]]:
    """Calculate closeness centrality using Tore Opsahl's algorithm.

    Sums the reciprocals of the shortest-path distances rather than
    taking the reciprocal of their sum, so unreachable nodes
    contribute ``1 / inf == 0`` instead of making the total infinite.

    See `Opsahl's 2010 post
    <https://toreopsahl.com/2010/03/20/closeness-centrality-in-networks-with-disconnected-components/>`_.
    The parameters are just like those in
    :func:`networkx.closeness_centrality`, except for ``normalized``.

    Parameters
    ----------
    G : networkx.Graph
        A NetworkX graph.
    u : Any or None, optional
        Return only the value for node ``u``.
    distance : str or None, optional
        Use the specified edge attribute as the edge distance in
        shortest-path calculations. If None, every edge has
        distance 1.
    normalized : bool, optional
        If True (default), divide by ``N - 1`` so scores fall in
        ``[0, 1]``. Note this differs from NetworkX's ``wf_improved``,
        which has no counterpart here.

    Returns
    -------
    float or dict
        A single score if ``u`` is given, otherwise a dictionary
        mapping each node to its closeness centrality.
    """

    # Which function to use for Dijkstra's algorithm
    path_length: PathLengths
    if distance is not None:
        path_length = functools.partial(
            nx.single_source_dijkstra_path_length,
            weight=distance,
        )
    else:
        path_length = nx.single_source_shortest_path_length

    # Whether to calculate for all nodes or just one
    if u is None:
        nodes = G.nodes()
    else:
        nodes = [u]

    centrality: Dict[Any, float] = {}
    for n in nodes:
        sp = dict(path_length(G, n))
        totsp: float = functools.reduce(
            lambda x, y: x + 1 / y if y != 0 else x,
            sp.values(),
            0.0,
        )

        if totsp > 0.0 and len(G) > 1:
            centrality[n] = totsp
            # normalize to number of nodes-1 in connected part
            if normalized:
                s = 1 / (len(G) - 1)
                centrality[n] *= s
        else:
            centrality[n] = 0.0

    # Return centralit(y/ies)
    if u is not None:
        return centrality[u]
    return centrality
