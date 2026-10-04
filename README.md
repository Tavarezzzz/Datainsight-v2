📊 DataInsight
<p align="center"> <strong>Transformando dados brutos em análises, visualizações e insights inteligentes.</strong> </p> <p align="center"> <img src="https://img.shields.io/badge/Python-141414?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/Streamlit-141414?style=for-the-badge&logo=streamlit&logoColor=white"> <img src="https://img.shields.io/badge/Pandas-141414?style=for-the-badge&logo=pandas&logoColor=white"> <img src="https://img.shields.io/badge/Plotly-141414?style=for-the-badge&logo=plotly&logoColor=white"> <img src="https://img.shields.io/badge/Google_Gemini-141414?style=for-the-badge&logo=googlegemini&logoColor=white"> </p> <p align="center"> <br>Dashboard interativo para exploração, análise e interpretação de dados. </p>

---

# 📌 Sobre o projeto

O DataInsight é uma plataforma de análise de dados desenvolvida em Python e Streamlit, criada para transformar diferentes conjuntos de dados em informações mais fáceis de explorar e interpretar.

A aplicação permite carregar arquivos, aplicar filtros, analisar a qualidade dos dados, construir visualizações interativas e utilizar um assistente baseado em Inteligência Artificial para auxiliar na interpretação da base.

A proposta é reunir em uma única interface etapas comuns do processo de análise exploratória, reduzindo o trabalho manual necessário para compreender inicialmente um dataset.

---

# 🎯 O problema

A análise inicial de uma base de dados normalmente exige várias etapas diferentes.

Antes de conseguir extrair informações relevantes, o analista precisa:

Carregar os dados;
Verificar a estrutura da base;
Identificar colunas e tipos de dados;
Encontrar valores ausentes;
Identificar registros duplicados;
Aplicar filtros;
Criar visualizações;
Calcular métricas;
Interpretar os resultados.

Quando essas etapas são realizadas manualmente para diferentes datasets, o processo pode se tornar repetitivo e demorado.

O DataInsight busca centralizar essas etapas em uma única aplicação.


---

# 💡 A solução

O DataInsight combina Análise de Dados + Visualização + Qualidade de Dados + Inteligência Artificial em uma única interface.

--- 

# 📥 Importação

Permite carregar diferentes formatos de arquivos diretamente no dashboard.

---

# 🧹 Preparação

Os dados são carregados e preparados para exploração dentro da aplicação.

---

# 🔎 Exploração

Filtros e métricas permitem investigar diferentes partes da base.

---

# 📊 Visualização

Gráficos interativos facilitam a identificação de padrões e comportamentos nos dados.

---

# 🧠 Inteligência Artificial

O assistente integrado ao Google Gemini permite realizar perguntas sobre o dataset.

---

# 📤 Exportação

Os dados podem ser exportados após a análise em formatos como CSV e Excel.

---

# 🔄 Fluxo da aplicação
              📁 Dataset
                  │
                  ▼
          📥 Importação dos dados
                  │
                  ▼
          🧹 Preparação da base
                  │
          ┌───────┴────────┐
          ▼                ▼
      🔎 Filtros       📊 Qualidade
          │                │
          └───────┬────────┘
                  ▼
          📈 Visualizações
                  │
                  ▼
          🧠 Assistente IA
                  │
                  ▼
            📤 Exportação

---

# 📂 Entrada de dados

O DataInsight foi desenvolvido para trabalhar com diferentes formatos de arquivos.

Formatos suportados
CSV
XLSX
XLS
Parquet

Após o upload, a aplicação disponibiliza os dados para exploração diretamente no dashboard.

---

# 📊 Análise dos dados

A aplicação apresenta uma visão inicial da estrutura do dataset.

Entre as informações analisadas estão:

Quantidade de registros;
Quantidade de colunas;
Valores ausentes;
Registros duplicados;
Colunas disponíveis;
Variáveis numéricas;
Variáveis categóricas.

Essa etapa permite identificar rapidamente características importantes da base antes de iniciar uma análise mais aprofundada.

---

# 🔎 Filtros dinâmicos

Os filtros são construídos de acordo com as informações disponíveis no dataset.

O usuário pode selecionar valores de diferentes colunas categóricas para restringir a análise aos registros desejados.

Isso permite explorar diferentes segmentos da base sem precisar modificar o arquivo original.

--- 

# 📈 Visualizações

O DataInsight utiliza Plotly para gerar visualizações interativas.

Entre os gráficos disponíveis estão:

📊 Gráfico de barras;
🥧 Gráfico de pizza;
📈 Gráfico de linhas;
📦 Box Plot;
📊 Histograma;
📉 Violin Plot.

Além disso, o usuário pode selecionar operações como:

Soma;
Média;
Contagem.

A proposta é permitir que o usuário explore diferentes perspectivas do mesmo conjunto de dados.

---

# 🧠 Inteligência Artificial

Uma das funcionalidades do DataInsight é a integração com o Google Gemini.

O assistente permite que o usuário faça perguntas relacionadas à estrutura e ao conteúdo analítico da base carregada.

O contexto enviado para o modelo inclui informações como:

Quantidade de registros;
Quantidade de colunas;
Nome das colunas;
Pergunta realizada pelo usuário.
Exemplo
"Quais informações posso analisar nesta base?"

A Inteligência Artificial atua como uma camada de apoio à interpretação dos dados, complementando as visualizações e indicadores apresentados pelo dashboard.

--- 

# 🧪 Qualidade dos dados

A qualidade dos dados é uma etapa importante antes de qualquer análise.

O DataInsight disponibiliza indicadores para auxiliar na identificação de problemas como:

Valores ausentes;
Registros duplicados;
Estrutura da base;
Quantidade de registros;
Quantidade de variáveis.

Essas informações ajudam o usuário a compreender as condições do dataset antes de tirar conclusões sobre os dados.

---

# 📤 Exportação

Após realizar a exploração, o usuário pode exportar os dados diretamente pela aplicação.

Formatos disponíveis
CSV
Excel

Isso permite utilizar os resultados em outras ferramentas e etapas do processo analítico.

---

# 🔐 Autenticação

O DataInsight possui um sistema de autenticação para controlar o acesso à aplicação.

As credenciais são armazenadas utilizando o sistema de Secrets do Streamlit, evitando que informações sensíveis sejam inseridas diretamente no código.

A aplicação utiliza:

Hash SHA-256 para senhas;
hmac.compare_digest para comparação;
secrets.toml para armazenamento local das credenciais;
.gitignore para evitar o versionamento de informações sensíveis.
🏗️ Arquitetura
                    ┌─────────────────┐
                    │      Usuário    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Streamlit    │
                    │    Dashboard    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         📥 Upload       🔎 Filtros     🧪 Qualidade
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
                    │     Pandas      │
                    │  Processamento  │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
       📊 Plotly                    🧠 Google Gemini
       Visualização                    Assistente

---

🛠️ Tecnologias
Tecnologia	Utilização
Python	Desenvolvimento da aplicação
Streamlit	Interface e dashboard
Pandas	Manipulação dos dados
NumPy	Operações numéricas
Plotly	Visualizações interativas
Google Gemini	Assistente de Inteligência Artificial
OpenPyXL	Manipulação de arquivos Excel
uv	Gerenciamento do ambiente e dependências
Git / GitHub	Versionamento
📁 Estrutura do projeto
Datainsight-v2/
│
├── .streamlit/
│   └── secrets.toml
│
├── app_v2.py
├── utils.py
├── requirements.txt
├── guia_implementacao.md
├── README.md
├── .gitignore
│
└── ...
Principais arquivos
app_v2.py — aplicação principal;
utils.py — funções auxiliares;
requirements.txt — dependências;
guia_implementacao.md — documentação complementar;
.streamlit/secrets.toml — credenciais e chaves locais.

---

# 🚀 Como executar
1. Clone o repositório
git clone https://github.com/Tavarezzzz/Datainsight-v2.git
2. Acesse a pasta
cd Datainsight-v2
3. Crie o ambiente virtual
uv venv --python 3.12
4. Ative o ambiente
.venv\Scripts\activate
5. Instale as dependências
uv pip install -r requirements.txt
6. Configure os Secrets

Crie:

.streamlit/secrets.toml

E configure suas credenciais:

LOGIN_USERNAME = "admin"
LOGIN_PASSWORD_HASH = "SEU_HASH"
GEMINI_API_KEY = "SUA_CHAVE"
7. Execute
uv run streamlit run app_v2.py

---

# 🔒 Segurança

Para manter o projeto seguro:

Não versione o secrets.toml;
Não coloque chaves de API diretamente no código;
Não publique senhas;
Não envie dados privados para o GitHub;
Utilize o .gitignore para arquivos sensíveis.

---
# 🗺️ Roadmap
 Upload de arquivos CSV
 Upload de arquivos Excel
 Upload de arquivos Parquet
 Filtros dinâmicos
 Indicadores de qualidade
 Visualizações interativas
 Exportação CSV
 Exportação Excel
 Autenticação
 Integração com Google Gemini
 Detecção automática de anomalias
 Análise automática de correlações
 Identificação automática de outliers
 Recomendação inteligente de gráficos
 Perfilamento automático de datasets
 Integração com bancos de dados
 Testes automatizados
 CI/CD
 Arquitetura modular
 Observabilidade

---

# 🎓 Objetivo do projeto

O DataInsight também funciona como um projeto prático para aplicação de conceitos de:

Engenharia de Dados • Data Analytics • Python • Visualização de Dados • Inteligência Artificial

A construção da plataforma busca aplicar esses conceitos em uma aplicação funcional, aproximando o desenvolvimento acadêmico de problemas encontrados em ambientes reais de análise de dados.

---

# 👨‍💻 Autor
<p align="center">
Leandro Tavarez
  
Engenharia de Dados • Data Analytics • Inteligência Artificial
<p align="center">
