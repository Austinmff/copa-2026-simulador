"""
Módulo de Simulação Estatística - Copa do Mundo FIFA 2026
Responsável pelos cálculos de gols esperados, partidas isoladas e chaveamento completo.
"""

import random
import numpy as np
from collections import defaultdict
from typing import Tuple, Dict, List, Any
from worldcup.data_loader import get_team_stats, get_groups


def get_expected_goals(team_a: str, team_b: str, stage_modifier: int) -> Tuple[float, float]:
    """
    Calcula a média de golos esperados (λ) para cada equipa em uma partida específica.

    Utiliza a modelagem de distribuição de Poisson baseada na força relativa (Elo) 
    e nos coeficientes individuais de ataque e defesa. Incorpora uma heurística de 
    fadiga com base na profundidade do plantel (squad_depth).

    Nota Estatística: Este modelo assume independência estocástica entre os gols 
    marcados pelas duas equipes, funcionando como uma aproximação ágil.
    """
    stats_a = get_team_stats(team_a)
    stats_b = get_team_stats(team_b)

    # Heurística de Fadiga Acumulada: Reduz o Elo conforme o torneio avança
    fatigue_a = stage_modifier * (10.0 - stats_a["squad_depth"]) * 5
    fatigue_b = stage_modifier * (10.0 - stats_b["squad_depth"]) * 5

    eff_elo_a = stats_a["elo"] - fatigue_a
    eff_elo_b = stats_b["elo"] - fatigue_b

    # Fator multiplicador baseado na diferença de rating Elo clássico
    elo_diff_factor = 10 ** ((eff_elo_a - eff_elo_b) / 400)

    # Cálculo do Lambda (gols esperados) cruzando Força de Ataque vs Solidez de Defesa
    lambda_a = (stats_a["attack"] * stats_b["defense"]) * (elo_diff_factor ** 0.5)
    lambda_b = (stats_b["attack"] * stats_a["defense"]) * ((1 / elo_diff_factor) ** 0.5)

    # Volatilidade: Injeta variabilidade aleatória normal para simular oscilações do dia do jogo
    lambda_a *= np.random.normal(1.0, (stats_a["volatility"] * 0.1))
    lambda_b *= np.random.normal(1.0, (stats_b["volatility"] * 0.1))

    return max(0.1, lambda_a), max(0.1, lambda_b)


def simulate_match(team_a: str, team_b: str, stage_modifier: int, knockout: bool = False) -> Tuple[str, int, int]:
    """
    Simula uma única partida do torneio por amostragem pontual de Poisson.
    Retorna o vencedor (ou 'Draw' em grupos) e o placar final.
    """
    lambda_a, lambda_b = get_expected_goals(team_a, team_b, stage_modifier)

    gols_a = int(np.random.poisson(lambda_a))
    gols_b = int(np.random.poisson(lambda_b))

    if gols_a > gols_b:
        return team_a, gols_a, gols_b
    elif gols_b > gols_a:
        return team_b, gols_a, gols_b
    else:
        if knockout:
            # Desempate probabilístico baseado no Elo (Heurística simplificada de Prorrogação/Pênaltis)
            stats_a = get_team_stats(team_a)
            stats_b = get_team_stats(team_b)
            prob_a = stats_a["elo"] / (stats_a["elo"] + stats_b["elo"])
            
            winner = team_a if random.random() < prob_a else team_b
            return winner, gols_a, gols_b
            
        return "Draw", gols_a, gols_b


def simulate_matchup_vectorized(team_a: str, team_b: str, stage_modifier: int, n_simulations: int = 1000) -> Tuple[int, int]:
    """
    Simula N confrontos diretos de forma inteiramente vetorizada em memória usando NumPy.
    Garante alta performance para o simulador de jogo único no painel Streamlit, eliminando loops Python.
    """
    lambda_a, lambda_b = get_expected_goals(team_a, team_b, stage_modifier)

    # Amostragem massiva instantânea via NumPy
    gols_a = np.random.poisson(lambda_a, n_simulations)
    gols_b = np.random.poisson(lambda_b, n_simulations)

    vitorias_a = np.sum(gols_a > gols_b)
    vitorias_b = np.sum(gols_b > gols_a)
    empates = np.sum(gols_a == gols_b)

    if empates > 0:
        stats_a = get_team_stats(team_a)
        stats_b = get_team_stats(team_b)
        prob_a = stats_a["elo"] / (stats_a["elo"] + stats_b["elo"])

        # Sorteio vetorizado para resolver todos os empates simultaneamente
        desempates_a = np.sum(np.random.random(empates) < prob_a)
        vitorias_a += desempates_a
        vitorias_b += (empates - desempates_a)

    return int(vitorias_a), int(vitorias_b)


def run_tournament() -> Dict[str, Any]:
    """Executa o fluxo completo do campeonato baseado nas regras oficiais da FIFA 2026."""
    groups = get_groups()
    group_stats = defaultdict(lambda: defaultdict(lambda: {"pts": 0, "gd": 0, "gf": 0}))
    third_places = []

    # 1. Fase de Grupos
    for g, teams in groups.items():
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                winner, ga, gb = simulate_match(teams[i], teams[j], stage_modifier=0, knockout=False)
                group_stats[g][teams[i]]["gf"] += ga
                group_stats[g][teams[j]]["gf"] += gb
                group_stats[g][teams[i]]["gd"] += (ga - gb)
                group_stats[g][teams[j]]["gd"] += (gb - ga)

                if winner == teams[i]:
                    group_stats[g][teams[i]]["pts"] += 3
                elif winner == teams[j]:
                    group_stats[g][teams[j]]["pts"] += 3
                else:
                    group_stats[g][teams[i]]["pts"] += 1
                    group_stats[g][teams[j]]["pts"] += 1

        # Critério de desempate simplificado: Pontos -> Saldo de Gols -> Gols Pró
        ranking = sorted(teams, key=lambda t: (group_stats[g][t]["pts"], group_stats[g][t]["gd"], group_stats[g][t]["gf"]), reverse=True)
        group_stats[g]["1st"] = ranking[0]
        group_stats[g]["2nd"] = ranking[1]
        third_places.append((ranking[2], group_stats[g][ranking[2]]["pts"], group_stats[g][ranking[2]]["gd"], group_stats[g][ranking[2]]["gf"]))

    # Resolução dos 8 melhores terceiros colocados gerais
    third_places.sort(key=lambda x: (x[1], x[2], x[3]), reverse=True)
    best_thirds = [x[0] for x in third_places[:8]]

    # 2. Dezasseis-avos-de-final (Rodada de 32)
    r32_matchups = [
        (group_stats["A"]["2nd"], group_stats["B"]["2nd"]), (group_stats["E"]["1st"], best_thirds[0]),
        (group_stats["F"]["1st"], group_stats["C"]["2nd"]), (group_stats["C"]["1st"], group_stats["F"]["2nd"]),
        (group_stats["I"]["1st"], best_thirds[1]),          (group_stats["E"]["2nd"], group_stats["I"]["2nd"]),
        (group_stats["A"]["1st"], best_thirds[2]),          (group_stats["L"]["1st"], best_thirds[3]),
        (group_stats["D"]["1st"], best_thirds[4]),          (group_stats["G"]["1st"], best_thirds[5]),
        (group_stats["K"]["2nd"], group_stats["L"]["2nd"]), (group_stats["H"]["1st"], group_stats["J"]["2nd"]),
        (group_stats["B"]["1st"], best_thirds[6]),          (group_stats["J"]["1st"], group_stats["H"]["2nd"]),
        (group_stats["K"]["1st"], best_thirds[7]),          (group_stats["D"]["2nd"], group_stats["G"]["2nd"]),
    ]

    r16_teams = []
    for a, b in r32_matchups:
        w, _, _ = simulate_match(a, b, stage_modifier=1, knockout=True)
        r16_teams.append(w)

    # 3. Oitavos-de-final
    qf_teams = []
    for i in range(0, 16, 2):
        w, _, _ = simulate_match(r16_teams[i], r16_teams[i + 1], stage_modifier=2, knockout=True)
        qf_teams.append(w)

    # 4. Quartos-de-final (Fadiga passa a exercer forte peso)
    sf_teams = []
    for i in range(0, 8, 2):
        w, _, _ = simulate_match(qf_teams[i], qf_teams[i + 1], stage_modifier=3, knockout=True)
        sf_teams.append(w)

    # 5. Meias-finais
    finalists = []
    for i in range(0, 4, 2):
        w, _, _ = simulate_match(sf_teams[i], sf_teams[i + 1], stage_modifier=4, knockout=True)
        finalists.append(w)

    # 6. Final do Torneio
    champion, _, _ = simulate_match(finalists[0], finalists[1], stage_modifier=5, knockout=True)

    return {"champion": champion, "final": finalists, "semi": sf_teams, "quarter": qf_teams}