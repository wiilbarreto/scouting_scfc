# Implementação do Motor Preditivo — Passo a Passo

## Arquivos entregues

| Arquivo | Função | Destino |
|---|---|---|
| `predictive_engine.py` | Motor preditivo (substitui similarity.py) | Raiz do repo |
| `calibration.py` | Coeficientes reais dos 7 trabalhos acadêmicos | Raiz do repo |
| `integration_guide.py` | Funções de integração + validação | Raiz do repo |
| `requirements.txt` | Dependências atualizadas (sklearn, scipy, etc.) | Raiz do repo |

---

## Passo 1 — Adicionar os arquivos ao repositório

Copie os 4 arquivos para a raiz do `scouting_bfsa/`, ao lado do `app.py` e `similarity.py`:

```
scouting_bfsa/
├── app.py                  # existente
├── similarity.py           # existente (mantido como fallback)
├── similarity_v2.py        # existente
├── predictive_engine.py    # ← NOVO
├── calibration.py          # ← NOVO
├── integration_guide.py    # ← NOVO
├── requirements.txt        # ← ATUALIZADO
├── data_loader.py
├── fuzzy_match.py
└── config.toml
```

---

## Passo 2 — Instalar dependências

```bash
pip install -r requirements.txt
```

Novas dependências: `scikit-learn`, `scipy`, `statsmodels`, `xgboost`.

---

## Passo 3 — Validar a instalação

```bash
python integration_guide.py
```

Deve imprimir `PIPELINE VALIDADO COM SUCESSO` ao final.

---

## Passo 4 — Alterar os imports no `app.py`

No topo do `app.py`, **depois** dos imports existentes, adicione:

```python
# Motor preditivo (usa calibration.py automaticamente)
try:
    from predictive_engine import (
        ScoutScorePreditivo,
        ContractSuccessPredictor,
        compute_advanced_similarity,
        calculate_overall_score_v3,
        AdvancedSimilarity,
        TacticalClusterer,
        DataPreprocessor,
        POSITION_PROFILES,
    )
    HAS_PREDICTIVE = True
except ImportError:
    HAS_PREDICTIVE = False
```

**Mantenha** os imports antigos do `similarity.py` — eles servem de fallback.

---

## Passo 5 — Cachear o engine por posição (performance)

Adicione esta função após a seção de config do `app.py`:

```python
@st.cache_resource
def get_ssp_engine(_df_hash, df, position):
    """Treina o motor preditivo uma vez por posição."""
    if not HAS_PREDICTIVE:
        return None
    try:
        engine = ScoutScorePreditivo()
        engine.fit(df=df, position=position, min_minutes=500)
        return engine
    except Exception as e:
        st.warning(f"Motor preditivo indisponível para {position}: {e}")
        return None
```

Chame no ponto onde a posição é selecionada:

```python
# Após o selectbox de posição
if HAS_PREDICTIVE:
    engine = get_ssp_engine(
        hash(tuple(df_all.columns)),
        df_all, selected_position
    )
else:
    engine = None
```

---

## Passo 6 — Substituir o ranking (Tab 6)

Localize o bloco que chama `rank_players_weighted()` e substitua:

```python
# ANTES:
# df_ranked = rank_players_weighted(df_players, position, df_all, ...)

# DEPOIS:
if engine is not None:
    df_ranked = engine.rank_players(df_players, df_all, min_minutes=min_minutes)
    # Colunas novas: SSP, WP, Efficiency, Cluster, Percentile
else:
    df_ranked = rank_players_weighted(df_players, position, df_all, min_minutes=min_minutes)
```

---

## Passo 7 — Substituir a similaridade (Tab 7)

Localize o bloco que chama `compute_weighted_cosine_similarity()` e substitua:

```python
# ANTES:
# df_similar = compute_weighted_cosine_similarity(target, pool, position, ...)

# DEPOIS:
if HAS_PREDICTIVE:
    df_similar = compute_advanced_similarity(
        target_player, comparison_pool, position,
        top_n=20, min_minutes=500,
    )
    # Colunas novas: mahalanobis_sim, rf_proximity
else:
    df_similar = compute_weighted_cosine_similarity(
        target_player, comparison_pool, position,
        top_n=20, min_minutes=500,
    )
```

---

## Passo 8 — (Opcional) Adicionar tab de Predição de Contratação

```python
with tab_predicao:
    st.subheader("Predição de Sucesso de Contratação")

    if engine is not None and selected_player is not None:
        player_row = df_all[df_all['JogadorDisplay'] == selected_player].iloc[0]

        col1, col2, col3 = st.columns(3)
        age = col1.number_input("Idade", 16, 42, 24)
        league_origin = col2.selectbox("Liga Origem", [
            'Serie A Brasil', 'Serie B Brasil', 'Serie C Brasil',
            'Paulista A1', 'Paulista A2',
        ])
        league_target = col3.selectbox("Liga Alvo", [
            'Serie A Brasil', 'Serie B Brasil',
            'Premier League', 'La Liga', 'Bundesliga',
            'Serie A Italia', 'Ligue 1', 'Liga Portugal',
        ])

        # Calcular SSP
        ssp_result = engine.score_player(player_row, df_all)
        ssp = ssp_result.get('ssp', 50.0)
        minutes = float(player_row.get('Minutos jogados:', 0))

        # Predição
        predictor = ContractSuccessPredictor()
        pred = predictor.predict_success_unsupervised(
            ssp_score=ssp, age=age,
            league_origin=league_origin,
            league_target=league_target,
            minutes=minutes,
        )

        # Exibir
        st.metric("SSP (Score Preditivo)", f"{ssp:.1f}/100")
        st.metric("P(Sucesso)", f"{pred['success_probability']:.1%}")
        st.metric("Nível de Risco", pred['risk_level'].upper())

        st.json({
            'ssp_contribution': pred['ssp_contribution'],
            'age_factor': pred['age_factor'],
            'league_factor': pred['league_factor'],
            'minutes_factor': pred['minutes_factor'],
        })
```

---

## Passo 9 — (Opcional) Adicionar tab de Clusters Táticos

```python
with tab_clusters:
    st.subheader("Perfis Táticos")

    if HAS_PREDICTIVE:
        from predictive_engine import DataPreprocessor, TacticalClusterer

        pp = DataPreprocessor()
        features = pp.get_available_features(df_position, selected_position)

        try:
            df_f, X, available = pp.prepare_matrix(df_position, features, min_minutes=500)
            if len(df_f) >= 15:
                tc = TacticalClusterer()
                tc.fit(X, available)

                result = tc.predict(X)
                df_f['Cluster'] = result['labels']
                df_f['Prob_Cluster'] = result['probabilities'].max(axis=1)

                st.write(f"**{tc.optimal_k} perfis** identificados ({len(df_f)} jogadores)")

                for k, profile in tc.cluster_profiles.items():
                    with st.expander(f"Cluster {k} ({profile['size']} jogadores)"):
                        top_feats = sorted(
                            profile['centroid'].items(),
                            key=lambda x: -abs(x[1])
                        )[:5]
                        for feat, val in top_feats:
                            st.write(f"  {feat}: {val:.2f}")
        except Exception as e:
            st.warning(f"Clustering indisponível: {e}")
```

---

## Passo 10 — Commit e deploy

```bash
git add predictive_engine.py calibration.py integration_guide.py requirements.txt
git commit -m "feat: motor preditivo v3 com calibração acadêmica (7 trabalhos)"
git push origin main
```

---

## Equação do SSP (referência rápida)

```
SSP = 0.25·WP + 0.25·E + 0.15·C + 0.35·P

WP  = Percentil ponderado por coeficientes de win-probability (Schimidt, 2021)
E   = Φ(z_efficiency) × 100  — resíduo xG/xGOT (Buso, 2025)
C   = max(P(cluster_k | x)) × 100  — aderência tática (Ferra + Nunes)
P   = Percentil ponderado por coeficientes de rating (PIBITI, 2025)
```

## Fontes dos coeficientes

| Componente | Fonte | Método | Confiança |
|---|---|---|---|
| WP (λ=0.25) | Schimidt (UNESP, 2021) | Logistic Regression, 10 ligas | Moderada |
| Efficiency (λ=0.25) | Buso (UFSC, 2025) + Nunes (UFMG, 2025) | LogReg xG/xGOT (AUC=0.83) + RF (R²=0.93) | Alta |
| Cluster (λ=0.15) | Ferra (NOVA, 2025) + Nunes (UFMG, 2025) | KMeans+GMM+RF (93.3% acc) + Fuzzy C-Means | Alta |
| Percentile (λ=0.35) | PIBITI João Vitor (Insper, 2025) + Baptista (USP, 2024) | OLS (R²=0.99) + RF/XGBoost (F1=83%) | Muito alta |
