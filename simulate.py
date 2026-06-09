"""
Script de Execução em Linha de Comando (CLI) - Simulador Copa do Mundo 2026
Executa simulações estatísticas em larga escala (Monte Carlo) para convergência de dados.
"""

import sys
import os
import time
from collections import defaultdict
import pandas as pd

# Garante que o pacote worldcup seja visível independentemente de onde o script é chamado
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from worldcup.simulation import run_tournament


if __name__ == "__main__":
    ITERATIONS = 100000
    print(f"📊 Iniciando modelo híbrido modular (Elo + Poisson) com {ITERATIONS:,} iterações...")
    print("⏳ Por favor, aguarde. O processamento estatístico profundo pode levar alguns segundos...")
    
    start_time = time.time()
    
    # Contadores estruturados para armazenamento dos resultados de Monte Carlo
    counters = {
        "champion": defaultdict(int),
        "final": defaultdict(int),
        "semi": defaultdict(int),
        "quarter": defaultdict(int)
    }
    
    # Execução do loop em lote
    for i in range(1, ITERATIONS + 1):
        if i % 25000 == 0:
            print(f"   -> {i:,} simulações concluídas...")
            
        res = run_tournament()
        
        # Incrementa estatísticas agregadas
        counters["champion"][res["champion"]] += 1
        for team in res["final"]:
            counters["final"][team] += 1
        for team in res["semi"]:
            counters["semi"][team] += 1
        for team in res["quarter"]:
            counters["quarter"][team] += 1

    # Conversão das frequências brutas para percentagens probabilísticas
    results = {}
    for stage, counter in counters.items():
        results[stage] = {
            team: round((count / ITERATIONS) * 100, 2)
            for team, count in sorted(counter.items(), key=lambda x: -x[1])
        }
        
    end_time = time.time()
    print(f"\n✅ Análise concluída em {round(end_time - start_time, 1)} segundos.")

    # Exibição do relatório final formatado diretamente no terminal
    print("\n🏆 === RELATÓRIO FINAL: CHANCES DE TÍTULO (Top 10) ===")
    for rank, (team, prob) in enumerate(list(results["champion"].items())[:10], 1):
        print(f" {rank:2d}º  {team:<15} : {prob:5.2f}%")
        
    print("\n🛡️ === CHANCES DE CHEGAR ÀS MEIAS-FINAIS ===")
    for rank, (team, prob) in enumerate(list(results["semi"].items())[:8], 1):
        print(f" {rank:2d}º  {team:<15} : {prob:5.2f}%")

    # Exportação opcional para auditoria de dados (Via flag --csv)
    if "--csv" in sys.argv:
        os.makedirs("output", exist_ok=True)
        rows = [
            {"stage": stage, "team": team, "prob_pct": prob}
            for stage in results
            for team, prob in results[stage].items()
        ]
        pd.DataFrame(rows).to_csv("output/relatorio_final_copa2026.csv", index=False)
        print("\n📁 Dados completos gravados em: output/relatorio_final_copa2026.csv")