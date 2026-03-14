"""
league_power_model.py — League Strength Adjustment via Opta Power Ranking
=========================================================================

Base científica:
- Opta Power Ranking (The Analyst): sistema global de rating de clubes baseado
  em resultados competitivos (modelo Elo), classificando milhares de clubes.
- UEFA coefficient logic para hierarquização de ligas.

Coeficientes normalizados a partir da média do rating Opta dos clubes por liga.
Integra-se ao pipeline preditivo como fator multiplicativo para comparação
estatisticamente consistente entre ligas.

Referências:
- Perspectives on Data Analytics for Gaining a Competitive Advantage in Football
  (Liverpool John Moores University + KU Leuven, Science & Medicine in Football, 2025)
- Frost & Groom (2025): The Use of Performance Analysis and Data-Driven Approaches
  within Senior Men's Football Recruitment
"""

from typing import Dict, Optional


# ================================================================
# OPTA POWER RANKING COEFFICIENTS (normalizados, Premier League = 1.00)
# ================================================================
# Baseados na média do rating Opta dos clubes por liga.
# Atualizados com base em rankings competitivos 2024/2025.

OPTA_LEAGUE_POWER = {
    # === TOP 5 EUROPEIAS (1ª divisão) ===
    'Premier League': 1.00,
    'La Liga': 0.96,
    'Bundesliga': 0.94,
    'Serie A Italia': 0.93,
    'Ligue 1': 0.91,

    # === TOP 5 EUROPEIAS (2ª divisão) ===
    'Championship': 0.87,
    'La Liga 2': 0.80,
    'Serie B Italia': 0.78,
    '2. Bundesliga': 0.77,
    'Ligue 2': 0.74,
    'La Liga 3': 0.65,
    'Serie C Italia': 0.58,

    # === EUROPA — TIER 2 (1ª divisão) ===
    'Liga Portugal': 0.86,
    'Eredivisie': 0.85,
    'Belgian Pro League': 0.83,
    'Scottish Premiership': 0.82,
    'Super Lig': 0.80,
    'Austrian Bundesliga': 0.79,
    'Swiss Super League': 0.79,
    'Danish Superliga': 0.78,
    'Serbian Super Liga': 0.78,
    'Swedish Allsvenskan': 0.76,
    'Czech First League': 0.75,
    'Hungarian NB I': 0.75,
    'Greek Super League': 0.74,
    'Croatian First League': 0.74,
    'Russian Premier League': 0.73,
    'Polish Ekstraklasa': 0.73,
    'Norwegian Eliteserien': 0.72,
    'Israeli Premier League': 0.72,
    'Cypriot First Division': 0.71,
    'Romanian Liga I': 0.70,
    'Ukrainian Premier League': 0.69,
    'Bulgarian First League': 0.67,
    'Slovenian PrvaLiga': 0.65,

    # === EUROPA — TIER 2 (2ª divisão / inferior) ===
    'Liga Portugal 2': 0.68,
    'Liga Portugal 3': 0.55,
    'Campeonato de Portugal': 0.42,
    'Super Lig 2': 0.65,
    'Swiss Challenge League': 0.64,
    'Belgian Second Division': 0.63,
    'Austrian 2. Liga': 0.63,
    'Romanian Liga II': 0.58,
    'Bosnian Premier League': 0.62,
    'Slovak Super Liga': 0.62,
    'Croatian HNL': 0.74,
    'Albanian Superiore': 0.55,
    'Moldovan National Division': 0.52,
    'Azerbaijan Premier League': 0.55,
    'Armenian Premier League': 0.52,
    'Montenegrin First League': 0.45,
    'Maltese Premier League': 0.45,

    # === AMÉRICAS ===
    'Serie A Brasil': 0.89,
    'Serie B Brasil': 0.75,
    'Serie C Brasil': 0.63,
    'Serie D Brasil': 0.52,
    'Liga Argentina': 0.81,
    'Liga Argentina B': 0.67,
    'MLS': 0.82,
    'Liga MX': 0.80,
    'Liga Colombia': 0.74,
    'Liga Colombia B': 0.58,
    'Liga Chile': 0.72,
    'Liga Chile B': 0.59,
    'Liga Uruguai': 0.70,
    'Liga Uruguai B': 0.50,
    'Liga Peru': 0.62,
    'Liga Equador': 0.72,
    'Liga Paraguai': 0.68,
    'Liga Paraguai B': 0.54,
    'Liga Bolivia': 0.60,
    'Liga Venezuela': 0.58,

    # === ÁSIA / ORIENTE MÉDIO ===
    'J1 League': 0.76,
    'J2 League': 0.65,
    'K-League 1': 0.74,
    'K-League 2': 0.60,
    'Saudi Pro League': 0.78,
    'Saudi First Division': 0.58,
    'Qatar Stars League': 0.65,
    'UAE Pro League': 0.65,
    'UAE First Division': 0.52,
    'Chinese Super League': 0.68,
    'Indian Super League': 0.52,
    'Thai League': 0.55,
    'Malaysian Super League': 0.50,
    'Indonesian Liga 1': 0.50,
    'Uzbek Super League': 0.55,

    # === ÁFRICA ===
    'Egyptian Premier League': 0.70,
    'South African Premier': 0.60,
    'Moroccan Botola': 0.65,
    'Tunisian Ligue 1': 0.65,

    # === OCEANIA ===
    'A-League': 0.70,

    # === ESTADUAIS BRASIL ===
    'Paulista A1': 0.55,
    'Paulista A2': 0.48,
    'Paulista A3': 0.35,
    'Carioca A1': 0.55,
    'Gaucho A1': 0.50,
    'Mineiro A1': 0.50,
    'Paranaense A1': 0.50,
    'Catarinense A1': 0.48,
    'Cearense A1': 0.42,
    'Pernambucano A1': 0.42,
    'Baiano A1': 0.42,

    # === COPAS ===
    'Copa do Brasil': 0.85,
    'Copa do Nordeste': 0.50,
    'Copa Libertadores': 0.92,
    'Copa Sudamericana': 0.78,
}

# Default para ligas não mapeadas
DEFAULT_OPTA_POWER = 0.60


def get_opta_league_power(league: str) -> float:
    """Retorna o coeficiente Opta Power para uma liga.

    Args:
        league: Nome da liga (deve corresponder aos nomes em OPTA_LEAGUE_POWER
                ou nos LEAGUE_TIERS do ContractSuccessPredictor).

    Returns:
        Coeficiente normalizado [0, 1] onde Premier League = 1.00.
    """
    if not league:
        return DEFAULT_OPTA_POWER
    return OPTA_LEAGUE_POWER.get(league, DEFAULT_OPTA_POWER)


def get_league_strength_factor(league: str) -> float:
    """Retorna fator de força da liga para ajuste de métricas.

    Combina Opta Power com um fator de escala para que ligas menores
    não sejam excessivamente penalizadas (floor em 0.50).

    adjusted_metric = metric × league_strength_factor
    """
    opta = get_opta_league_power(league)
    # Floor de 0.50 para não penalizar demais ligas menores
    return max(0.50, opta)


def get_combined_league_adjustment(league: str,
                                    league_tiers: Optional[Dict[str, float]] = None) -> float:
    """Retorna ajuste combinado: league_strength_factor × opta_league_power.

    Conforme especificação:
    adjusted_metric = metric × league_strength_factor × opta_league_power

    Args:
        league: Nome da liga.
        league_tiers: Dicionário de tiers do ContractSuccessPredictor (0-10 scale).

    Returns:
        Fator combinado para ajuste de métricas.
    """
    opta_power = get_opta_league_power(league)

    if league_tiers and league in league_tiers:
        # Normalizar tier (0-10) para (0-1) e usar como league_strength_factor
        tier_normalized = league_tiers[league] / 10.0
        return tier_normalized * opta_power

    # Se não tiver tier, usar apenas opta_power ao quadrado (ambos fatores)
    return opta_power * opta_power


def adjust_metric(metric_value: float, league: str,
                  league_tiers: Optional[Dict[str, float]] = None) -> float:
    """Ajusta uma métrica pelo fator combinado de liga.

    adjusted_metric = metric × league_strength_factor × opta_league_power
    """
    factor = get_combined_league_adjustment(league, league_tiers)
    return metric_value * factor


def get_all_league_powers() -> Dict[str, float]:
    """Retorna todos os coeficientes Opta Power disponíveis."""
    return dict(OPTA_LEAGUE_POWER)
