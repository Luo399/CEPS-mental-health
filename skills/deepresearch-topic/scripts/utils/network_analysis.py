"""
Keyword co-occurrence network construction and analysis.
"""

from collections import defaultdict, Counter
from itertools import combinations
import math


def build_cooccurrence_matrix(
    papers_keywords: list,
    min_cooccurrence: int = 2,
    weighting: str = "jaccard",
) -> dict:
    """Build keyword co-occurrence network from papers.

    Args:
        papers_keywords: List of keyword lists, one per paper
        min_cooccurrence: Minimum co-occurrence count to include edge
        weighting: 'binary', 'frequency', or 'jaccard'

    Returns:
        Dict with 'nodes', 'edges', 'adjacency'
    """
    # Count co-occurrences
    cooccurrence = Counter()
    keyword_freq = Counter()

    for keywords in papers_keywords:
        unique_kw = list(set(keywords))  # Deduplicate within paper
        for kw in unique_kw:
            keyword_freq[kw] += 1
        for kw1, kw2 in combinations(sorted(unique_kw), 2):
            cooccurrence[(kw1, kw2)] += 1

    # Filter by minimum co-occurrence
    filtered_edges = {pair: count for pair, count in cooccurrence.items()
                      if count >= min_cooccurrence}

    # Build node set from filtered edges
    active_nodes = set()
    for (kw1, kw2) in filtered_edges:
        active_nodes.add(kw1)
        active_nodes.add(kw2)

    # Calculate edge weights
    edges = []
    for (kw1, kw2), count in filtered_edges.items():
        if weighting == "binary":
            weight = 1.0
        elif weighting == "frequency":
            weight = count
        elif weighting == "jaccard":
            union = keyword_freq[kw1] + keyword_freq[kw2] - count
            weight = count / union if union > 0 else 0
        else:
            weight = count

        edges.append({
            "source": kw1,
            "target": kw2,
            "weight": weight,
            "cooccurrence": count,
        })

    # Sort edges by weight descending
    edges.sort(key=lambda e: e["weight"], reverse=True)

    nodes = [{"id": kw, "frequency": keyword_freq[kw]} for kw in sorted(active_nodes)]

    return {
        "nodes": nodes,
        "edges": edges,
        "keyword_frequencies": dict(keyword_freq),
    }


def compute_centrality(network: dict) -> dict:
    """Compute centrality metrics for the co-occurrence network.

    Uses pure Python implementation (no NetworkX dependency required).

    Returns:
        Dict mapping keyword -> {degree, betweenness, closeness}
    """
    nodes = network["nodes"]
    edges = network["edges"]

    if not nodes or not edges:
        return {}

    # Build adjacency list
    adj = defaultdict(set)
    node_ids = {n["id"] for n in nodes}

    for edge in edges:
        adj[edge["source"]].add(edge["target"])
        adj[edge["target"]].add(edge["source"])

    n = len(node_ids)
    if n == 0:
        return {}

    # Degree centrality
    centrality = {}
    for node_id in node_ids:
        degree = len(adj[node_id])
        centrality[node_id] = {
            "degree": degree,
            "degree_centrality": degree / (n - 1) if n > 1 else 0,
            "betweenness": 0.0,
            "closeness": 0.0,
        }

    # Betweenness centrality (simplified: sample-based for large networks)
    node_list = list(node_ids)
    sample_nodes = node_list if n <= 100 else node_list[:50]

    for s in sample_nodes:
        # BFS from s
        dist = {s: 0}
        pred = defaultdict(list)
        sigma = defaultdict(int)
        sigma[s] = 1
        queue = [s]
        stack = []

        while queue:
            v = queue.pop(0)
            stack.append(v)
            for w in adj[v]:
                if w not in dist:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist.get(w) == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)

        # Accumulate betweenness
        delta = defaultdict(float)
        while stack:
            w = stack.pop()
            for v in pred[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != s:
                centrality[w]["betweenness"] += delta[w]

    # Normalize betweenness
    scale = 2.0 / (n * (n - 1)) if n > 1 else 1.0
    for node_id in node_ids:
        centrality[node_id]["betweenness"] *= scale

    # Closeness centrality (for sampled nodes to limit computation)
    for s in sample_nodes:
        # BFS from s
        visited = {s}
        queue = [(s, 0)]
        total_dist = 0
        reachable = 0

        while queue:
            v, d = queue.pop(0)
            for w in adj[v]:
                if w not in visited:
                    visited.add(w)
                    queue.append((w, d + 1))
                    total_dist += d + 1
                    reachable += 1

        if reachable > 0:
            centrality[s]["closeness"] = reachable / total_dist

    return centrality


def detect_communities(network: dict, resolution: float = 1.0) -> dict:
    """Detect communities using Louvain-like algorithm (simplified).

    For production use, consider using python-louvain or networkx.community.

    Returns:
        Dict with 'communities' (list of node lists) and 'modularity'
    """
    nodes = network["nodes"]
    edges = network["edges"]

    if not nodes or not edges:
        return {"communities": [], "modularity": 0}

    # Build adjacency with weights
    adj = defaultdict(lambda: defaultdict(float))
    node_ids = {n["id"] for n in nodes}
    total_weight = 0.0

    for edge in edges:
        adj[edge["source"]][edge["target"]] += edge["weight"]
        adj[edge["target"]][edge["source"]] += edge["weight"]
        total_weight += edge["weight"]

    if total_weight == 0:
        return {"communities": [list(node_ids)], "modularity": 0}

    # Initialize: each node in its own community
    community = {node: i for i, node in enumerate(node_ids)}
    n_communities = len(node_ids)

    # Louvain phase 1: local moves
    improved = True
    while improved:
        improved = False
        for node in list(node_ids):
            current_comm = community[node]
            # Compute weighted degree
            ki = sum(adj[node].values())

            # Find neighbor communities
            neighbor_comms = defaultdict(float)
            for neighbor, weight in adj[node].items():
                neighbor_comms[community[neighbor]] += weight

            if not neighbor_comms:
                continue

            # Compute gain for moving to each neighbor community
            best_gain = 0
            best_comm = current_comm

            sigma_total = defaultdict(float)
            for n_id in node_ids:
                sigma_total[community[n_id]] += sum(adj[n_id].values())

            for comm, ki_in in neighbor_comms.items():
                if comm == current_comm:
                    continue
                sigma_c = sigma_total[comm]
                gain = ki_in - resolution * ki * sigma_c / total_weight
                if gain > best_gain:
                    best_gain = gain
                    best_comm = comm

            if best_comm != current_comm:
                community[node] = best_comm
                improved = True

    # Collect communities
    comm_map = defaultdict(list)
    for node, comm in community.items():
        comm_map[comm].append(node)

    communities = list(comm_map.values())

    # Compute modularity
    modularity = 0.0
    for comm_nodes in communities:
        comm_set = set(comm_nodes)
        lc = 0.0
        dc = 0.0
        for node in comm_nodes:
            dc += sum(adj[node].values())
            for neighbor, weight in adj[node].items():
                if neighbor in comm_set:
                    lc += weight
        lc /= 2  # Each edge counted twice
        modularity += (lc / total_weight) - (dc / (2 * total_weight)) ** 2

    return {
        "communities": communities,
        "modularity": modularity,
        "n_communities": len(communities),
    }


def identify_bridge_keywords(centrality: dict, node_count: int = None) -> list:
    """Identify bridge keywords: high betweenness + low degree.

    These keywords connect different research streams and indicate
    cross-domain integration opportunities.
    """
    if not centrality:
        return []

    # Compute percentiles
    betweenness_values = [v["betweenness"] for v in centrality.values()]
    degree_values = [v["degree"] for v in centrality.values()]

    betweenness_values.sort()
    degree_values.sort()

    n = len(betweenness_values)
    if n == 0:
        return []

    p75_b = betweenness_values[int(n * 0.75)] if n > 4 else betweenness_values[-1]
    p25_d = degree_values[int(n * 0.25)] if n > 4 else degree_values[0]

    bridges = []
    for kw, metrics in centrality.items():
        if metrics["betweenness"] >= p75_b and metrics["degree"] <= p25_d:
            bridges.append({
                "keyword": kw,
                "betweenness": metrics["betweenness"],
                "degree": metrics["degree"],
                "degree_centrality": metrics["degree_centrality"],
            })

    bridges.sort(key=lambda x: x["betweenness"], reverse=True)
    return bridges


def compute_network_density(network: dict) -> float:
    """Compute network density."""
    n = len(network["nodes"])
    m = len(network["edges"])
    if n <= 1:
        return 0.0
    max_edges = n * (n - 1) / 2
    return m / max_edges
