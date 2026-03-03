"""
similarity.py - Weighted Cosine Similarity para Tab 7 do app.py
================================================================
Substitui distancia euclidiana por cosine similarity ponderada.

Import no app.py:
    from similarity import compute_weighted_cosine_similarity, get_similarity_breakdown, POSITION_WEIGHTS
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict

# ============================================
# POSITION_WEIGHTS
# ============================================
# Escala: 0.5 (contexto) -> 3.0 (core)
# Nomes = colunas EXATAS do DataFrame WyScout

POSITION_WEIGHTS = {
    'Atacante': {
        'Golos/90': 3.0, 'Golos esperados/90': 3.0, 'Golos sem ser por penalti/90': 2.5,
        'Remates/90': 1.5, 'Remates a baliza, %': 2.0, 'Golos marcados, %': 1.5,
        'Toques na area/90': 1.5, 'Golos de cabeca/90': 1.0,
        'Dribles/90': 1.5, 'Dribles com sucesso, %': 1.5,
        'Duelos ofensivos/90': 1.0, 'Duelos ofensivos ganhos, %': 1.0,
        'Aceleracoes/90': 1.0, 'Faltas sofridas/90': 0.5,
        'Duelos aerios/90': 1.5, 'Duelos aereos ganhos, %': 1.5,
        'Corridas progressivas/90': 1.0, 'Recesao de passes em profundidade/90': 1.0,
        'Passes longos recebidos/90': 0.5,
        'Passes recebidos/90': 0.5, 'Passes/90': 0.5, 'Passes certos, %': 0.5,
        'Assistencias/90': 1.5, 'Assistencias esperadas/90': 1.5,
        'Segundas assistencias/90': 0.5, 'Passes chave/90': 1.0,
        'Acoes defensivas com exito/90': 0.5,
    },
    'Extremo': {
        'Golos/90': 2.0, 'Golos esperados/90': 2.0, 'Remates/90': 1.0,
        'Remates a baliza, %': 1.0, 'Toques na area/90': 1.0, 'Golos marcados, %': 1.0,
        'Assistencias/90': 2.5, 'Assistencias esperadas/90': 2.5,
        'Passes chave/90': 2.0, 'Passes inteligentes/90': 1.5,
        'Segundas assistencias/90': 1.0, 'Terceiras assistencias/90': 0.5,
        'Passes para a area de penalti/90': 1.5,
        'Dribles/90': 2.5, 'Dribles com sucesso, %': 2.0,
        'Duelos ofensivos/90': 1.5, 'Duelos ofensivos ganhos, %': 1.5,
        'Faltas sofridas/90': 0.5, 'Aceleracoes/90': 1.5,
        'Corridas progressivas/90': 1.5, 'Passes progressivos/90': 1.0,
        'Passes progressivos certos, %': 0.5, 'Passes para terco final/90': 1.0,
        'Cruzamentos/90': 1.5, 'Cruzamentos certos, %': 1.0,
        'Cruzamentos para a area de baliza/90': 1.0,
        'Acoes defensivas com exito/90': 0.5,
        'Duelos defensivos/90': 0.5, 'Duelos defensivos ganhos, %': 0.5,
    },
    'Meia': {
        'Assistencias/90': 2.5, 'Assistencias esperadas/90': 2.5,
        'Passes chave/90': 2.5, 'Passes inteligentes/90': 2.0,
        'Passes inteligentes certos, %': 1.5,
        'Segundas assistencias/90': 1.5, 'Terceiras assistencias/90': 1.0,
        'Passes para a area de penalti/90': 1.5,
        'Passes precisos para a area de penalti, %': 1.0,
        'Passes progressivos/90': 2.0, 'Passes progressivos certos, %': 1.5,
        'Corridas progressivas/90': 1.5,
        'Passes para terco final/90': 1.5, 'Passes certos para terco final, %': 1.0,
        'Passes em profundidade/90': 1.5, 'Passes em profundidade certos, %': 1.0,
        'Passes/90': 1.0, 'Passes certos, %': 1.5,
        'Passes longos/90': 1.0, 'Passes longos certos, %': 1.0,
        'Passes para a frente/90': 0.5, 'Passes para a frente certos, %': 0.5,
        'Golos/90': 1.5, 'Golos esperados/90': 1.5, 'Remates/90': 0.5,
        'Toques na area/90': 1.0,
        'Dribles/90': 1.5, 'Dribles com sucesso, %': 1.0, 'Duelos ofensivos/90': 0.5,
        'Acoes defensivas com exito/90': 1.0,
        'Duelos defensivos/90': 0.5, 'Duelos defensivos ganhos, %': 0.5,
        'Intersecoes/90': 0.5,
    },
    'Volante': {
        'Acoes defensivas com exito/90': 2.5, 'Intersecoes/90': 2.5,
        'Intercecoes ajust. a posse': 2.0,
        'Duelos defensivos/90': 2.0, 'Duelos defensivos ganhos, %': 2.0,
        'Cortes/90': 1.5, 'Cortes de carrinho ajust. a posse': 1.0,
        'Remates intercetados/90': 1.0,
        'Duelos/90': 1.5, 'Duelos ganhos, %': 1.5,
        'Duelos aerios/90': 1.5, 'Duelos aereos ganhos, %': 1.5,
        'Passes/90': 1.5, 'Passes certos, %': 2.0,
        'Passes longos/90': 1.5, 'Passes longos certos, %': 1.5,
        'Passes para a frente/90': 1.0, 'Passes para a frente certos, %': 1.0,
        'Passes progressivos/90': 1.5, 'Passes progressivos certos, %': 1.0,
        'Passes para terco final/90': 1.0,
        'Corridas progressivas/90': 0.5, 'Passes em profundidade/90': 0.5,
        'Faltas/90': 1.0, 'Cartoes amarelos/90': 0.5,
    },
    'Lateral': {
        'Cruzamentos/90': 2.0, 'Cruzamentos certos, %': 1.5,
        'Cruzamentos para a area de baliza/90': 1.5,
        'Passes para terco final/90': 1.5, 'Passes certos para terco final, %': 1.0,
        'Toques na area/90': 1.0, 'Passes para a area de penalti/90': 1.0,
        'Corridas progressivas/90': 2.0, 'Passes progressivos/90': 1.5,
        'Passes progressivos certos, %': 1.0, 'Aceleracoes/90': 1.5,
        'Passes em profundidade/90': 1.0,
        'Dribles/90': 1.5, 'Dribles com sucesso, %': 1.0,
        'Duelos ofensivos/90': 1.0, 'Duelos ofensivos ganhos, %': 1.0,
        'Faltas sofridas/90': 0.5,
        'Duelos defensivos/90': 2.0, 'Duelos defensivos ganhos, %': 2.0,
        'Intersecoes/90': 1.5, 'Cortes/90': 1.0,
        'Acoes defensivas com exito/90': 1.5, 'Remates intercetados/90': 0.5,
        'Duelos/90': 1.0, 'Duelos ganhos, %': 1.0,
        'Duelos aerios/90': 1.0, 'Duelos aereos ganhos, %': 1.0,
        'Assistencias/90': 1.5, 'Assistencias esperadas/90': 1.5, 'Passes chave/90': 1.0,
    },
    'Zagueiro': {
        'Duelos defensivos/90': 2.5, 'Duelos defensivos ganhos, %': 2.5,
        'Cortes/90': 2.0, 'Cortes de carrinho ajust. a posse': 1.5,
        'Acoes defensivas com exito/90': 2.0,
        'Duelos aerios/90': 2.5, 'Duelos aereos ganhos, %': 2.5,
        'Golos de cabeca/90': 0.5,
        'Intersecoes/90': 2.0, 'Intercecoes ajust. a posse': 1.5,
        'Remates intercetados/90': 1.0,
        'Passes/90': 1.5, 'Passes certos, %': 2.0,
        'Passes longos/90': 1.5, 'Passes longos certos, %': 1.5,
        'Passes para a frente/90': 1.0, 'Passes para a frente certos, %': 1.0,
        'Passes progressivos/90': 1.0, 'Passes progressivos certos, %': 0.5,
        'Passes para terco final/90': 0.5, 'Corridas progressivas/90': 0.5,
        'Faltas/90': 1.0, 'Cartoes amarelos/90': 0.5,
    },
    'Goleiro': {
        'Defesas, %': 3.0,
        'Golos sofridos/90': 2.5,
        'Remates sofridos/90': 1.0,
        'Golos sofridos esperados/90': 2.0,
        'Golos expectaveis defendidos por 90': 2.5,
        'Duelos aerios/90.1': 1.5, 'Saidas/90': 1.5,
        'Passes para tras recebidos pelo guarda-redes/90': 1.0,
        'Passes longos certos, %': 1.5,
    },
}

# Metricas INVERTIDAS: menor valor = melhor
INVERTED_METRICS = frozenset({
    'Faltas/90', 'Cartoes amarelos/90', 'Cartoes vermelhos/90',
    'Golos sofridos/90', 'Remates sofridos/90', 'Golos sofridos esperados/90',
})


def _safe_float(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    try:
        if isinstance(val, str):
            val = val.replace(',', '.')
        return float(val)
    except (ValueError, TypeError):
        return None


def _percentile_rank(value, series):
    valid = pd.to_numeric(series, errors='coerce').dropna()
    if len(valid) == 0:
        return 50.0
    return float((valid < value).sum() / len(valid) * 100)


def _resolve_metric(metric, columns):
    """Tenta encontrar a coluna exata; se nao, busca sem acentos."""
    if metric in columns:
        return metric
    # fallback: comparar sem acentos
    import unicodedata
    def strip_acc(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    m_stripped = strip_acc(metric)
    for col in columns:
        if strip_acc(col) == m_stripped:
            return col
    return None


def compute_weighted_cosine_similarity(
    target_player,
    comparison_pool,
    position,
    top_n=20,
    min_minutes=500,
    minutes_col='Minutos jogados:',
    player_display_col='JogadorDisplay',
    percentile_base=None,
):
    """
    Weighted cosine similarity. Drop-in replacement para Tab 7.

    Returns DataFrame com colunas originais + 'similarity_pct' + 'matched_metrics'.
    """
    weights = POSITION_WEIGHTS.get(position)
    if weights is None:
        return pd.DataFrame()

    if percentile_base is None:
        percentile_base = comparison_pool

    pool = comparison_pool.copy()
    pool[minutes_col] = pool[minutes_col].apply(_safe_float)
    pool = pool[pool[minutes_col] >= min_minutes]

    if player_display_col in pool.columns and player_display_col in target_player.index:
        pool = pool[pool[player_display_col] != target_player[player_display_col]]

    if len(pool) == 0:
        return pd.DataFrame()

    # Resolver metricas (com fallback sem acentos)
    col_set = set(target_player.index) & set(pool.columns)
    metric_map = {}
    for m in weights:
        resolved = _resolve_metric(m, col_set)
        if resolved:
            metric_map[m] = resolved

    if len(metric_map) < 5:
        return pd.DataFrame()

    # Percentis do target
    target_percs = {}
    for m_key, m_col in metric_map.items():
        val = _safe_float(target_player[m_col])
        if val is not None:
            perc = _percentile_rank(val, percentile_base[m_col])
            if m_key in INVERTED_METRICS:
                perc = 100.0 - perc
            target_percs[m_key] = (perc, m_col)

    metrics_list = list(target_percs.keys())
    if len(metrics_list) < 5:
        return pd.DataFrame()

    t_vec = np.array([target_percs[m][0] for m in metrics_list])
    w_vec = np.array([weights[m] for m in metrics_list])
    wt = t_vec * w_vec
    norm_t = np.linalg.norm(wt)
    if norm_t == 0:
        return pd.DataFrame()

    results = []
    for idx, row in pool.iterrows():
        cand_percs = {}
        for m_key in metrics_list:
            m_col = target_percs[m_key][1]
            val = _safe_float(row[m_col])
            if val is not None:
                perc = _percentile_rank(val, percentile_base[m_col])
                if m_key in INVERTED_METRICS:
                    perc = 100.0 - perc
                cand_percs[m_key] = perc

        common = [m for m in metrics_list if m in cand_percs]
        if len(common) < 5:
            continue

        tv = np.array([target_percs[m][0] for m in common])
        cv = np.array([cand_percs[m] for m in common])
        wv = np.array([weights[m] for m in common])

        wtv = tv * wv
        wcv = cv * wv
        dot = np.dot(wtv, wcv)
        n_t = np.linalg.norm(wtv)
        n_c = np.linalg.norm(wcv)
        if n_t == 0 or n_c == 0:
            continue

        cosine_sim = dot / (n_t * n_c)
        abs_diff = np.abs(tv - cv) * wv
        proximity = max(0.0, 1.0 - np.mean(abs_diff) / 100.0)
        similarity = (0.70 * cosine_sim + 0.30 * proximity) * 100.0

        results.append({
            '_idx': idx,
            'similarity_pct': round(similarity, 1),
            'matched_metrics': len(common),
        })

    if not results:
        return pd.DataFrame()

    df_r = pd.DataFrame(results).sort_values('similarity_pct', ascending=False).head(top_n)
    out = pool.loc[df_r['_idx']].copy()
    out['similarity_pct'] = df_r.set_index('_idx')['similarity_pct']
    out['matched_metrics'] = df_r.set_index('_idx')['matched_metrics']
    return out.sort_values('similarity_pct', ascending=False)


def get_similarity_breakdown(target, similar, position, percentile_base=None):
    """Tabela detalhada comparando target vs similar por metrica."""
    weights = POSITION_WEIGHTS.get(position, {})
    rows = []
    for metric, weight in weights.items():
        t_val = _safe_float(target.get(metric))
        s_val = _safe_float(similar.get(metric))
        if t_val is not None and s_val is not None:
            rows.append({
                'Metrica': metric,
                'Peso': weight,
                'Referencia': round(t_val, 2),
                'Similar': round(s_val, 2),
                'Diferenca': round(s_val - t_val, 2),
                'Invertida': 'sim' if metric in INVERTED_METRICS else '',
            })
    return pd.DataFrame(rows)
