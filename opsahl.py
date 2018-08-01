import functools
import networkx as nx

def opsahl(G, u=None, distance=None, normalized=True):
    """Calculates closeness centrality using Tore Opsahl's algorithm.
    See: https://toreopsahl.com/2010/03/20/closeness-centrality-in-networks-with-disconnected-components/
    The parameters are just like those in networkx.closeness_centrality()
    
    Parameters
    ----------
    G (graph) –
        A NetworkX graph.
    u (node, optional) –
        Return only the value for node u.
    distance (edge attribute key, optional (default=None)) –
        Use the specified edge attribute as the edge distance
        in shortest path calculations.
    normalized (bool, optional) –
        If True (default) normalize by the number of nodes
        in the connected part of the graph.
    
    Returns
    -------
    nodes –
        Dictionary of nodes with closeness centrality as the value.
    """
    
    # Which function to use for Dijkstra's algorithm
    if distance is not None:
        path_length = functools.partial(nx.single_source_dijkstra_path_length,
                                        weight=distance)
    else:
        path_length = nx.single_source_shortest_path_length

    # Whether to calculate for all nodes or just one
    if u is None:
        nodes = G.nodes()
    else:
        nodes = [u]
    
    closeness_centrality = {}
    for n in nodes:
        sp = dict(path_length(G, n))
        totsp = functools.reduce(lambda x, y: x + 1/y if y!=0 else x, sp.values(), 0.0)
        
        if totsp > 0.0 and len(G) > 1:
            closeness_centrality[n] = totsp
            # normalize to number of nodes-1 in connected part
            if normalized:
                s = 1 / ( len(G) - 1 )
                closeness_centrality[n] *= s
        else:
            closeness_centrality[n] = 0.0
    
    # Return centralit(y/ies)
    if u is not None:
        return closeness_centrality[u]
    else:
        return closeness_centrality
