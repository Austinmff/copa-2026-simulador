# 🏆 Simulador Probabilístico - Copa do Mundo FIFA 2026

Este é um ecossistema modular de simulação estocástica para a Copa do Mundo de 2026. O motor combina a força histórica das seleções (**Modelagem de Rating Elo**) com a volatilidade de gols por partida (**Distribuição de Poisson**), aplicando penalidades dinâmicas de fadiga com base na profundidade do plantel.

---

## 🛠️ Tecnologias e Arquitetura

O projeto foi totalmente reestruturado seguindo boas práticas de engenharia de software (**Clean Code**, separação de conceitos e alta performance):

- **Motor Vetorizado:** Implementado com **NumPy** para simulações massivas em milissegundos, eliminando loops pesados em Python.
- **Dados Isolados:** Configurações de grupos e atributos das seleções externalizados em arquivos `.json` na pasta `data/`.
- **Interface Gráfica:** Painel dinâmico construído em **Streamlit** e gráficos interativos via **Plotly**.
- **Garantia de Qualidade:** Suíte de testes unitários automatizados com **Pytest**.
- **Esteira de CI:** Integração contínua via **GitHub Actions** (`ci.yml`) validando o código a cada push.

---

## 📁 Estrutura do Repositório

```text
├── .github/
│   └── workflows/          # Automação de CI (GitHub Actions)
├── data/                   # Arquivos de dados estáticos (JSON)
├── tests/                  # Suíte de testes unitários (Pytest)
├── worldcup/               # Pacote lógico encapsulado (Motor e Loader)
├── app.py                  # Interface gráfica (Streamlit View)
├── simulate.py             # Orquestrador CLI (Simulação de Monte Carlo)
└── requirements.txt        # Gerenciador de dependências
```

---

## 🚀 Como Executar o Projeto

### 1. Clonar o Repositório e Instalar Dependências

```bash
# Instalar as bibliotecas necessárias
pip install -r requirements.txt
```

### 2. Executar a Simulação em Larga Escala (CLI)

Para rodar **100.000 simulações** via terminal e exportar o relatório estatístico para auditoria:

```bash
python simulate.py --csv
```

### 3. Iniciar o Painel Interativo (Web)

Para abrir o painel gráfico no seu navegador:

```bash
streamlit run app.py
```

### 4. Rodar os Testes Unitários

Para validar os critérios e restrições matemáticas do motor:

```bash
pytest
```