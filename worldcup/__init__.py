"""
Motor Matemático Vetorizado - Copa do Mundo 2026
"""
import numpy as np
import random

# Importações temporárias (mudaremos no Passo B para ler JSON)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from teams_data import get_team_stats

def obter_golos_esperados(time_a: str, time_b: str, modificador_fase: int, usar_cortes: bool = True) -> tuple:
    """Calcula o Lambda (xG) cruzando Ataque A vs Defesa B e ajustando por Fadiga."""
    stats_a = get_team_stats(time_a)
    stats_b = get_team_stats(time_b)
    
    if not usar_cortes:
        stats_a, stats_b = stats_a.copy(), stats_b.copy()
        if time_a == "Brazil": stats_a["defense"], stats_a["squad_depth"] = 0.7, 8.5
        if time_b == "Brazil": stats_b["defense"], stats_b["squad_depth"] = 0.7, 8.5

    canso_a = modificador_fase * (10.0 - stats_a["squad_depth"]) * 5
    canso_b = modificador_fase * (10.0 - stats_b["squad_depth"]) * 5
    
    fator_forca = 10 ** (((stats_a["elo"] - canso_a) - (stats_b["elo"] - canso_b)) / 400)
    
    lambda_a = (stats_a["attack"] * stats_b["defense"]) * (fator_forca ** 0.5)
    lambda_b = (stats_b["attack"] * stats_a["defense"]) * ((1/fator_forca) ** 0.5)
    
    return max(0.1, lambda_a), max(0.1, lambda_b)

def simular_jogos_vetorizado(time_a: str, time_b: str, modificador_fase: int, n_simulacoes: int = 1000) -> tuple:
    """
    Simula N jogos simultaneamente usando matrizes NumPy (Vetorização).
    Elimina o loop 'for', aumentando a performance em até 100x.
    """
    la, lb = obter_golos_esperados(time_a, time_b, modificador_fase, usar_cortes=True)
    
    # Gera TODOS os jogos de uma vez só!
    golos_a = np.random.poisson(la, n_simulacoes)
    golos_b = np.random.poisson(lb, n_simulacoes)
    
    # Conta as vitórias diretamente no array
    vitorias_a = np.sum(golos_a > golos_b)
    vitorias_b = np.sum(golos_b > golos_a)
    empates = np.sum(golos_a == golos_b)
    
    # Resolve todos os empates de uma vez só (Desempate por Elo)
    if empates > 0:
        s_a, s_b = get_team_stats(time_a), get_team_stats(time_b)
        prob_a = s_a["elo"] / (s_a["elo"] + s_b["elo"])
        
        # Sorteia N números aleatórios de uma vez para decidir os empates
        desempates_a = np.sum(np.random.random(empates) < prob_a)
        
        vitorias_a += desempates_a
        vitorias_b += (empates - desempates_a)
        
    return int(vitorias_a), int(vitorias_b)