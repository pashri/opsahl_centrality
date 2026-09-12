# opsahl-centrality

An implementation of [Tore Opsahl's closeness centrality algorithm][post]
for NetworkX, as an alternative to Linton Freeman's.

[NetworkX's `closeness_centrality()`][nx] uses [Freeman's algorithm][freeman],
which takes the reciprocal of the sum of distances. That breaks on
disconnected graphs: an unreachable node is at infinite distance, so the
sum is infinite and the score collapses to zero. NetworkX works around it
by measuring each node only within its own component, which then scores a
node in a tiny component as highly as one at the heart of the graph.

Opsahl's reformulation sums the *reciprocals* of the distances instead.
An unreachable node contributes `1 / inf == 0` and simply drops out, so
disconnected graphs need no special handling.

## Install

```sh
uv add git+https://github.com/pashri/opsahl_centrality
```

```sh
pip install git+https://github.com/pashri/opsahl_centrality
```

## Usage

```python
import networkx as nx
from opsahl_centrality import closeness_centrality

G = nx.Graph([("A", "B"), ("B", "C")])
G.add_node("D")  # isolated

closeness_centrality(G)
# {'A': 0.5, 'B': 0.6666666666666666, 'C': 0.5, 'D': 0.0}

closeness_centrality(G, u="B")          # a single node
closeness_centrality(G, distance="weight")  # weighted edges
closeness_centrality(G, normalized=False)   # raw sums
```

## Differences from NetworkX

The signature mirrors `nx.closeness_centrality()` with one exception:
this takes `normalized` where NetworkX takes `wf_improved`.

They are not the same thing. `wf_improved` applies the Wasserman–Faust
correction, scaling each score by the fraction of the graph a node can
reach, to compensate for Freeman's formula overrating nodes in small
components. Opsahl's measure has no such flaw to correct — unreachable
nodes contribute zero on their own — so there is nothing for it to do.

`normalized` (default `True`) divides by `N - 1`, the largest sum
attainable when every other node is one hop away, putting scores in
`[0, 1]`. This matches the normalisation in Opsahl's post.

## Development

```sh
uv sync
uv run pytest
uv run pylint src tests
uv run mypy
uv run isort --check-only src tests
uv run numpydoc lint src/opsahl_centrality/*.py
```

Supports Python 3.8+ and NetworkX 2.3+; CI tests both floors.

To release: bump `version` in `pyproject.toml`, then tag and push.
Pushing a `v*` tag runs the checks, builds, and publishes the release;
it fails if the tag and the project version disagree.

```sh
git tag -a v1.1.0 -m "v1.1.0" && git push origin v1.1.0
```

[post]: https://toreopsahl.com/2010/03/20/closeness-centrality-in-networks-with-disconnected-components/
[nx]: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.closeness_centrality.html
[freeman]: http://leonidzhukov.ru/hse/2013/socialnetworks/papers/freeman79-centrality.pdf
