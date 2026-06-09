# 🏆 Simulador Preditivo Inteligente — Copa do Mundo FIFA 2026

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit)
![Numpy](https://img.shields.io/badge/Numpy-Data-013243?style=for-the-badge&logo=numpy)
![Plotly](https://img.shields.io/badge/Plotly-Graphics-3F4F75?style=for-the-badge&logo=plotly)

Este repositório contém um ecossistema robusto de **Ciência de Dados e Analytics** voltado para a previsão probabilística e simulação estocástica de cenários da Copa do Mundo de 2026. O projeto combina modelos estatísticos consagrados no mercado com uma interface gráfica interativa (dashboard nativo) para traduzir distribuições matemáticas complexas em insights de fácil compreensão.

---

## 📊 O Projeto e Seus Diferenciais

Ao contrário de palpites e análises puramente subjetivas, este sistema adota uma abordagem estritamente quantitativa baseada em dados históricos e de mercado atualizados (maio/junho de 2026). O motor preditivo realiza simulações considerando cinco camadas independentes de fatores:

1. **Força Relativa (Ranking Elo Calibrado):** A métrica base de força histórica e momento de cada uma das 48 seleções.
2. **Poder de Ataque (Média de Gols Esperados - xG):** Capacidade intrínseca da equipe de gerar volume e ocasiões de gol.
3. **Solidez Defensiva (Fator de Bloqueio):** Coeficiente de resistência à criação de jogadas do adversário (quanto menor o número, mais intransitável é a defesa).
4. **Fadiga Dinâmica Estocástica:** Desgaste físico incremental calculado em tempo real a cada fase avançada (Oitavas, Quartas, Semis e Final).
5. **Índice de Volatilidade (Grau de Instabilidade):** Modelagem de ruído estatístico para simular flutuações táticas, capturando o risco de cenários reais de "zebra" (upsets).

### 🩹 Análise de Sensibilidade (Desfalques e Lesões)
O grande diferencial de negócios do modelo é a capacidade de reavaliar o favoritismo com base em dados dinâmicos de junho de 2026. Ele projeta os impactos táticos causados por desfalques médicos de peso confirmados antes do início do torneio (como a ausência de **Rodrygo** e **Wesley** no Brasil, ou de **Serge Gnabry** na Alemanha). O algoritmo reduz a nota de profundidade de elenco destas seleções, punindo o rendimento físico delas à medida que se aproximam da grande final.

---

## 🛠️ Arquitetura e Estrutura do Repositório

O projeto foi modularizado seguindo padrões rígidos de engenharia de software, garantindo o desacoplamento entre dados, motor matemático e camada visual:

* **`groups_odds.py`**: Contém o chaveamento e a distribuição oficial dos 12 grupos da Copa (48 seleções), além das probabilidades implícitas brutas extraídas das principais bolsas de apostas e mercados preditivos globais (Polymarket, bookmakers UK).
* **`teams_data.py`**: Banco de dados técnico que indexa as variáveis quantitativas e os coeficientes de performance de cada país (Ataque, Defesa, Elo, Volatilidade e *Squad Depth*).
* **`simulate.py`**: O motor matemático central em Python puro. É responsável por rodar testes estocásticos em lote via terminal, validando a estabilidade macro do modelo.
* **`app.py`**: A interface gráfica e interativa desenvolvida com **Streamlit** e **Plotly Express**. Transforma matrizes numéricas em gráficos de barras dinâmicos, tabelas interativas e permite simulações customizadas de confrontos diretos na hora.
* **`Projeto Analítico_ Probabilidades da Copa do Mundo FIFA 2026.pdf`**: Documento de fundamentação de negócios com o escopo, suposições metodológicas e limites analíticos do projeto.

---

## 🧠 Detalhes da Metodologia Estatística

A inteligência analítica do simulador está amparada em três pilares matemáticos fundamentais:

### 1. Distribuição de Poisson Bivariada
O número de gols marcados em uma partida de futebol não segue uma distribuição normal clássica. Utilizamos a distribuição de Poisson para calcular as probabilidades de placares. O parâmetro $\lambda$ (gols esperados) de cada time é obtido cruzando o coeficiente de ataque do Time A com o coeficiente de defesa do Time B, ponderado pela diferença de ranking Elo entre os dois.

### 2. Modelo de Penalização por Fadiga
A energia gasta por uma seleção é modelada de forma cumulativa com base na seguinte equação:
$$\text{Fadiga} = \text{Modificador da Fase} \times (10.0 - \text{Profundidade de Elenco}) \times 5$$
Este valor deduz pontos do Elo efetivo da equipe antes de entrar em campo. Seleções com banco de reservas limitado sofrem severamente nas fases avançadas contra equipes de alta rotação de elenco.

### 3. Simulação de Monte Carlo
Como o futebol envolve eventos altamente aleatórios, o campeonato inteiro é simulado **10.000 vezes** (ou mais). Pela Lei dos Grandes Números, a consolidação dessas milhares de repetições gera uma convergência estatística estável, revelando a probabilidade real de cada seleção atingir cada fase do torneio.

---

## 🚀 Como Executar o Projeto Localmente

Siga o passo a passo abaixo para rodar a aplicação em qualquer ambiente Windows (comandos otimizados para evitar conflitos de variáveis de ambiente do sistema):

### 1. Clonar o Repositório e Acessar a Pasta
```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio
2. Instalar as Dependências Requeridas
Instale os pacotes de computação científica, manipulação de dados e renderização gráfica via Python executando:

Bash
py -m pip install streamlit plotly numpy pandas
3. Executar o Dashboard Interativo
Para ligar o servidor local e abrir automaticamente a interface gráfica customizada no seu navegador de internet padrão, digite o comando:

Bash
py -m streamlit run app.py
🖥️ Funcionalidades do Dashboard Visual
Ao abrir a aplicação, você terá acesso a um painel analítico dividido em três grandes módulos focados em experiência do usuário (UX):

📊 Probabilidades Completas: Gráficos interativos ordenando os maiores favoritos e tabelas que destrincham as chances de sucesso de cada equipe de avançar em cada fase do funil da FIFA.

🩹 Desfalques & Lesões: Um painel detalhado de análise de impacto médico, mostrando graficamente como as perdas de jogadores importantes alteram as chances de título da equipe a longo prazo.

⚔️ Simulador de Jogo Único: Uma arena interativa onde você escolhe duas seleções quaisquer e o sistema roda, em tempo real, 1.000 partidas isoladas entre elas para simular quem avançaria num cenário hipotético de mata-mata.