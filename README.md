# Scouting Dashboard | Botafogo-SP

Dashboard de scouting profissional com motor preditivo de ML e visualizações estilo Wyscout.

---

## Arquitetura

```
Google Sheets
     ↓
PostgreSQL
     ↓
FastAPI Backend
     ├── predictive_engine.py    (Scout Score Preditivo, clustering, similaridade)
     ├── scouting_intelligence.py (6 modelos de ML — Scouting Intelligence Engine)
     ├── league_power_model.py   (Opta Power Ranking, ajuste por liga)
     ├── calibration.py          (coeficientes calibrados por literatura acadêmica)
     └── similarity.py           (índices compostos, percentis, ranking)
     ↓
API REST (JSON)
     ↓
React Frontend (Dashboard)
```

---

## Motor Analítico — Scouting Intelligence Engine

### Modelo 1: Player Trajectory Model
Previsão de evolução de carreira usando **Gradient Boosting Regressor**.

- **Pipeline:** normalização z-score → feature selection (mutual information) → gradient boosting → cross-validation
- **Saída:** `predicted_rating_next_season`, `trajectory_score`
- **Endpoint:** `POST /api/trajectory`

### Modelo 2: Market Value Prediction
Estimativa de valor de mercado com **XGBoost Regressor**.

- **Segmentação:** posição × faixa etária (Khalife et al., 2025)
- **Saída:** `estimated_market_value`, `market_value_gap`
- **Endpoint:** `POST /api/market_value`

### Modelo 3: Market Opportunity Detector
Score composto para identificação de oportunidades de mercado.

- **Fórmula:** `performance × trajectory × value_gap − age_penalty`
- **Inspiração:** Brighton, Brentford, FC Midtjylland
- **Saída:** `market_opportunity_score` (0-100)
- **Endpoint:** `POST /api/market_opportunities`

### Modelo 4: Player Replacement Engine
Motor de busca de substitutos com similaridade multi-método.

- **Métodos:** Cosine Similarity (45%) + Mahalanobis Distance (35%) + Cluster Proximity (20%)
- **Saída:** Top-N substitutos com scores de similaridade, trajetória e valor
- **Endpoint:** `POST /api/replacements`

### Modelo 5: Temporal Performance Trend
Análise temporal de tendência de performance.

- **Cálculo:** `trend = rolling_mean(current) − rolling_mean(previous)`
- **Classificação:** `improving`, `stable`, `declining`

### Modelo 6: League Strength Adjustment
Ajuste de métricas por nível de liga via Opta Power Ranking.

- **Fórmula:** `adjusted_metric = metric × league_strength_factor × opta_league_power`
- **Endpoint:** `GET /api/league_powers`

---

## Motor Preditivo Original (predictive_engine v3.0)

- **Scout Score Preditivo (SSP):** ensemble de WP-weights + xG-residual + cluster-fit + percentil
- **Win-Probability Model:** Logistic Regression com coeficientes calibrados
- **Clusterização Tática:** K-Means + Gaussian Mixture + RF interpreter
- **Similaridade Avançada:** Mahalanobis + Random Forest proximity
- **Predição de Contratação:** `ContractSuccessPredictor` com ajuste por liga

---

## Referências Científicas

### Modelos de Similaridade e Substituição
- Bhatt, Pandya, Raje, Shah (2025). *KickClone: A Machine Learning Model Built to Revolutionize Football Scouting.* AIMV 2025.
- *FPSRec: Football Players Scouting Recommendation System.* IEEE BigData 2024.
- *Spatial Similarity Index for Scouting in Football.* PMC/NCBI 2025.

### Revisões Sistemáticas
- *Artificial Intelligence in Football Scouting: Systematic Literature Review and Application with Unsupervised Machine Learning.* 2025.
- *Machine Learning Applied to Professional Football.* MDPI 2025 (172 artigos, 2019-2024).

### Valuation de Jogadores
- Khalife et al. (2025). *Dynamic Financial Valuation of Football Players: A Machine Learning Approach.* MDPI.

### Frameworks de Scouting com ML
- *A Machine Learning Framework to Scout Football Players.* National College of Ireland.
- *An xG-Based Football Scouting System Using Machine Learning Techniques.* 2024.

### Análise de Performance e Recrutamento
- Frost & Groom (2025). *The Use of Performance Analysis and Data-Driven Approaches within Senior Men's Football Recruitment.*
- Liverpool JMU + KU Leuven (2025). *Perspectives on Data Analytics for Gaining a Competitive Advantage in Football.* Science & Medicine in Football.

### Calibração do Motor Original
- PIBITI João Vitor Oliveira (Insper, 2025): Coeficientes β de rating por posição.
- Victor Valvano Schimidt (UNESP, 2021): Coeficientes de win-probability.
- Eduardo Baptista dos Santos (MBA USP/ICMC, 2024): Classificação de jogadores por posição.
- Frederico Ferra (NOVA IMS, 2025): PCA + K-Means + RF para clustering tático.
- Tiago Pinto (ISEP Porto, 2024): Gradient Boosting para predição de performance.
- Felipe Nunes (UFMG, 2025): Fuzzy + Random Forest para recrutamento.
- Gabriel Buso (UFSC, 2025): Modelos xG e xGOT.
- Gyarmati & Stanojevic (2016): Análise temporal de jogadores.

---

## Endpoints API

### Scouting Intelligence (novos)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/trajectory` | Previsão de evolução de carreira |
| POST | `/api/market_value` | Estimativa de valor de mercado |
| POST | `/api/market_opportunities` | Detecção de oportunidades |
| POST | `/api/replacements` | Busca de substitutos |
| GET | `/api/league_powers` | Coeficientes Opta Power por liga |

### Core (existentes)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/players` | Lista de jogadores |
| GET | `/api/players/{name}/profile` | Perfil completo |
| POST | `/api/rankings` | Ranking por posição |
| POST | `/api/similarity` | Jogadores similares |
| POST | `/api/prediction` | Predição de sucesso de contratação |
| POST | `/api/clusters` | Clusterização tática |
| POST | `/api/comparison` | Comparação entre jogadores |

---

## Rodar Localmente

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

---

## Funcionalidades

- **Perfil Individual:** Radar de atributos + percentis estilo Wyscout
- **Comparativo:** Scatter plot + comparação entre jogadores
- **Dados Físicos:** Métricas SkillCorner com radar de rankings
- **Rankings Preditivos:** Scout Score Preditivo com calibração acadêmica
- **Previsão de Evolução:** Trajetória de carreira com Gradient Boosting
- **Valuation:** Estimativa de valor de mercado com XGBoost
- **Oportunidades:** Detecção de talentos subvalorizados
- **Substituição:** Motor de busca de substitutos multi-método
- **Análise Temporal:** Tendências de performance

---

**Desenvolvido para Botafogo SA Ribeirão Preto**
