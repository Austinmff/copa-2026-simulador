"""
Interface Gráfica (Dashboard) - Simulador Copa do Mundo 2026
Construído em Streamlit e Plotly para visualização dinâmica de probabilidades.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from collections import defaultdict

from worldcup.data_loader import load_json, get_groups
from worldcup.simulation import run_tournament, simulate_matchup_vectorized

# Configurações de página do Streamlit
st.set_page_config(
    page_title="Simulador Copa do Mundo 2026",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 Simulador Probabilístico - Copa do Mundo FIFA 2026")
st.markdown(
    "Este painel executa simulações estocásticas (Monte Carlo) combinando o "
    "**Ranking Elo** das seleções com a distribuição de **Poisson** para projetar cenários do torneio."
)
st.write("---")

# Carga inicial de dados para preenchimento dos componentes visuais
teams_dict = load_json("teams.json")
all_teams = sorted(list(teams_dict.keys()))

# Barra Lateral - Painel de Controle de Parâmetros
st.sidebar.header("⚙️ Configurações da Simulação")
st.sidebar.markdown("### Escala Macro (Monte Carlo)")
iterations = st.sidebar.slider(
    "Número de Iterações do Torneio",
    min_value=1000,
    max_value=20000,
    value=5000,
    step=1000,
    help="Defina o volume de campeonatos simulados em segundo plano. Valores maiores aumentam a convergência estatística."
)

st.sidebar.write("---")
st.sidebar.markdown("### 📋 Contexto de Mercado (Maio/2026)")
st.sidebar.info(
    "Dados estáticos baseados em snapshots de mercados preditivos (Polymarket/BetMGM).\n\n"
    "**Ajustes de Elenco Aplicados:**\n"
    "- **Brasil:** Penalizado em Defesa (1.1) e Profundidade (7.0) devido aos cortes de Rodrygo e Wesley.\n"
    "- **Alemanha:** Penalizado em Ataque (1.9) pela ausência de Serge Gnabry."
)

# Definição das Abas da Aplicação
tab1, tab2 = st.tabs(["📊 Projeções Estatísticas Gerais", "⚔️ Simulador de Confronto Direto"])

# ==========================================
# ABA 1: PROJEÇÕES GERAIS (MONTE CARLO)
# ==========================================
with tab1:
    st.header("📈 Prospecção de Probabilidades Avançadas")
    st.markdown(
        "Execute simulações em lote do torneio completo para mapear as chances "
        "reais de cada seleção avançar de fase."
    )
    
    if st.button("🚀 Rodar Simulação em Lote", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Estrutura de contagem para as fases do torneio
        counters = {
            "champion": defaultdict(int),
            "final": defaultdict(int),
            "semi": defaultdict(int),
            "quarter": defaultdict(int)
        }
        
        # Loop de simulação com atualização visual de progresso
        for i in range(1, iterations + 1):
            if i % max(1, (iterations // 10)) == 0:
                pct = i / iterations
                progress_bar.progress(pct)
                status_text.text(f"Processando: {i:,} / {iterations:,} campeonatos resolvidos...")
                
            res = run_tournament()
            counters["champion"][res["champion"]] += 1
            for team in res["final"]:
                counters["final"][team] += 1
            for team in res["semi"]:
                counters["semi"][team] += 1
            for team in res["quarter"]:
                counters["quarter"][team] += 1
                
        progress_bar.empty()
        status_text.success(f"🎉 Sucesso! {iterations:,} campeonatos processados com estabilidade matemática.")
        
        # Consolidação dos resultados em DataFrame do Pandas
        consolidated_data = []
        for team in all_teams:
            consolidated_data.append({
                "Seleção": team,
                "Quartas (%)": round((counters["quarter"][team] / iterations) * 100, 2),
                "Semifinal (%)": round((counters["semi"][team] / iterations) * 100, 2),
                "Final (%)": round((counters["final"][team] / iterations) * 100, 2),
                "Campeão (%)": round((counters["champion"][team] / iterations) * 100, 2),
            })
            
        df_res = pd.DataFrame(consolidated_data).sort_values(by="Campeão (%)", ascending=False).reset_index(drop=True)
        
        # Exibição dos Gráficos e Tabelas Líderes
        col_graph, col_table = st.columns([3, 2])
        
        with col_graph:
            st.subheader("🏆 Probabilidade de Título (Top 10)")
            fig = px.bar(
                df_res.head(10),
                x="Campeão (%)",
                y="Seleção",
                orientation='h',
                color="Campeão (%)",
                color_continuous_scale="Viridis",
                text="Campeão (%)"
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_table:
            st.subheader("📋 Matriz de Probabilidades Ordenada")
            st.dataframe(
                df_res.style.background_gradient(cmap="Blues", subset=["Campeão (%)", "Final (%)"]),
                use_container_width=True,
                height=400
            )

# ==========================================
# ABA 2: CONFRONTO DIRETO VETORIZADO
# ==========================================
with tab2:
    st.header("⚔️ Análise de Confronto Direto Isolado")
    st.markdown(
        "Selecione dois países para disputar uma série massiva de **10.000 partidas simultâneas** "
        "via vetorização em memória (NumPy). O desempate de mata-mata utiliza a razão proporcional do ranking Elo."
    )
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        team_a = st.selectbox("Selecione a Seleção A", all_teams, index=2) # Padrão: Brazil
        stats_a = teams_dict[team_a]
        st.metric("Rating Elo Base", f"{stats_a['elo']}")
        st.caption(f"Ataque: {stats_a['attack']} | Defesa: {stats_a['defense']} | Banco: {stats_a['squad_depth']}")
        
    with col_t2:
        team_b = st.selectbox("Selecione a Seleção B", all_teams, index=0) # Padrão: Argentina
        stats_b = teams_dict[team_b]
        st.metric("Rating Elo Base", f"{stats_b['elo']}")
        st.caption(f"Ataque: {stats_b['attack']} | Defesa: {stats_b['defense']} | Banco: {stats_b['squad_depth']}")
        
    st.write("---")
    
    if st.button("⚡ Executar Matchup Vetorizado (10.000 Jogos)", type="primary"):
        with st.spinner("Processando tensores aleatórios com NumPy..."):
            # Executa os 10k confrontos sem loops Python
            v_a, v_b = simulate_matchup_vectorized(team_a, team_b, stage_modifier=3, n_simulations=10000)
            
        prob_a = (v_a / 10000) * 100
        prob_b = (v_b / 10000) * 100
        
        st.subheader("📊 Balanço Probabilístico de Qualificação")
        
        col_res_a, col_res_b = st.columns(2)
        col_res_a.metric(f"Chances de Avanço - {team_a}", f"{prob_a:.2f}%")
        col_res_b.metric(f"Chances de Avanço - {team_b}", f"{prob_b:.2f}%")
        
        st.progress(v_a / 10000)
        st.caption("Barra de dominância: O preenchimento para a direita representa a vantagem competitiva da Seleção A.")