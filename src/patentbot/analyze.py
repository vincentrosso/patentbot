"""
Analysis module - clustering and gap analysis for patent portfolios
"""
import json
import numpy as np
from typing import Any
from collections import Counter, defaultdict
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def cluster_patents(
    embeddings: np.ndarray,
    n_clusters: int = 10
) -> tuple[np.ndarray, float]:
    """Cluster patents using KMeans"""
    # Determine optimal clusters if not specified
    if n_clusters is None:
        # Use silhouette score to find optimal k
        best_k, best_score = 2, -1
        for k in range(3, min(20, len(embeddings))):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
            score = silhouette_score(embeddings, labels)
            if score > best_score:
                best_k, best_score = k, score
        n_clusters = best_k
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)
    score = silhouette_score(embeddings, labels)
    
    return labels, score

def analyze_cpc_distribution(patents: list[dict[str, Any]]) -> Dict[str, Any]:
    """Analyze CPC code distribution"""
    cpc_counter = Counter()
    
    for patent in patents:
        cpc_codes = patent.get("cpc_codes", [])
        if isinstance(cpc_codes, str):
            cpc_codes = json.loads(cpc_codes)
        
        # Get top-level CPC classes
        for cpc in cpc_codes:
            if cpc:
                top_class = cpc.split("/")[0] if "/" in cpc else cpc
                cpc_counter[top_class] += 1
    
    return {
        "distribution": dict(cpc_counter.most_common()),
        "total_unique": len(cpc_counter),
        "coverage": dict(cpc_counter)
    }

def find_white_space_gaps(
    company_patents: list[dict[str, Any]],
    competitor_patents: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Find white-space gaps - CPC classes in competitor but not in company"""
    company_cpcs = set()
    competitor_cpcs = set()
    
    for patent in company_patents:
        cpc_codes = patent.get("cpc_codes", [])
        if isinstance(cpc_codes, str):
            cpc_codes = json.loads(cpc_codes)
        for cpc in cpc_codes:
            if cpc:
                company_cpcs.add(cpc.split("/")[0])
    
    for patent in competitor_patents:
        cpc_codes = patent.get("cpc_codes", [])
        if isinstance(cpc_codes, str):
            cpc_codes = json.loads(cpc_codes)
        for cpc in cpc_codes:
            if cpc:
                competitor_cpcs.add(cpc.split("/")[0])
    
    gaps = competitor_cpcs - company_cpcs
    
    return [{"cpc_class": cpc, "opportunity": "potential_gap"} for cpc in gaps]

def generate_cluster_report(
    patents: list[dict[str, Any]],
    labels: np.ndarray,
    cpc_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a cluster report with insights"""
    clusters = defaultdict(list)
    
    for patent, label in zip(patents, labels):
        clusters[label].append(patent)
    
    cluster_report = {}
    
    for cluster_id, cluster_patents in clusters.items():
        # Get dominant CPC codes
        cpc_counter = Counter()
        for patent in cluster_patents:
            cpc_codes = patent.get("cpc_codes", [])
            if isinstance(cpc_codes, str):
                cpc_codes = json.loads(cpc_codes)
            for cpc in cpc_codes:
                if cpc:
                    cpc_counter[cpc.split("/")[0]] += 1
        
        # Get top tags
        tag_counter = Counter()
        for patent in cluster_patents:
            tags = patent.get("tags", [])
            if isinstance(tags, str):
                tags = json.loads(tags)
            tag_counter.update(tags)
        
        # Get titles for this cluster
        titles = [p.get("title", "") for p in cluster_patents[:5]]
        
        cluster_report[f"cluster_{cluster_id}"] = {
            "patent_count": len(cluster_patents),
            "dominant_cpc": cpc_counter.most_common(5),
            "top_tags": tag_counter.most_common(10),
            "sample_titles": titles
        }
    
    return cluster_report

def analyze_citations(patents: list[dict[str, Any]]) -> Dict[str, Any]:
    """Analyze citation patterns"""
    forward_cites = []
    backward_cites = []
    
    for patent in patents:
        fwd = patent.get("forward_citations", [])
        if isinstance(fwd, str):
            fwd = json.loads(fwd)
        backward = patent.get("backward_citations", [])
        if isinstance(backward, str):
            backward = json.loads(backward)
        
        forward_cites.extend(fwd)
        backward_cites.extend(backward)
    
    return {
        "total_forward_citations": len(forward_cites),
        "total_backward_citations": len(backward_cites),
        "unique_forward_cited": len(set(forward_cites)),
        "unique_backward_cited": len(set(backward_cites))
    }

if __name__ == "__main__":
    print("Analysis module loaded")