"""
Topic clustering implementations: LDA, community detection, embedding clustering.
"""

from collections import Counter, defaultdict
import math


def lda_clustering(
    papers_keywords: list,
    n_topics_range: tuple = (5, 15),
    n_top_words: int = 5,
) -> dict:
    """Simple LDA-like topic clustering using keyword co-occurrence.

    For production, use gensim or scikit-learn LDA. This implementation
    provides a lightweight fallback when those libraries are unavailable.

    Args:
        papers_keywords: List of keyword lists per paper
        n_topics_range: Range of topic numbers to try
        n_top_words: Number of top words per topic

    Returns:
        Dict with 'topics', 'paper_assignments', 'optimal_n_topics'
    """
    # Try using sklearn LDA first
    try:
        return _sklearn_lda(papers_keywords, n_topics_range, n_top_words)
    except ImportError:
        pass

    # Fallback: keyword-based clustering
    return _keyword_based_clustering(papers_keywords, n_top_words)


def _sklearn_lda(papers_keywords, n_topics_range, n_top_words):
    """LDA using scikit-learn."""
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation

    # Convert keyword lists to documents
    docs = [" ".join(kws) for kws in papers_keywords if kws]
    if not docs:
        return {"topics": [], "paper_assignments": [], "optimal_n_topics": 0}

    vectorizer = CountVectorizer(max_features=500, min_df=2)
    doc_term_matrix = vectorizer.fit_transform(docs)
    feature_names = vectorizer.get_feature_names_out()

    # Find optimal n_topics by perplexity
    best_n = n_topics_range[0]
    best_perplexity = float("inf")

    for n_topics in range(n_topics_range[0], n_topics_range[1] + 1):
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            max_iter=20,
            learning_method="online",
            random_state=42,
        )
        lda.fit(doc_term_matrix)
        perplexity = lda.perplexity(doc_term_matrix)
        if perplexity < best_perplexity:
            best_perplexity = perplexity
            best_n = n_topics

    # Final model with optimal n_topics
    lda = LatentDirichletAllocation(
        n_components=best_n,
        max_iter=40,
        learning_method="online",
        random_state=42,
    )
    lda.fit(doc_term_matrix)

    # Extract topics
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        top_weights = [topic[i] / topic.sum() for i in top_indices]
        topics.append({
            "topic_id": topic_idx,
            "keywords": top_words,
            "keyword_weights": dict(zip(top_words, top_weights)),
        })

    # Assign papers to topics
    doc_topic_dist = lda.transform(doc_term_matrix)
    paper_assignments = []
    for i, dist in enumerate(doc_topic_dist):
        primary_topic = dist.argmax()
        paper_assignments.append({
            "paper_index": i,
            "primary_topic": int(primary_topic),
            "topic_probability": float(dist[primary_topic]),
        })

    return {
        "topics": topics,
        "paper_assignments": paper_assignments,
        "optimal_n_topics": best_n,
    }


def _keyword_based_clustering(papers_keywords, n_top_words):
    """Fallback clustering using keyword frequency and co-occurrence."""
    # Count keyword frequencies
    keyword_freq = Counter()
    for kws in papers_keywords:
        for kw in kws:
            keyword_freq[kw] += 1

    # Identify top keywords as cluster seeds
    top_keywords = [kw for kw, _ in keyword_freq.most_common(30)]

    if not top_keywords:
        return {"topics": [], "paper_assignments": [], "optimal_n_topics": 0}

    # Group papers by their highest-frequency keyword
    cluster_map = defaultdict(list)
    for i, kws in enumerate(papers_keywords):
        if not kws:
            continue
        kw_set = set(kws)
        best_kw = max(kw_set, key=lambda k: keyword_freq.get(k, 0))
        cluster_map[best_kw].append(i)

    # Build topics
    topics = []
    paper_assignments = []
    for topic_idx, (seed_kw, paper_indices) in enumerate(cluster_map.items()):
        # Collect all keywords in this cluster
        cluster_kws = Counter()
        for pi in paper_indices:
            for kw in papers_keywords[pi]:
                cluster_kws[kw] += 1

        top_kws = [kw for kw, _ in cluster_kws.most_common(n_top_words)]
        topics.append({
            "topic_id": topic_idx,
            "keywords": top_kws,
            "keyword_weights": {kw: cluster_kws[kw] / sum(cluster_kws.values())
                                for kw in top_kws},
        })

        for pi in paper_indices:
            paper_assignments.append({
                "paper_index": pi,
                "primary_topic": topic_idx,
                "topic_probability": 1.0,
            })

    return {
        "topics": topics,
        "paper_assignments": paper_assignments,
        "optimal_n_topics": len(topics),
    }


def network_clustering(network: dict, resolution: float = 1.0) -> dict:
    """Cluster papers using community detection on keyword co-occurrence network.

    Delegates to network_analysis.detect_communities.
    """
    from . import network_analysis

    result = network_analysis.detect_communities(network, resolution)

    topics = []
    for i, community_nodes in enumerate(result["communities"]):
        topics.append({
            "topic_id": i,
            "keywords": community_nodes,
            "keyword_weights": {},
        })

    return {
        "topics": topics,
        "n_communities": result["n_communities"],
        "modularity": result["modularity"],
    }


def consensus_clustering(
    lda_result: dict,
    network_result: dict,
) -> dict:
    """Cross-validate LDA and network clustering results.

    Topics that appear in both methods get higher confidence.
    """
    lda_topics = lda_result.get("topics", [])
    network_topics = network_result.get("topics", [])

    if not lda_topics or not network_topics:
        best = lda_result if lda_topics else network_result
        best["confidence"] = "low"
        return best

    # Map LDA topics to network communities by keyword overlap
    consensus_topics = []
    for lda_topic in lda_topics:
        lda_kws = set(lda_topic.get("keywords", []))
        best_overlap = 0
        best_net_topic = None

        for net_topic in network_topics:
            net_kws = set(net_topic.get("keywords", []))
            overlap = len(lda_kws & net_kws) / max(len(lda_kws | net_kws), 1)
            if overlap > best_overlap:
                best_overlap = overlap
                best_net_topic = net_topic

        consensus_topics.append({
            "topic_id": lda_topic["topic_id"],
            "keywords": lda_topic.get("keywords", []),
            "keyword_weights": lda_topic.get("keyword_weights", {}),
            "network_overlap": best_overlap,
            "confidence": "high" if best_overlap > 0.3 else "medium",
        })

    return {
        "topics": consensus_topics,
        "optimal_n_topics": len(consensus_topics),
        "lda_n_topics": lda_result.get("optimal_n_topics", 0),
        "network_n_communities": network_result.get("n_communities", 0),
        "network_modularity": network_result.get("modularity", 0),
    }
