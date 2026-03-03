"""
fuzzy_match.py — Módulo de Fuzzy Matching para SkillCorner
Botafogo FSA Scouting Pipeline

Dependências: pip install rapidfuzz unidecode
"""

from rapidfuzz import fuzz, process
from unidecode import unidecode
from typing import Optional, Dict
import pandas as pd


def normalize_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    return unidecode(name).lower().strip()


def build_skillcorner_index(
    df_skillcorner: pd.DataFrame,
    name_col: str = "player_name",
) -> Dict[str, int]:
    index = {}
    for idx, row in df_skillcorner.iterrows():
        normalized = normalize_name(row[name_col])
        if normalized:
            index[normalized] = idx
    return index


def find_skillcorner_player(
    player_name: str,
    club_name: str,
    sc_index: Dict[str, int],
    df_skillcorner: pd.DataFrame,
    name_col: str = "player_name",
    team_col: str = "team_name",
    threshold: int = 80,
) -> Optional[int]:
    query = normalize_name(player_name)
    if not query:
        return None

    # Fase 1: match exato
    if query in sc_index:
        return sc_index[query]

    # Fase 2: fuzzy com token_sort_ratio
    candidates = list(sc_index.keys())
    if not candidates:
        return None

    result = process.extractOne(
        query,
        candidates,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=threshold,
    )

    if result is None:
        return None

    match_name, score, _ = result

    # Fase 3: validar pelo clube se score < 90
    if score < 90:
        candidate_idx = sc_index[match_name]
        candidate_club = normalize_name(
            str(df_skillcorner.loc[candidate_idx, team_col])
        )
        query_club = normalize_name(club_name)
        club_score = fuzz.token_sort_ratio(query_club, candidate_club)

        if club_score < 60:
            return None

    return sc_index[match_name]
