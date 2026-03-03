"""
similarity.py — Cosine Similarity Ponderada por Posição
Botafogo FSA Scouting Pipeline

Dependências: pip install scikit-learn numpy pandas
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional


POSITION_WEIGHTS: Dict[str, Dict[str, float]] = {
    "Atacante": {
        "goals_per_90": 3.0,
        "xg_per_90": 2.5,
        "shots_per_90": 2.0,
        "aerial_duels_won_pct": 1.5,
        "touches_in_box_per_90": 2.0,
        "sprint_count_per_90": 1.0,
        "pressing_index_per_90": 1.0,
        "progressive_carries_per_90": 1.5,
        "pass_completion_pct": 0.5,
        "dribbles_per_90": 1.0,
    },
    "Extremo": {
        "dribbles_per_90": 3.0,
        "progressive_carries_per_90": 2.5,
        "crosses_per_90": 2.0,
        "key_passes_per_90": 2.5,
        "sprint_count_per_90": 2.0,
        "high_speed_running_distance_per_90": 2.0,
        "goals_per_90": 1.5,
        "xg_assisted_per_90": 2.0,
        "pass_completion_pct": 1.0,
        "tackles_per_90": 0.5,
    },
    "Meia": {
        "key_passes_per_90": 3.0,
        "progressive_passes_per_90": 2.5,
        "pass_completion_pct": 2.0,
        "through_balls_per_90": 2.0,
        "xg_assisted_per_90": 2.5,
        "ball_recoveries_per_90": 1.5,
        "smart_passes_per_90": 2.0,
        "dribbles_per_90": 1.5,
        "goals_per_90": 1.0,
        "interceptions_per_90": 1.0,
    },
    "Volante": {
        "tackles_per_90": 3.0,
        "interceptions_per_90": 2.5,
        "ball_recoveries_per_90": 2.5,
        "aerial_duels_won_pct": 2.0,
        "pass_completion_pct": 2.0,
        "progressive_passes_per_90": 1.5,
        "fouls_per_90": 1.0,
        "distance_per_90": 1.5,
        "pressing_index_per_90": 2.0,
        "duels_won_pct": 2.0,
    },
    "Lateral": {
        "crosses_per_90": 2.5,
        "progressive_carries_per_90": 2.0,
        "tackles_per_90": 2.5,
        "interceptions_per_90": 2.0,
        "sprint_count_per_90": 2.5,
        "high_speed_running_distance_per_90": 2.5,
        "key_passes_per_90": 1.5,
        "pass_completion_pct": 1.5,
        "aerial_duels_won_pct": 1.0,
        "dribbles_per_90": 1.5,
    },
    "Zagueiro": {
        "aerial_duels_won_pct": 3.0,
        "tackles_per_90": 2.5,
        "interceptions_per_90": 2.5,
        "clearances_per_90": 2.0,
        "duels_won_pct": 2.0,
        "pass_completion_pct": 1.5,
        "progressive_passes_per_90": 1.0,
        "blocks_per_90": 2.0,
        "fouls_per_90": 1.0,
        "ball_recoveries_per_90": 1.5,
    },
    "Goleiro": {
        "saves_pct": 3.0,
        "clean_sheets_pct": 2.5,
        "goals_prevented_per_90": 2.5,
        "xg_against_per_90": 2.0,
        "passes_completed_pct": 1.5,
        "long_passes_completed_pct": 1.5,
        "aerial_duels_won_pct": 1.0,
        "sweeper_actions_per_90": 2.0,
    },
}


def compute_weighted_cosine_similarity(
    target_player: pd.Series,
    comparison_pool: pd.DataFrame,
    position: str,
    top_n: int = 10,
    min_minutes: int = 450,
) -> pd.DataFrame:
    weights_dict = POSITION_WEIGHTS.get(position)
    if weights_dict is None:
        raise ValueError(f"Posição '{position}' não mapeada em POSITION_WEIGHTS")

    if "minutes_played" in comparison_pool.columns:
        pool = comparison_pool[comparison_pool["minutes_played"] >= min_minutes].copy()
    else:
        pool = comparison_pool.copy()

    available_metrics = [m for m in weights_dict.keys() if m in pool.columns]
    if not available_metrics:
        return pd.DataFrame()

    weights = np.array([weights_dict[m] for m in available_metrics])
    weights = weights / weights.sum()

    X_pool = pool[available_metrics].fillna(0).values
    x_target = target_player[available_metrics].fillna(0).values.reshape(1, -1)

    scaler = StandardScaler()
    X_pool_scaled = scaler.fit_transform(X_pool)
    x_target_scaled = scaler.transform(x_target)

    X_pool_weighted = X_pool_scaled * weights
    x_target_weighted = x_target_scaled * weights

    similarities = cosine_similarity(x_target_weighted, X_pool_weighted)[0]

    pool = pool.copy()
    pool["similarity_score"] = similarities
    pool["similarity_pct"] = (similarities * 100).round(1)

    result = (
        pool.nlargest(top_n + 1, "similarity_score")
        .query("similarity_score < 0.9999")
        .head(top_n)
    )

    return result


def get_similarity_breakdown(
    target: pd.Series,
    similar: pd.Series,
    position: str,
) -> pd.DataFrame:
    weights_dict = POSITION_WEIGHTS.get(position, {})
    available = [
        m for m in weights_dict.keys()
        if m in target.index and m in similar.index
    ]

    rows = []
    for metric in available:
        t_val = float(target.get(metric, 0))
        s_val = float(similar.get(metric, 0))
        weight = weights_dict[metric]
        diff_pct = ((s_val - t_val) / t_val * 100) if t_val != 0 else 0

        rows.append({
            "Métrica": metric,
            "Alvo": round(t_val, 2),
            "Similar": round(s_val, 2),
            "Δ%": round(diff_pct, 1),
            "Peso": weight,
        })

    return pd.DataFrame(rows).sort_values("Peso", ascending=False)
