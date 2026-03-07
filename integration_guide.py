"""
integration_guide.py — Guia de Integração do Motor Preditivo
=============================================================

Como substituir a lógica descritiva do similarity.py pelo predictive_engine.py
no app.py do dashboard Streamlit.

Execução: python integration_guide.py (para validar imports e pipeline)
"""

import numpy as np
import pandas as pd

# ================================================================
# 1. SUBSTITUIÇÃO DE IMPORTS NO app.py
# ================================================================
"""
ANTES (similarity.py descritivo):
    from similarity import (
        compute_weighted_cosine_similarity, get_similarity_breakdown,
        calculate_weighted_index, calculate_all_indices,
        calculate_overall_score, rank_players_weighted,
        get_top_metrics_for_position, calculate_metric_percentiles,
        POSITION_WEIGHTS, INVERTED_METRICS
    )

DEPOIS (predictive_engine.py):
    from predictive_engine import (
        # Motor preditivo principal
        ScoutScorePreditivo,
        ContractSuccessPredictor,
        # Módulos individuais
        DataPreprocessor,
        PositionFeatureSelector,
        WinProbabilityModel,
        xGResidualModel,
        TacticalClusterer,
        AdvancedSimilarity,
        # Drop-in replacements (backward compatible)
        calculate_overall_score_v3,
        compute_advanced_similarity,
        # Constantes
        POSITION_PROFILES,
        INVERTED_METRICS,
    )
    # Manter import legacy para funções ainda não migradas
    from similarity import (
        calculate_weighted_index, calculate_all_indices,
        get_top_metrics_for_position, calculate_metric_percentiles,
        POSITION_WEIGHTS,
    )
"""


# ================================================================
# 2. INICIALIZAÇÃO DO ENGINE (no início do app.py, após load de dados)
# ================================================================

def initialize_predictive_engine(df_all: pd.DataFrame, position: str):
    """
    Chamado uma vez por sessão/posição.
    Cachear com @st.cache_resource no Streamlit.

    Uso no app.py:
        @st.cache_resource
        def get_ssp_engine(_df, position):
            return initialize_predictive_engine(_df, position)
    """
    from predictive_engine import ScoutScorePreditivo

    engine = ScoutScorePreditivo()
    try:
        engine.fit(
            df=df_all,
            position=position,
            result_col=None,  # Sem coluna de resultado por enquanto
            min_minutes=500,
        )
    except Exception as e:
        print(f"[WARN] Engine fit falhou para {position}: {e}")
        return None
    return engine


# ================================================================
# 3. TAB 6 — RANKING (substituir rank_players_weighted)
# ================================================================

def ranking_tab_v3(df_players, df_all, position, engine, min_minutes=500):
    """
    Substitui o bloco de ranking no Tab 6 do app.py.

    ANTES:
        df_ranked = rank_players_weighted(
            df_players, position, df_all,
            indices_config=INDICES_CONFIG, min_minutes=min_minutes
        )

    DEPOIS:
        df_ranked = ranking_tab_v3(df_players, df_all, position, engine, min_minutes)
    """
    if engine is not None:
        return engine.rank_players(df_players, df_all, min_minutes)
    else:
        # Fallback para sistema legado
        from similarity import rank_players_weighted
        return rank_players_weighted(df_players, position, df_all, min_minutes=min_minutes)


# ================================================================
# 4. TAB 7 — SIMILARIDADE (substituir compute_weighted_cosine_similarity)
# ================================================================

def similarity_tab_v3(target_player, comparison_pool, position,
                       top_n=20, min_minutes=500):
    """
    Substitui compute_weighted_cosine_similarity no Tab 7.

    ANTES:
        df_similar = compute_weighted_cosine_similarity(
            target_player, comparison_pool, position,
            top_n=20, min_minutes=500
        )

    DEPOIS:
        df_similar = similarity_tab_v3(
            target_player, comparison_pool, position
        )
    """
    from predictive_engine import compute_advanced_similarity
    return compute_advanced_similarity(
        target_player, comparison_pool, position,
        top_n=top_n, min_minutes=min_minutes
    )


# ================================================================
# 5. NOVO TAB — PREDIÇÃO DE CONTRATAÇÃO
# ================================================================

def contract_prediction_tab(player_row, df_all, position, engine,
                             age, league_origin, league_target, minutes):
    """
    Tab nova para predição de sucesso de contratação.
    Requer: age (float), liga de origem, liga alvo, minutos jogados.

    Retorna dict com probabilidade de sucesso e componentes.
    """
    from predictive_engine import ContractSuccessPredictor

    # Calcular SSP primeiro
    if engine is not None:
        ssp_result = engine.score_player(player_row, df_all)
        ssp = ssp_result.get('ssp', 50.0)
    else:
        from similarity import calculate_overall_score
        ssp = calculate_overall_score(player_row, position, df_all) or 50.0

    predictor = ContractSuccessPredictor()
    return predictor.predict_success_unsupervised(
        ssp_score=ssp,
        age=age,
        league_origin=league_origin,
        league_target=league_target,
        minutes=minutes,
    )


# ================================================================
# 6. NOVO TAB — ANÁLISE DE CLUSTERS
# ================================================================

def cluster_analysis_tab(df_players, position, min_minutes=500):
    """
    Tab nova: visualização dos clusters táticos da posição.
    Retorna: labels, profiles, feature_importance.
    """
    from predictive_engine import DataPreprocessor, TacticalClusterer

    preprocessor = DataPreprocessor()
    features = preprocessor.get_available_features(df_players, position)

    try:
        df_f, X, available = preprocessor.prepare_matrix(
            df_players, features, min_minutes
        )
    except Exception:
        return None

    if len(df_f) < 15:
        return None

    clusterer = TacticalClusterer()
    clusterer.fit(X, available)

    result = clusterer.predict(X)
    df_f['cluster'] = result['labels']
    df_f['cluster_probability'] = result['probabilities'].max(axis=1)

    return {
        'df': df_f,
        'n_clusters': clusterer.optimal_k,
        'profiles': clusterer.cluster_profiles,
        'features': available,
        'feature_importance': clusterer.get_feature_importance(),
    }


# ================================================================
# 7. EQUAÇÕES MATEMÁTICAS (DOCUMENTAÇÃO)
# ================================================================
"""
═══════════════════════════════════════════════════════════════
TOPOLOGIA DO ALGORITMO: Scout Score Preditivo (SSP)
═══════════════════════════════════════════════════════════════

1. SCORE GLOBAL:

    SSP = 0.30·WP + 0.25·E + 0.15·C + 0.30·P

    onde:
        WP = Σᵢ (percentil_i × β_i^{wp}) / Σᵢ β_i^{wp}
        E  = Φ(z_efficiency)  ×  100
        C  = max(P(cluster_k | x)) × 100
        P  = Σᵢ (percentil_i × w_i^{fs}) / Σᵢ w_i^{fs}


2. FEATURE SELECTION (relevância):

    relevance_i = 0.4·MI(x_i, y) + 0.3·|λ_i^{PC1}| + 0.3·domain_weight_i

    MI = Mutual Information (classif ou regression conforme target)
    λ_i^{PC1} = loading da feature i no 1º componente principal
    domain_weight = peso funcional da posição (ofensivo/defensivo/passe/físico)


3. WIN-PROBABILITY:

    P(win) = σ(β₀ + Σᵢ βᵢ·xᵢ)

    Coeficientes βᵢ com p-value < 0.05 → usados como pesos no WP component.
    Magnitude |βᵢ| proporcional ao impacto da ação na vitória.


4. EFICIÊNCIA xG (Atacantes):

    E_atk = 0.50·z(G-xG)/xG + 0.30·z(SOT%) + 0.20·z(Conv%)

    z(·) = z-score em relação à distribuição da posição
    Φ(·) = CDF da normal padrão (mapeia z-score → [0, 1])

   EFICIÊNCIA xG (Goleiros):

    E_gk = 0.60·z(xGA - GC) + 0.40·z(Defesas%)


5. CLUSTERIZAÇÃO:

    k* = argmax_k silhouette(KMeans(k), X_PCA)    para k ∈ [3, 8]
    P(cluster | x) via Gaussian Mixture Model
    Interpretabilidade via Random Forest feature importance


6. SIMILARIDADE AVANÇADA:

    S = 0.40·(1 - d_Mahal/d_max) + 0.35·RF_proximity + 0.25·I(cluster_match)

    d_Mahal = √((x-μ)ᵀ Σ⁻¹ (x-μ))
    RF_proximity = fração de folhas compartilhadas no Random Forest
    I(cluster_match) = indicadora de mesmo cluster


7. PREDIÇÃO DE CONTRATAÇÃO (modo unsupervised):

    P(sucesso) = σ(6·(z̄ - 0.5))

    z̄ = 0.40·(SSP/100) + 0.20·age_factor + 0.20·league_factor + 0.20·min_factor

    age_factor = max(0, 1 - (age-26)²/225)
    league_factor = min(tier_origin/tier_target, 1.5) / 1.5
    min_factor = min(minutes/3000, 1)


═══════════════════════════════════════════════════════════════
MATRIZ DE COEFICIENTES (Win-Probability — Exemplo Atacante)
═══════════════════════════════════════════════════════════════

Feature                     | β (coef)  | p-value   | Sig.
────────────────────────────┼───────────┼───────────┼──────
Golos/90                    |  +0.847   |  0.001    | ***
Golos esperados/90          |  +0.623   |  0.003    | **
Dribles com sucesso, %      |  +0.412   |  0.018    | *
Duelos ofensivos ganhos, %  |  +0.389   |  0.022    | *
Remates a baliza, %         |  +0.356   |  0.031    | *
Acoes defensivas/90         |  +0.198   |  0.142    |  ns
Passes certos, %            |  +0.087   |  0.523    |  ns

Nota: Coeficientes são hipotéticos e servem como template.
      Valores reais dependem do fit com dados da liga/posição.
      *** p<0.001, ** p<0.01, * p<0.05, ns = não significativo


═══════════════════════════════════════════════════════════════
PIPELINE ESTRUTURAL
═══════════════════════════════════════════════════════════════

    ┌─────────────────┐
    │  Dados Brutos   │  Google Sheets / Wyscout export
    │  (Wyscout/SKC)  │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ DataPreprocessor │  Limpeza + RobustScaler + Imputer
    └────────┬────────┘
             │
    ┌────────▼──────────────────┐
    │  PositionFeatureSelector  │  PCA + MI + Domain Weights
    │  (features relevantes)    │  → top-K features por posição
    └────────┬──────────────────┘
             │
    ┌────────▼─────┐   ┌──────────────┐   ┌───────────────┐
    │ WP Model     │   │ xG Residual  │   │ Clusterer     │
    │ (LogReg)     │   │ (z-scores)   │   │ (KMeans+GMM)  │
    │ β_i → pesos  │   │ Efficiency   │   │ cluster fit   │
    └──────┬───────┘   └──────┬───────┘   └───────┬───────┘
           │                  │                    │
    ┌──────▼──────────────────▼────────────────────▼──────┐
    │              ScoutScorePreditivo (SSP)               │
    │  SSP = 0.30·WP + 0.25·E + 0.15·C + 0.30·P         │
    └──────────────────────┬──────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │ ContractSuccessPredictor │
              │ P(sucesso) = σ(z_comp)  │
              └─────────────────────────┘
"""


# ================================================================
# 8. VALIDAÇÃO DO PIPELINE
# ================================================================

def validate_pipeline():
    """Teste rápido com dados sintéticos para validar o pipeline."""

    print("=" * 60)
    print("VALIDAÇÃO DO PIPELINE PREDITIVO")
    print("=" * 60)

    # Verificar dependências
    try:
        from predictive_engine import (
            DataPreprocessor, PositionFeatureSelector,
            WinProbabilityModel, xGResidualModel,
            TacticalClusterer, AdvancedSimilarity,
            ScoutScorePreditivo, ContractSuccessPredictor,
            POSITION_PROFILES, INVERTED_METRICS,
        )
        print("[OK] Imports do predictive_engine")
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False

    try:
        from sklearn.preprocessing import StandardScaler
        print("[OK] scikit-learn disponível")
    except ImportError:
        print("[WARN] scikit-learn não instalado — modo degradado")

    # Dados sintéticos
    np.random.seed(42)
    n = 100
    df_test = pd.DataFrame({
        'Golos/90': np.random.exponential(0.3, n),
        'Golos esperados/90': np.random.exponential(0.25, n),
        'Golos sem ser por penalti/90': np.random.exponential(0.2, n),
        'Remates/90': np.random.normal(2.5, 1.0, n),
        'Remates a baliza, %': np.random.uniform(20, 60, n),
        'Golos marcados, %': np.random.uniform(5, 25, n),
        'Toques na area/90': np.random.normal(3, 1.5, n),
        'Golos de cabeca/90': np.random.exponential(0.05, n),
        'Dribles/90': np.random.normal(2, 1, n),
        'Dribles com sucesso, %': np.random.uniform(30, 70, n),
        'Duelos ofensivos/90': np.random.normal(5, 2, n),
        'Duelos ofensivos ganhos, %': np.random.uniform(30, 60, n),
        'Aceleracoes/90': np.random.normal(3, 1, n),
        'Faltas sofridas/90': np.random.normal(1.5, 0.5, n),
        'Duelos aerios/90': np.random.normal(2, 1, n),
        'Duelos aereos ganhos, %': np.random.uniform(30, 70, n),
        'Corridas progressivas/90': np.random.normal(2, 0.8, n),
        'Recesao de passes em profundidade/90': np.random.normal(1, 0.5, n),
        'Passes recebidos/90': np.random.normal(20, 5, n),
        'Passes/90': np.random.normal(25, 8, n),
        'Passes certos, %': np.random.uniform(60, 90, n),
        'Assistencias/90': np.random.exponential(0.1, n),
        'Assistencias esperadas/90': np.random.exponential(0.08, n),
        'Segundas assistencias/90': np.random.exponential(0.05, n),
        'Passes chave/90': np.random.normal(0.8, 0.3, n),
        'Acoes defensivas com exito/90': np.random.normal(2, 1, n),
        'Passes longos recebidos/90': np.random.normal(1, 0.5, n),
        'Minutos jogados:': np.random.uniform(200, 3000, n),
        'JogadorDisplay': [f'Jogador_{i}' for i in range(n)],
    })

    position = 'Atacante'

    # Test 1: DataPreprocessor
    print("\n--- DataPreprocessor ---")
    pp = DataPreprocessor()
    features = pp.get_available_features(df_test, position)
    print(f"  Features encontradas: {len(features)}")
    df_f, X, avail = pp.prepare_matrix(df_test, features, min_minutes=500)
    print(f"  Jogadores filtrados: {len(df_f)}")
    print(f"  Shape X_scaled: {X.shape}")

    # Test 2: FeatureSelector
    print("\n--- PositionFeatureSelector ---")
    fs = PositionFeatureSelector()
    fs.fit(X, avail, position)
    top_features = fs.select(avail, top_k=10)
    print(f"  Top 10 features:")
    for feat, score in top_features[:5]:
        print(f"    {feat}: {score:.3f}")

    # Test 3: TacticalClusterer
    print("\n--- TacticalClusterer ---")
    tc = TacticalClusterer()
    tc.fit(X, avail)
    print(f"  K ótimo: {tc.optimal_k}")
    print(f"  Perfis: {list(tc.cluster_profiles.keys())}")

    # Test 4: AdvancedSimilarity
    print("\n--- AdvancedSimilarity ---")
    sim = AdvancedSimilarity()
    sim.fit(X)
    results = sim.compute_similarity(X[0], clusterer=tc, top_n=5)
    print(f"  Top 5 similares ao Jogador 0:")
    for r in results[:3]:
        print(f"    idx={r['pool_index']}, sim={r['similarity_pct']}%")

    # Test 5: ScoutScorePreditivo
    print("\n--- ScoutScorePreditivo ---")
    ssp = ScoutScorePreditivo()
    ssp.fit(df_test, position, min_minutes=500)
    player = df_f.iloc[0]
    score = ssp.score_player(player, df_test)
    print(f"  SSP: {score['ssp']}")
    print(f"  WP: {score['wp_component']}")
    print(f"  Efficiency: {score['efficiency_component']}")
    print(f"  Cluster: {score['cluster_component']}")
    print(f"  Percentile: {score['percentile_component']}")

    # Test 6: ContractSuccessPredictor
    print("\n--- ContractSuccessPredictor ---")
    csp = ContractSuccessPredictor()
    pred = csp.predict_success_unsupervised(
        ssp_score=score['ssp'],
        age=24,
        league_origin='Serie B Brasil',
        league_target='Serie A Brasil',
        minutes=2000,
    )
    print(f"  P(sucesso): {pred['success_probability']}")
    print(f"  Risco: {pred['risk_level']}")

    # Test 7: Ranking batch
    print("\n--- Ranking Batch ---")
    ranked = ssp.rank_players(df_test, df_test, min_minutes=500)
    print(f"  Jogadores rankeados: {len(ranked)}")
    if len(ranked) > 0:
        print(f"  Top SSP: {ranked['SSP'].iloc[0]}")
        print(f"  Bottom SSP: {ranked['SSP'].iloc[-1]}")

    print("\n" + "=" * 60)
    print("PIPELINE VALIDADO COM SUCESSO")
    print("=" * 60)
    return True


if __name__ == '__main__':
    validate_pipeline()
