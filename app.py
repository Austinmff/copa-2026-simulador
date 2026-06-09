"""
Copa do Mundo FIFA 2026 — Painel Analítico Interativo
Interface Gráfica Simples e Didática usando Streamlit e Plotly
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
from collections import defaultdict

# Importações dos ficheiros originais do projeto
from groups_odds import GROUPS, RAW_ODDS
from teams_data import get_team_stats, TEAMS_DATA

# Dicionário de Tradução dos Países para o Utilizador Final
TRADUCAO_PAISES = {
    "Argentina": "Argentina", "France": "França", "Brazil": "Brasil", "Spain": "Espanha",
    "England": "Inglaterra", "Portugal": "Portugal", "Germany": "Alemanha", "Netherlands": "Países Baixos (Holanda)",
    "Belgium": "Bélgica", "USA": "Estados Unidos", "Mexico": "México", "Uruguay": "Uruguai",
    "Japan": "Japão", "Morocco": "Marrocos", "Colombia": "Colômbia", "Norway": "Noruega",
    "Senegal": "Senegal", "South Korea": "Coreia do Sul", "Croatia": "Croácia", "Switzerland": "Suíça",
    "Turkey": "Turquia", "Sweden": "Suécia", "Ecuador": "Equador", "Canada": "Canadá",
    "Czechia": "Chéquia", "South Africa": "África do Sul", "Bosnia & Herzegovina": "Bósnia",
    "Qatar": "Catar", "Haiti": "Haiti", "Scotland": "Escócia", "Paraguay": "Paraguai",
    "Australia": "Austrália", "Ivory Coast": "Costa do Marfim", "Curacao": "Curaçau",
    "Tunisia": "Tunísia", "Egypt": "Egito", "Iran": "Irão", "New Zealand": "Nova Zelândia",
    "Saudi Arabia": "Arábia Saudita", "Cape Verde": "Cabo Verde", "Iraq": "Iraque",
    "Algeria": "Argélia", "Austria": "Áustria", "Jordan": "Jordânia", "DR Congo": "R.D. Congo",
    "Uzbekistan": "Usbequistão", "Ghana": "Gana", "Panama": "Panamá"
}

# 1. CONFIGURAÇÃO DA INTERFACE
st.set_page_config(
    page_title="Previsões Copa do Mundo 2026",
    page_icon="🏆",
    layout="wide"
)

# Estilização Visual em Português e Cores da Copa (Premium Dark)
st.markdown("""
    <style>
    .stApp {
        background-color: #000b1a;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #001529;
        border-right: 2px solid #d4af37;
    }
    h1, h2, h3 {
        color: #d4af37 !important;
        font-weight: 700;
    }
    .card-favorito {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(212, 175, 55, 0.3);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE CÁLCULO ESTATÍSTICO
def obter_golos_esperados(time_a, time_b, modificador_fase, usar_cortes=True):
    stats_a = get_team_stats(time_a)
    stats_b = get_team_stats(time_b)
    
    if not usar_cortes:
        stats_a = stats_a.copy()
        stats_b = stats_b.copy()
        if time_a == "Brazil": stats_a["defense"], stats_a["squad_depth"] = 0.7, 8.5
        if time_b == "Brazil": stats_b["defense"], stats_b["squad_depth"] = 0.7, 8.5

    canso_a = modificador_fase * (10.0 - stats_a["squad_depth"]) * 5
    canso_b = modificador_fase * (10.0 - stats_b["squad_depth"]) * 5
    
    elo_final_a = stats_a["elo"] - canso_a
    elo_final_b = stats_b["elo"] - canso_b
    
    fator_forca = 10 ** ((elo_final_a - elo_final_b) / 400)
    
    lambda_a = (stats_a["attack"] * stats_b["defense"]) * (fator_forca ** 0.5)
    lambda_b = (stats_b["attack"] * stats_a["defense"]) * ((1/fator_forca) ** 0.5)
    return max(0.1, lambda_a), max(0.1, lambda_b)

def simular_jogo(time_a, time_b, modificador_fase, eliminar_direto=False, usar_cortes=True):
    la, lb = obter_golos_esperados(time_a, time_b, modificador_fase, usar_cortes)
    golos_a = np.random.poisson(la)
    golos_b = np.random.poisson(lb)
    
    if golos_a > golos_b: return time_a
    elif golos_b > golos_a: return time_b
    elif eliminar_direto:
        s_a, s_b = get_team_stats(time_a), get_team_stats(time_b)
        return time_a if random.random() < s_a["elo"]/(s_a["elo"]+s_b["elo"]) else time_b
    return "Empate"

def rodar_campeonato(usar_cortes=True):
    pontos_grupos = defaultdict(lambda: defaultdict(lambda: {"pts": 0}))
    terceiros = []
    
    for g, times in GROUPS.items():
        for i in range(len(times)):
            for j in range(i+1, len(times)):
                resultado = simular_jogo(times[i], times[j], 0, False, usar_cortes)
                if resultado == times[i]: pontos_grupos[g][times[i]]["pts"] += 3
                elif resultado == times[j]: pontos_grupos[g][times[j]]["pts"] += 3
                else: pontos_grupos[g][times[i]]["pts"], pontos_grupos[g][times[j]]["pts"] = pontos_grupos[g][times[i]]["pts"]+1, pontos_grupos[g][times[j]]["pts"]+1
        ranking = sorted(times, key=lambda t: pontos_grupos[g][t]["pts"], reverse=True)
        pontos_grupos[g]["1º"], pontos_grupos[g]["2º"] = ranking[0], ranking[1]
        terceiros.append((ranking[2], pontos_grupos[g][ranking[2]]["pts"]))
        
    terceiros.sort(key=lambda x: x[1], reverse=True)
    melhores_terceiros = [x[0] for x in terceiros[:8]]
    
    confrontos = [
        (pontos_grupos["A"]["2º"], pontos_grupos["B"]["2º"]), (pontos_grupos["E"]["1º"], melhores_terceiros[0]),
        (pontos_grupos["F"]["1º"], pontos_grupos["C"]["2º"]), (pontos_grupos["C"]["1º"], pontos_grupos["F"]["2º"]),
        (pontos_grupos["I"]["1º"], melhores_terceiros[1]),    (pontos_grupos["E"]["2º"], pontos_grupos["I"]["2º"]),
        (pontos_grupos["A"]["1º"], melhores_terceiros[2]),    (pontos_grupos["L"]["1º"], melhores_terceiros[3]),
        (pontos_grupos["D"]["1º"], melhores_terceiros[4]),    (pontos_grupos["G"]["1º"], melhores_terceiros[5]),
        (pontos_grupos["K"]["2º"], pontos_grupos["L"]["2º"]), (pontos_grupos["H"]["1º"], pontos_grupos["J"]["2º"]),
        (pontos_grupos["B"]["1º"], melhores_terceiros[6]),    (pontos_grupos["J"]["1º"], pontos_grupos["H"]["2º"]),
        (pontos_grupos["K"]["1º"], melhores_terceiros[7]),    (pontos_grupos["D"]["2º"], pontos_grupos["G"]["2º"])
    ]
    
    oitavas = [simular_jogo(a, b, 1, True, usar_cortes) for a, b in confrontos]
    quartas = [simular_jogo(oitavas[i], oitavas[i+1], 2, True, usar_cortes) for i in range(0, 16, 2)]
    semis = [simular_jogo(quartas[i], quartas[i+1], 3, True, usar_cortes) for i in range(0, 8, 2)]
    final = [simular_jogo(semis[i], semis[i+1], 4, True, usar_cortes) for i in range(0, 4, 2)]
    campeao = simular_jogo(final[0], final[1], 5, True, usar_cortes)
    return oitavas, quartas, semis, final, campeao

@st.cache_data(show_spinner="Simulando Mundiais...")
def gerar_dados_simulados(n=10000):
    contagem = defaultdict(lambda: defaultdict(int))
    for _ in range(n):
        oit, qua, sem, fin, cam = rodar_campeonato(True)
        for t in oit: contagem[t]["Oitavas"] += 1
        for t in qua: contagem[t]["Quartas"] += 1
        for t in sem: contagem[t]["Semifinais"] += 1
        for t in fin: contagem[t]["Final"] += 1
        contagem[cam]["Campeão"] += 1
        
    dados_finais = []
    for t in RAW_ODDS.keys():
        nome_pt = TRADUCAO_PAISES.get(t, t)
        dados_finais.append({
            "Seleção": nome_pt,
            "Chances de Oitavas (%)": round((contagem[t]["Oitavas"]/n)*100, 2),
            "Chances de Quartas (%)": round((contagem[t]["Quartas"]/n)*100, 2),
            "Chances de Semifinais (%)": round((contagem[t]["Semifinais"]/n)*100, 2),
            "Chances de Final (%)": round((contagem[t]["Final"]/n)*100, 2),
            "Chance de Título (%)": round((contagem[t]["Campeão"]/n)*100, 2)
        })
    return pd.DataFrame(dados_finais).sort_values(by="Chance de Título (%)", ascending=False).reset_index(drop=True)

# 3. APRESENTAÇÃO DO PAINEL PRINCIPAL
st.markdown("""
    <div style="background: linear-gradient(90deg, #001f3f 0%, #00d4ff 100%); padding: 25px; border-radius: 15px; border-bottom: 4px solid #d4af37; margin-bottom: 25px">
        <h1 style="margin:0; color:white !important; font-size: 2.8em">🏆 SIMULADOR INTELIGENTE COPA 2026</h1>
        <p style="color: #d4af37; font-size: 1.2em; margin:0">A matemática aplicada ao futebol de forma simples e visual.</p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("### 🛠️ Configurações")
st.sidebar.write("Escolha quantas vezes o computador vai simular o torneio inteiro para calcular os resultados:")
iteracoes = st.sidebar.select_slider("Número de Torneios Simulados", options=[1000, 5000, 10000], value=10000)
df_copa = gerar_dados_simulados(iteracoes)

st.markdown("### 🔥 Os 3 Maiores Favoritos ao Título")
top3 = df_copa.head(3)
colunas_top = st.columns(3)
for i, (idx, linha) in enumerate(top3.iterrows()):
    with colunas_top[i]:
        st.markdown(f"""
            <div class="card-favorito">
                <p style="font-size: 1.1em; color: #d4af37; margin:0">🏆 {i+1}º Favorito</p>
                <h2 style="margin: 5px 0; color: white !important">{linha['Seleção']}</h2>
                <h1 style="margin:0; font-size: 2.5em">{linha['Chance de Título (%)']}%</h1>
                <p style="margin:0; opacity:0.7; font-size:0.9em">de chance de ganhar a Copa</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Definição das Abas Didáticas
aba1, aba2, aba3 = st.tabs(["📊 Probabilidades Completas", "🩹 Desfalques & Lesões", "⚔️ Simulador de Jogo Único"])

with aba1:
    st.markdown("### Quanto mais alta a barra, maior a hipótese de ser campeão:")
    col_grafico, col_tabela = st.columns([2, 1])
    
    with col_grafico:
        figura = px.bar(
            df_copa.head(12), x="Seleção", y="Chance de Título (%)",
            title="Top 12 Candidatos à Taça",
            labels={"Chance de Título (%)": "Probabilidade de Título (%)"},
            color="Chance de Título (%)", color_continuous_scale="YlOrRd"
        )
        figura.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(figura, use_container_width=True)
        
    with col_tabela:
        st.markdown("### Lista Geral (Top 10)")
        st.dataframe(df_copa[["Seleção", "Chance de Título (%)"]].head(10), height=350, use_container_width=True)

with aba2:
    st.markdown("### 🩺 Como os cortes médicos mudaram o favoritismo?")
    st.write("O nosso modelo calcula o cansaço acumulado dos jogadores ao longo das fases. Se uma seleção perde atletas importantes antes do campeonato começar, o banco de reservas enfraquece e o time perde rendimento nos jogos decisivos da fase final.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card-favorito" style="border-color: #ff4d4d; text-align: left">
            <h3 style="color: #ff4d4d !important; margin:0">Brasil 🇧🇷</h3>
            <p style="margin:5px 0">Os cortes de <b>Rodrygo</b> e <b>Wesley</b> deixaram o Brasil sem laterais suplentes de alto nível.</p>
            <p style="margin:0"><b>Impacto no Modelo:</b> O Brasil avança sem dificuldades nas fases iniciais, mas chega desgastado às Semifinais e perde força estatística contra gigantes inteiros como a França ou a Argentina.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card-favorito" style="border-color: #ff4d4d; text-align: left">
            <h3 style="color: #ff4d4d !important; margin:0">Alemanha 🇩🇪</h3>
            <p style="margin:5px 0">A ausência do avançado <b>Serge Gnabry</b> reduziu a pontuação do ataque germânico.</p>
            <p style="margin:0"><b>Impacto no Modelo:</b> O poder de fogo diminuiu, tornando a equipa alemã muito mais vulnerável a sofrer empates ou derrotas inesperadas contra seleções de médio porte (zebras).</p>
        </div>
        """, unsafe_allow_html=True)

with aba3:
    st.markdown("### ⚔️ Simulador de Confronto Direto Interativo")
    st.write("Cruze os dados matemáticos de duas seleções num jogo simulado 1.000 vezes na hora para ver quem tem mais chances de vencer numa fase de mata-mata.")
    
    lista_paises_pt = sorted(list(TRADUCAO_PAISES.values()))
    lista_paises_en = sorted(list(RAW_ODDS.keys()))
    
    col_t1, col_t2 = st.columns(2)
    
    nome_pt_1 = col_t1.selectbox("Escolha a Primeira Equipa", lista_paises_pt, index=lista_paises_pt.index("Brasil"))
    nome_pt_2 = col_t2.selectbox("Escolha a Segunda Equipa", lista_paises_pt, index=lista_paises_pt.index("Inglaterra"))
    
    # Inverter a tradução para enviar o nome correto em inglês para o motor
    t1_en = [k for k, v in TRADUCAO_PAISES.items() if v == nome_pt_1][0]
    t2_en = [k for k, v in TRADUCAO_PAISES.items() if v == nome_pt_2][0]
    
    if st.button("Iniciar Confronto"):
        v1, v2 = 0, 0
        for _ in range(1000):
            res = simular_jogo(t1_en, t2_en, modificador_fase=3, eliminar_direto=True)
            if res == t1_en: v1 += 1
            else: v2 += 1
            
        st.markdown(f"#### 📊 Probabilidade de Classificação num jogo decisivo:")
        col_t1.metric(nome_pt_1, f"{v1/10}% de hipóteses de passar")
        col_t2.metric(nome_pt_2, f"{v2/10}% de hipóteses de passar")
        st.progress(v1/1000)