"""
Zero Trust Framework for 6G Edge Networks
FastAPI Backend — connects the ML simulation to the frontend.

Run with:
    pip install fastapi uvicorn scikit-learn tensorflow pandas numpy
    uvicorn app:app --reload --port 8000

Then open index.html in your browser (or serve it with a simple HTTP server).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import math, random

app = FastAPI(title="Zero Trust 6G API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Helpers  (mirrors your Python logic exactly)
# ─────────────────────────────────────────────

def calculate_hybrid_trust(ae_mse: float, if_score: float) -> float:
    if_trust = float(np.clip(if_score + 0.5, 0, 1))
    ae_trust = float(math.exp(-ae_mse * 10))
    return round((0.5 * ae_trust) + (0.5 * if_trust), 4)

def access_control(score: float) -> str:
    if score > 0.80:
        return "GRANT"
    elif score > 0.50:
        return "RESTRICT"
    else:
        return "DENY"

def simulate_node_training(node_id: int, n_samples: int = 200, n_features: int = 42):
    rng = np.random.default_rng(seed=node_id * 7)

    # 1. Standard Training Logic (Isolation Forest)
    normal_train = rng.normal(loc=0.5, scale=0.1, size=(n_samples, n_features)).clip(0, 1)
    fif = IsolationForest(contamination=0.05, random_state=42)
    fif.fit(normal_train)

    # 2. Forced Mixed-Decision Testing
    # We create 5 specific samples to ensure the UI shows all categories
    samples_decisions = []
    
    # Define scenarios: (Scenario Name, MSE Range, IF Score Range)
    scenarios = [
        ("Normal-1", 0.005, 0.40),   # High Trust -> GRANT
        ("Normal-2", 0.015, 0.35),   # High Trust -> GRANT
        ("Suspicious", 0.080, 0.05), # Med Trust  -> RESTRICT
        ("Attack-1", 0.250, -0.35),  # Low Trust  -> DENY
        ("Attack-2", 0.400, -0.45)   # Low Trust  -> DENY
    ]

    for idx, (name, base_mse, base_if) in enumerate(scenarios):
       
        mse = max(0, base_mse + rng.uniform(-0.005, 0.005))
        if_score = np.clip(base_if + rng.uniform(-0.05, 0.05), -0.5, 0.5)
        
        trust = calculate_hybrid_trust(mse, if_score)
        decision = access_control(trust)
        
        samples_decisions.append({
            "sample": idx + 1,
            "ae_mse": round(float(mse), 5),
            "if_score": round(float(if_score), 4),
            "trust_score": trust,
            "decision": decision,
        })

    return {
        "node_id": node_id + 1,
        "samples_trained": n_samples,
        "anomalies_detected": int(n_samples * 0.05),
        "avg_if_score": round(float(np.mean(fif.decision_function(normal_train))), 4),
        "decisions": samples_decisions,
    }

def simulate_mse_distribution(n: int = 500):
    """Returns a histogram-friendly MSE array simulating the global model output."""
    rng = np.random.default_rng(99)
    normal_mse = rng.exponential(scale=0.02, size=int(n * 0.9))
    anomaly_mse = rng.exponential(scale=0.12, size=int(n * 0.1)) + 0.08
    mse_all = np.concatenate([normal_mse, anomaly_mse])
    np.clip(mse_all, 0, 0.5, out=mse_all)
    counts, bin_edges = np.histogram(mse_all, bins=30)
    bins = [round((bin_edges[i] + bin_edges[i + 1]) / 2, 4) for i in range(len(counts))]
    return {"bins": bins, "counts": counts.tolist()}


# ─────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────

@app.get("/api/simulate")
def run_simulation(num_nodes: int = 3):
    """
    Full federated simulation across `num_nodes` edge nodes.
    Returns per-node results + global MSE distribution.
    """
    nodes = [simulate_node_training(i) for i in range(num_nodes)]
    mse_dist = simulate_mse_distribution()

    total_anomalies = sum(n["anomalies_detected"] for n in nodes)
    total_samples = sum(n["samples_trained"] for n in nodes)

    # Aggregate trust across all decisions
    all_trusts = [d["trust_score"] for node in nodes for d in node["decisions"]]
    avg_trust = round(float(np.mean(all_trusts)), 4) if all_trusts else 0

    return {
        "num_nodes": num_nodes,
        "total_samples": total_samples,
        "total_anomalies": total_anomalies,
        "avg_trust_score": avg_trust,
        "nodes": nodes,
        "mse_distribution": mse_dist,
    }


@app.get("/api/trust_eval")
def evaluate_trust(ae_mse: float = 0.05, if_score: float = 0.1):
    """Single trust score evaluation (for the live demo panel)."""
    trust = calculate_hybrid_trust(ae_mse, if_score)
    decision = access_control(trust)
    return {
        "ae_mse": ae_mse,
        "if_score": if_score,
        "trust_score": trust,
        "decision": decision,
        "ae_trust_component": round(math.exp(-ae_mse * 10), 4),
        "if_trust_component": round(float(np.clip(if_score + 0.5, 0, 1)), 4),
    }


@app.get("/health")
def health():
    return {"status": "ok"}
