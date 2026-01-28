import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from math import pi, cos, sin

# ============================================
# CONFIGURAÇÃO
# ============================================
st.set_page_config(
    page_title="Scouting Dashboard | Botafogo-SP",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# TEMA DARK PROFISSIONAL
# ============================================
COLORS = {
    'bg_primary': '#0a0a0f',
    'bg_secondary': '#12121a',
    'bg_card': '#1a1a24',
    'accent': '#dc2626',
    'accent_light': '#ef4444',
    'text_primary': '#ffffff',
    'text_secondary': '#9ca3af',
    'text_muted': '#6b7280',
    'border': 'rgba(255,255,255,0.08)',
    'elite': '#22c55e',
    'above_avg': '#eab308',
    'average': '#f97316',
    'below_avg': '#ef4444',
}

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .main {{
        background: linear-gradient(180deg, {COLORS['bg_primary']} 0%, {COLORS['bg_secondary']} 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0d0d12 0%, #161620 100%);
        border-right: 1px solid {COLORS['border']};
    }}
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: {COLORS['text_secondary']};
    }}
    
    /* Headers */
    h1 {{ font-size: 28px !important; font-weight: 700 !important; color: {COLORS['text_primary']} !important; letter-spacing: -0.5px; }}
    h2 {{ font-size: 20px !important; font-weight: 600 !important; color: {COLORS['text_primary']} !important; }}
    h3 {{ font-size: 16px !important; font-weight: 600 !important; color: {COLORS['text_secondary']} !important; }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        background: {COLORS['bg_card']};
        border-radius: 12px;
        padding: 4px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border: none;
        color: {COLORS['text_muted']};
        font-weight: 500;
        font-size: 14px;
        padding: 10px 20px;
        border-radius: 8px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {COLORS['accent']} !important;
        color: white !important;
    }}
    
    /* Metrics */
    [data-testid="stMetric"] {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 20px;
    }}
    
    [data-testid="stMetric"] label {{
        color: {COLORS['text_muted']} !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {COLORS['text_primary']} !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }}
    
    /* Selectbox */
    .stSelectbox > div > div {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        color: {COLORS['text_primary']};
    }}
    
    /* Cards */
    .player-header {{
        background: linear-gradient(135deg, {COLORS['bg_card']} 0%, rgba(26,26,36,0.8) 100%);
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 24px;
    }}
    
    .player-name {{
        font-size: 36px;
        font-weight: 800;
        color: {COLORS['text_primary']};
        letter-spacing: -1px;
        margin-bottom: 4px;
    }}
    
    .player-position {{
        font-size: 14px;
        font-weight: 600;
        color: {COLORS['accent']};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .info-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin-top: 20px;
    }}
    
    .info-item {{
        display: flex;
        flex-direction: column;
        gap: 2px;
    }}
    
    .info-label {{
        font-size: 11px;
        color: {COLORS['text_muted']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .info-value {{
        font-size: 14px;
        color: {COLORS['text_primary']};
        font-weight: 500;
    }}
    
    .rating-box {{
        background: linear-gradient(135deg, {COLORS['accent']} 0%, #b91c1c 100%);
        border-radius: 12px;
        padding: 16px 24px;
        text-align: center;
        margin-top: 20px;
    }}
    
    .rating-label {{
        font-size: 11px;
        color: rgba(255,255,255,0.7);
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .rating-value {{
        font-size: 36px;
        font-weight: 800;
        color: white;
    }}
    
    /* Chart container */
    .chart-container {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }}
    
    .chart-title {{
        font-size: 14px;
        font-weight: 600;
        color: {COLORS['text_primary']};
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    .chart-title::before {{
        content: '';
        width: 3px;
        height: 16px;
        background: {COLORS['accent']};
        border-radius: 2px;
    }}
    
    /* Analysis box */
    .analysis-container {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-left: 4px solid {COLORS['accent']};
        border-radius: 0 12px 12px 0;
        padding: 24px;
    }}
    
    .analysis-text {{
        color: {COLORS['text_secondary']};
        font-size: 14px;
        line-height: 1.8;
    }}
    
    /* Legend */
    .legend-row {{
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 16px;
        flex-wrap: wrap;
    }}
    
    .legend-item {{
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
        color: {COLORS['text_muted']};
    }}
    
    .legend-dot {{
        width: 10px;
        height: 10px;
        border-radius: 2px;
    }}
    
    /* Link */
    a {{ color: {COLORS['accent']} !important; text-decoration: none !important; }}
    a:hover {{ color: {COLORS['accent_light']} !important; }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Divider */
    hr {{
        border: none;
        border-top: 1px solid {COLORS['border']};
        margin: 24px 0;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# DATA LOADING
# ============================================
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file:
        xlsx = pd.ExcelFile(uploaded_file)
    else:
        xlsx = pd.ExcelFile('Banco_de_Dados___Jogadores-2.xlsx')
    
    analises = pd.read_excel(xlsx, sheet_name='Análises')
    central = pd.read_excel(xlsx, sheet_name='Central de Dados')
    oferecidos = pd.read_excel(xlsx, sheet_name='Oferecidos')
    return analises, central, oferecidos

# ============================================
# CHART FUNCTIONS - ESTILO WYSCOUT
# ============================================

def get_percentile_color(value):
    """Retorna cor baseada no percentil"""
    if value >= 90:
        return COLORS['elite']
    elif value >= 65:
        return COLORS['above_avg']
    elif value >= 36:
        return COLORS['average']
    else:
        return COLORS['below_avg']


def create_wyscout_radar(metrics_dict, title="", min_val=0, max_val=100, show_values=True):
    """
    Radar chart estilo Wyscout com setores preenchidos
    """
    categories = list(metrics_dict.keys())
    values = list(metrics_dict.values())
    n = len(categories)
    
    # Ângulos para cada categoria
    angles = [i * (360 / n) for i in range(n)]
    
    fig = go.Figure()
    
    # Círculos de referência
    for r in [25, 50, 75, 100]:
        theta_circle = list(range(0, 361, 5))
        fig.add_trace(go.Scatterpolar(
            r=[r * (max_val/100)] * len(theta_circle),
            theta=theta_circle,
            mode='lines',
            line=dict(color='rgba(255,255,255,0.1)', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Barras radiais para cada métrica
    for i, (cat, val) in enumerate(zip(categories, values)):
        color = get_percentile_color(val)
        angle_start = angles[i] - (360 / n / 2) + 90
        angle_end = angles[i] + (360 / n / 2) + 90
        
        # Criar setor usando Scatterpolar
        theta_sector = np.linspace(angle_start, angle_end, 20)
        r_sector = [0] + [val * (max_val/100)] * len(theta_sector) + [0]
        theta_sector = [angle_start] + list(theta_sector) + [angle_end]
        
        fig.add_trace(go.Scatterpolar(
            r=r_sector,
            theta=theta_sector,
            fill='toself',
            fillcolor=color,
            line=dict(color=color, width=1),
            opacity=0.85,
            showlegend=False,
            hovertemplate=f'<b>{cat}</b><br>Percentil: {val:.0f}<extra></extra>'
        ))
    
    # Labels das categorias
    for i, (cat, val) in enumerate(zip(categories, values)):
        angle_rad = (angles[i] + 90) * pi / 180
        r_label = max_val * 1.15
        
        fig.add_trace(go.Scatterpolar(
            r=[r_label],
            theta=[angles[i] + 90],
            mode='text',
            text=[cat],
            textfont=dict(size=11, color=COLORS['text_secondary'], family='Inter'),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Valores dentro dos setores
        if show_values and val > 15:
            fig.add_trace(go.Scatterpolar(
                r=[val * (max_val/100) * 0.7],
                theta=[angles[i] + 90],
                mode='text',
                text=[f'{val:.0f}'],
                textfont=dict(size=10, color='white', family='Inter', weight=600),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[0, max_val * 1.2]
            ),
            angularaxis=dict(
                visible=False,
                direction='clockwise',
                rotation=90
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=80, r=80, t=40, b=40),
        height=380,
        showlegend=False
    )
    
    return fig


def create_attribute_radar(player_data, max_val=5):
    """Radar de atributos (escala 1-5)"""
    
    categories = ['Técnica', 'Físico', 'Tática', 'Mental']
    values = [player_data.get(cat, 0) or 0 for cat in categories]
    
    # Converter para percentil visual
    percentile_values = [(v / max_val) * 100 for v in values]
    
    metrics_dict = dict(zip(categories, percentile_values))
    return create_wyscout_radar(metrics_dict, max_val=100)


def create_comparison_radar(p1_data, p2_data, p1_name, p2_name):
    """Radar de comparação entre dois jogadores"""
    
    categories = ['Técnica', 'Físico', 'Tática', 'Mental']
    
    vals1 = [p1_data.get(cat, 0) or 0 for cat in categories]
    vals2 = [p2_data.get(cat, 0) or 0 for cat in categories]
    
    vals1 += vals1[:1]
    vals2 += vals2[:1]
    theta = categories + [categories[0]]
    
    fig = go.Figure()
    
    # Player 1
    fig.add_trace(go.Scatterpolar(
        r=vals1,
        theta=theta,
        fill='toself',
        fillcolor='rgba(220, 38, 38, 0.3)',
        line=dict(color=COLORS['accent'], width=3),
        name=p1_name
    ))
    
    # Player 2
    fig.add_trace(go.Scatterpolar(
        r=vals2,
        theta=theta,
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.3)',
        line=dict(color='#3b82f6', width=3),
        name=p2_name
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                tickfont=dict(size=10, color=COLORS['text_muted']),
                gridcolor='rgba(255,255,255,0.1)',
                linecolor='rgba(255,255,255,0.1)'
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.15)',
                linecolor='rgba(255,255,255,0.1)',
                tickfont=dict(size=12, color=COLORS['text_secondary'], family='Inter')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='center',
            x=0.5,
            font=dict(color='white', size=12, family='Inter')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=80, r=80, t=60, b=40),
        height=420
    )
    
    return fig


def create_scatter_plot(df, x_col, y_col, highlight=None, title=""):
    """Scatter plot com quadrantes"""
    
    x_mean = df[x_col].mean()
    y_mean = df[y_col].mean()
    
    fig = go.Figure()
    
    # Quadrantes
    x_max = df[x_col].max() * 1.15
    y_max = df[y_col].max() * 1.15
    x_min = df[x_col].min() * 0.85
    y_min = df[y_col].min() * 0.85
    
    # Top-right (Completo)
    fig.add_shape(type="rect", x0=x_mean, y0=y_mean, x1=x_max, y1=y_max,
                  fillcolor="rgba(34, 197, 94, 0.1)", line=dict(width=0))
    # Bottom-left (Limitado)
    fig.add_shape(type="rect", x0=x_min, y0=y_min, x1=x_mean, y1=y_mean,
                  fillcolor="rgba(239, 68, 68, 0.1)", line=dict(width=0))
    
    # Linhas de média
    fig.add_hline(y=y_mean, line_dash="dot", line_color="rgba(255,255,255,0.2)")
    fig.add_vline(x=x_mean, line_dash="dot", line_color="rgba(255,255,255,0.2)")
    
    # Pontos
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='markers',
        marker=dict(
            size=12,
            color=COLORS['text_muted'],
            opacity=0.5,
            line=dict(width=1, color='rgba(255,255,255,0.3)')
        ),
        text=df['Nome'],
        hovertemplate='<b>%{text}</b><br>%{x:.1f} | %{y:.1f}<extra></extra>',
        showlegend=False
    ))
    
    # Destacar jogador
    if highlight and highlight in df['Nome'].values:
        p = df[df['Nome'] == highlight].iloc[0]
        fig.add_trace(go.Scatter(
            x=[p[x_col]],
            y=[p[y_col]],
            mode='markers+text',
            marker=dict(size=18, color=COLORS['accent'], line=dict(width=2, color='white')),
            text=[highlight.split()[0]],
            textposition='top center',
            textfont=dict(color='white', size=11, family='Inter', weight=600),
            showlegend=False
        ))
    
    # Labels dos quadrantes
    fig.add_annotation(x=x_max*0.92, y=y_max*0.95, text="COMPLETO",
                      showarrow=False, font=dict(color=COLORS['elite'], size=12, family='Inter', weight=700))
    fig.add_annotation(x=x_min*1.05, y=y_min*1.05, text="LIMITADO",
                      showarrow=False, font=dict(color=COLORS['below_avg'], size=12, family='Inter', weight=700))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=COLORS['text_primary'])),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title=dict(text=x_col, font=dict(size=12, color=COLORS['text_muted'])),
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(size=10, color=COLORS['text_muted']),
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text=y_col, font=dict(size=12, color=COLORS['text_muted'])),
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(size=10, color=COLORS['text_muted']),
            zeroline=False
        ),
        margin=dict(l=60, r=40, t=60, b=60),
        height=500
    )
    
    return fig


def create_physical_radar(player_row):
    """Radar de métricas físicas"""
    
    def safe_rank(val):
        if pd.isna(val):
            return 50
        return max(0, min(100, 100 - val))
    
    metrics = {
        'Distância': safe_rank(player_row.get('distance_per_90_rank')),
        'Sprints': safe_rank(player_row.get('sprint_count_per_90_rank')),
        'HI Runs': safe_rank(player_row.get('hi_count_per_90_rank')),
        'Velocidade': safe_rank(player_row.get('avg_psv99_rank')),
        'Acelerações': safe_rank(player_row.get('explacceltosprint_count_per_90_rank')),
    }
    
    return create_wyscout_radar(metrics)


# ============================================
# UI COMPONENTS
# ============================================

def render_player_header(player):
    """Header do jogador"""
    
    contrato = player['Contrato']
    if pd.notna(contrato):
        if isinstance(contrato, pd.Timestamp):
            contrato_str = contrato.strftime('%d/%m/%Y')
        else:
            contrato_str = str(contrato).split(' ')[0]
    else:
        contrato_str = '-'
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="player-header">
            <div class="player-position">{player['Posição'] or 'Jogador'}</div>
            <div class="player-name">{player['Nome']}</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Idade</span>
                    <span class="info-value">{int(player['Idade']) if pd.notna(player['Idade']) else '-'} anos ({int(player['Ano']) if pd.notna(player['Ano']) else '-'})</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Clube</span>
                    <span class="info-value">{player['Clube'] or '-'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Liga</span>
                    <span class="info-value">{player['Liga'] or '-'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Contrato</span>
                    <span class="info-value">{contrato_str}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Perfil</span>
                    <span class="info-value">{player['Perfil'] or '-'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Agente</span>
                    <span class="info-value">{player['Agente'] if pd.notna(player.get('Agente')) else '-'}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if pd.notna(player['Nota_Desempenho']):
            st.markdown(f"""
            <div class="rating-box">
                <div class="rating-label">Nota Geral</div>
                <div class="rating-value">{player['Nota_Desempenho']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if pd.notna(player.get('Link_TM')):
            st.markdown(f"""
            <div style="margin-top: 16px; text-align: center;">
                <a href="{player['Link_TM']}" target="_blank" style="
                    display: inline-block;
                    padding: 10px 20px;
                    background: {COLORS['bg_card']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    font-size: 13px;
                ">🔗 Transfermarkt</a>
            </div>
            """, unsafe_allow_html=True)


def render_legend():
    """Legenda dos percentis"""
    st.markdown(f"""
    <div class="legend-row">
        <div class="legend-item">
            <div class="legend-dot" style="background: {COLORS['elite']};"></div>
            <span>Elite (P90+)</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background: {COLORS['above_avg']};"></div>
            <span>Acima Média (P65-89)</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background: {COLORS['average']};"></div>
            <span>Média (P36-64)</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background: {COLORS['below_avg']};"></div>
            <span>Abaixo Média (P0-35)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# MAIN APP
# ============================================
def main():
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <div style="
                font-size: 11px;
                color: {COLORS['accent']};
                letter-spacing: 3px;
                font-weight: 600;
            ">SCOUTING</div>
            <div style="
                font-size: 28px;
                font-weight: 800;
                color: white;
                letter-spacing: -1px;
                margin: 4px 0;
            ">BOTAFOGO</div>
            <div style="
                font-size: 10px;
                color: {COLORS['text_muted']};
                letter-spacing: 2px;
            ">RIBEIRÃO PRETO</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Upload
        uploaded_file = st.file_uploader("📂 Carregar Planilha", type=['xlsx'])
        
        try:
            analises, central, oferecidos = load_data(uploaded_file)
        except Exception as e:
            st.error("⚠️ Erro ao carregar dados")
            st.info("Faça upload do arquivo Excel")
            return
        
        st.markdown("---")
        
        # Filtros
        st.markdown(f'<p style="color: {COLORS["text_muted"]}; font-size: 10px; text-transform: uppercase; letter-spacing: 1px;">Filtros</p>', unsafe_allow_html=True)
        
        posicoes = ['Todas'] + sorted([str(p) for p in analises['Posição'].dropna().unique()])
        posicao_sel = st.selectbox("Posição", posicoes)
        
        if posicao_sel != 'Todas':
            df_filtered = analises[analises['Posição'] == posicao_sel]
        else:
            df_filtered = analises
        
        jogadores = sorted([str(j) for j in df_filtered['Nome'].dropna().unique()])
        if not jogadores:
            st.warning("Nenhum jogador encontrado")
            return
            
        jogador_sel = st.selectbox("Jogador", jogadores)
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="color: {COLORS['text_muted']}; font-size: 11px;">
            📊 {len(analises)} jogadores analisados<br>
            🏃 {len(central)} com dados físicos
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Perfil", "📈 Comparativo", "🏃 Físico", "📋 Dados"])
    
    # TAB 1: PERFIL
    with tab1:
        if jogador_sel:
            player = df_filtered[df_filtered['Nome'] == jogador_sel].iloc[0]
            
            render_player_header(player)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">Atributos</div>', unsafe_allow_html=True)
                
                attrs = {cat: player[cat] for cat in ['Técnica', 'Físico', 'Tática', 'Mental']}
                fig = create_attribute_radar(attrs)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">Percentile Rankings</div>', unsafe_allow_html=True)
                
                perc_metrics = {}
                for attr in ['Técnica', 'Físico', 'Tática', 'Mental']:
                    val = player[attr]
                    perc_metrics[attr] = (val / 5) * 100 if pd.notna(val) else 50
                
                if pd.notna(player.get('Potencial')):
                    perc_metrics['Potencial'] = (player['Potencial'] / 5) * 100
                
                fig_perc = create_wyscout_radar(perc_metrics)
                st.plotly_chart(fig_perc, use_container_width=True, config={'displayModeBar': False})
                render_legend()
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Análise
            if pd.notna(player.get('Análise')):
                st.markdown("---")
                st.markdown('<div class="chart-title">Análise Qualitativa</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="analysis-container"><div class="analysis-text">{player["Análise"]}</div></div>', unsafe_allow_html=True)
    
    # TAB 2: COMPARATIVO
    with tab2:
        df_plot = df_filtered.dropna(subset=['Técnica', 'Físico', 'Tática', 'Mental']).copy()
        
        if len(df_plot) > 0:
            df_plot['Finalização'] = (df_plot['Técnica'] + df_plot['Físico']) / 2 * 20
            df_plot['Criação'] = (df_plot['Tática'] + df_plot['Mental']) / 2 * 20
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">Perfil: Finalização x Criação ({len(df_plot)} jogadores)</div>', unsafe_allow_html=True)
            
            fig_scatter = create_scatter_plot(df_plot, 'Finalização', 'Criação', jogador_sel)
            st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown('<div class="chart-title">Comparar Jogadores</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            j1 = st.selectbox("Jogador 1", jogadores, key='cmp1')
        with col2:
            j2 = st.selectbox("Jogador 2", jogadores, index=min(1, len(jogadores)-1), key='cmp2')
        
        if j1 and j2 and j1 != j2:
            p1 = df_filtered[df_filtered['Nome'] == j1].iloc[0]
            p2 = df_filtered[df_filtered['Nome'] == j2].iloc[0]
            
            p1_data = {c: p1[c] for c in ['Técnica', 'Físico', 'Tática', 'Mental']}
            p2_data = {c: p2[c] for c in ['Técnica', 'Físico', 'Tática', 'Mental']}
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_comp = create_comparison_radar(p1_data, p2_data, j1, j2)
            st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: FÍSICO
    with tab3:
        if len(central) > 0:
            jogadores_fisico = sorted([str(j) for j in central['Nome'].dropna().unique()])
            jf = st.selectbox("Selecionar Jogador", jogadores_fisico, key='phys')
            
            if jf:
                pf = central[central['Nome'] == jf].iloc[0]
                
                # Métricas
                cols = st.columns(4)
                metrics_display = [
                    ("Distância/90", f"{pf['distance_per_90']:.0f}m" if pd.notna(pf['distance_per_90']) else "N/A"),
                    ("Sprints/90", f"{pf['sprint_count_per_90']:.1f}" if pd.notna(pf['sprint_count_per_90']) else "N/A"),
                    ("HI Dist/90", f"{pf['hi_distance_per_90']:.0f}m" if pd.notna(pf['hi_distance_per_90']) else "N/A"),
                    ("Top Speed", f"{pf['avg_psv99']:.1f} km/h" if pd.notna(pf['avg_psv99']) else "N/A"),
                ]
                
                for col, (label, val) in zip(cols, metrics_display):
                    with col:
                        st.metric(label, val)
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown('<div class="chart-title">Rankings Físicos</div>', unsafe_allow_html=True)
                    fig_phys = create_physical_radar(pf.to_dict())
                    st.plotly_chart(fig_phys, use_container_width=True, config={'displayModeBar': False})
                    render_legend()
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown('<div class="chart-title">Velocidade x Volume</div>', unsafe_allow_html=True)
                    
                    df_phys = central.dropna(subset=['avg_psv99', 'distance_per_90'])
                    
                    fig_vel = go.Figure()
                    
                    fig_vel.add_trace(go.Scatter(
                        x=df_phys['avg_psv99'],
                        y=df_phys['distance_per_90'],
                        mode='markers',
                        marker=dict(size=10, color=COLORS['text_muted'], opacity=0.4),
                        text=df_phys['Nome'],
                        hovertemplate='<b>%{text}</b><br>%{x:.1f} km/h | %{y:.0f}m<extra></extra>',
                        showlegend=False
                    ))
                    
                    if jf in df_phys['Nome'].values:
                        pr = df_phys[df_phys['Nome'] == jf].iloc[0]
                        fig_vel.add_trace(go.Scatter(
                            x=[pr['avg_psv99']],
                            y=[pr['distance_per_90']],
                            mode='markers+text',
                            marker=dict(size=16, color=COLORS['accent'], line=dict(width=2, color='white')),
                            text=[jf.split()[0]],
                            textposition='top center',
                            textfont=dict(color='white', size=11),
                            showlegend=False
                        ))
                    
                    fig_vel.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(title='Velocidade (km/h)', gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color=COLORS['text_muted'])),
                        yaxis=dict(title='Distância/90 (m)', gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color=COLORS['text_muted'])),
                        margin=dict(l=60, r=40, t=20, b=60),
                        height=350
                    )
                    
                    st.plotly_chart(fig_vel, use_container_width=True, config={'displayModeBar': False})
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Sem dados físicos disponíveis")
    
    # TAB 4: DADOS
    with tab4:
        tab_data = st.radio("", ['Análises', 'Dados Físicos', 'Oferecidos'], horizontal=True)
        
        if tab_data == 'Análises':
            cols_show = ['Nome', 'Posição', 'Idade', 'Clube', 'Liga', 'Perfil', 'Nota_Desempenho']
            df_show = df_filtered[[c for c in cols_show if c in df_filtered.columns]]
        elif tab_data == 'Dados Físicos':
            cols_show = ['Nome', 'Clube', 'Posição', 'distance_per_90', 'sprint_count_per_90', 'avg_psv99']
            df_show = central[[c for c in cols_show if c in central.columns]]
        else:
            df_show = oferecidos
        
        st.dataframe(df_show, use_container_width=True, height=500)
        
        csv = df_show.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar CSV", csv, f"{tab_data.lower().replace(' ', '_')}.csv")


if __name__ == "__main__":
    main()
