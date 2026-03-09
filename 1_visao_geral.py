import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# --- CONFIG GERAL ---
st.set_page_config(page_title="MC SONAE - Análise de Empresas", layout="wide")

# --- ESTADO DE SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "chat" not in st.session_state:
    st.session_state.chat = []

# --- FUNÇÃO DE LOGIN ---
def tela_login():
    st.title("Login de Acesso")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario.strip() == "" or senha.strip() == "":
            st.error("Preencha usuário e senha antes de entrar.")
            return
        if usuario == "admin" and senha == "1234":
            st.session_state.logado = True
            st.session_state.is_admin = True
        else:
            st.session_state.logado = True
            st.session_state.is_admin = False
        st.success(f"Bem-vindo, {usuario}!")
        st.rerun()

# --- BLOQUEIO DE LOGIN ---
if not st.session_state.logado:
    tela_login()
    st.stop()

# --- DASHBOARD ---
st.title("Dashboard Financeiro - MC SONAE")

# --- BOTÃO SAIR ---
col1, col2 = st.columns([8, 1])
with col2:
    if st.button("Sair", use_container_width=True):
        st.session_state.logado = False
        st.session_state.is_admin = False
        st.session_state.chat = []
        st.rerun()

# --- ADMIN OU USUÁRIO ---
if st.session_state.is_admin:
    st.sidebar.success("Modo Administrador")
else:
    st.sidebar.info("Modo Usuário")

# --- LER CSV COM CACHE ---
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("saida/empresas_2_tratado.csv")
        df["Ano"] = pd.to_numeric(df["Ano"])
        return df
    except FileNotFoundError:
        st.error("Arquivo 'empresas_2_tratado.csv' não encontrado.")
        return pd.DataFrame()

df = carregar_dados()
if df.empty:
    st.stop()

# --- FUNÇÃO PARA RESUMO DO CONTEXTO (IA) ---

# --- FUNÇÃO PARA RESUMO DO CONTEXTO (IA) - VERSÃO COMPLETA (Empresa, Setor, País, Ano) ---
def resumo_contexto(df_filtrado):
    # 1. Cabeçalho com os totais do que está na tela agora
    receita_atual = df_filtrado["Receita Total (receita bruta)"].sum()
    lucro_atual = df_filtrado["Lucro Líquido"].sum()
    
    resumo = f"Resumo Geral dos Dados Filtrados:\n"
    resumo += f"Receita Total acumulada: R$ {receita_atual:,.2f}\n"
    resumo += f"Lucro Líquido acumulado: R$ {lucro_atual:,.2f}\n\n"

    # 2. Detalhamento linha a linha
    # Agrupamos por TODAS as colunas importantes
    dados_completo = df_filtrado.groupby(["Empresa", "Setor", "País", "Ano"])[
        ["Receita Total (receita bruta)", "Lucro Líquido"] # Puxei o Lucro também para a IA ficar mais inteligente
    ].sum().reset_index()
    
    # Ordenar por Receita (para as mais importantes aparecerem primeiro)
    dados_completo = dados_completo.sort_values(by="Receita Total (receita bruta)", ascending=False)
    
    resumo += "Dados detalhados (Linha a linha):\n"
    for index, row in dados_completo.iterrows():
        # Montamos a "frase" que a IA vai ler
        resumo += (
            f"- Empresa: {row['Empresa']} | "
            f"Setor: {row['Setor']} | "
            f"País: {row['País']} | "
            f"Ano: {row['Ano']} | "
            f"Receita: R$ {row['Receita Total (receita bruta)']:,.2f} | "
            f"Lucro: R$ {row['Lucro Líquido']:,.2f}\n"
        )
    
    return resumo

# --- CHAT GEMINI (NO TOPO) ---
with st.expander("Assistente do Dashboard (IA)", expanded=True):
    pergunta = st.text_area("Digite sua pergunta sobre os dados do dashboard:")

    if st.button("Perguntar", key="btn_gpt_expander"):
        if pergunta.strip() == "":
            st.warning("Digite uma pergunta antes!")
        else:
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                modelo = genai.GenerativeModel("gemini-2.0-flash")
                contexto = resumo_contexto(df)  
                prompt = f"""
                Você é um assistente especializado no dashboard financeiro.
                Baseie suas respostas nos dados abaixo e explique de forma clara, simples e objetiva:
                {contexto}

                Pergunta do usuário: {pergunta}
                """
                resposta = modelo.generate_content(prompt)
                st.session_state.chat = [
                        ("Usuário", pergunta),
                        ("IA", resposta.text)
                ]
            except Exception as e:
                st.error("Erro ao conectar ao Gemini.")
                st.error(str(e))

    # Mostrar histórico do chat
    for quem, msg in st.session_state.chat:
        st.markdown(f"**{quem}:** {msg}")

# --- FILTROS ---
st.sidebar.header("Filtros")
empresa = st.sidebar.selectbox("Selecione a empresa", ["Todas"] + sorted(df["Empresa"].unique()))
ano = st.sidebar.multiselect("Selecione o(s) ano(s)", sorted(df["Ano"].unique()))
setor = st.sidebar.multiselect("Selecione o(s) setor(es)", sorted(df["Setor"].unique()))
pais = st.sidebar.multiselect("Selecione o(s) país(es)", sorted(df["País"].unique()))
filial = []
if "Filial" in df.columns:
    filial = st.sidebar.multiselect("Selecione a(s) filial(ais)", sorted(df["Filial"].unique()))

# --- UPLOAD CSV ---
st.sidebar.header("Atualizar Dataset")
arquivo_csv = st.sidebar.file_uploader("Enviar novo arquivo CSV", type=["csv"])
if arquivo_csv is not None:
    try:
        df = pd.read_csv(arquivo_csv)
        st.sidebar.success("Novo dataset carregado!")
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar o CSV: {e}")

# --- APLICA FILTROS ---
df_filtrado = df.copy()
if empresa != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Empresa"] == empresa]
if ano:
    df_filtrado = df_filtrado[df_filtrado["Ano"].isin(ano)]
if setor:
    df_filtrado = df_filtrado[df_filtrado["Setor"].isin(setor)]
if pais:
    df_filtrado = df_filtrado[df_filtrado["País"].isin(pais)]
if filial:
    df_filtrado = df_filtrado[df_filtrado["Filial"].isin(filial)]

# --- FORMATOS ---
fmt_moeda = lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
fmt_num = lambda x: f"{x:,}".replace(",", ".")
fmt_perc = lambda x: f"{x:.2%}"
def calcular_delta(atual, anterior):
    if pd.isna(atual) or pd.isna(anterior) or anterior == 0:
        return 0.0
    delta = (atual - anterior) / abs(anterior)
    return max(min(delta, 1), -1)

# --- ANO ANTERIOR PARA COMPARAÇÃO ---
df_ano_anterior = pd.DataFrame(columns=df.columns)
if ano:
    ano_atual = max(ano)
    anos_disponiveis = sorted(df["Ano"].unique())
    anos_anteriores = [a for a in anos_disponiveis if a < ano_atual]
    if anos_anteriores:
        ano_comp = max(anos_anteriores)
        df_ano_anterior = df[df["Ano"] == ano_comp]
        if empresa != "Todas":
            df_ano_anterior = df_ano_anterior[df_ano_anterior["Empresa"] == empresa]
        if setor:
            df_ano_anterior = df_ano_anterior[df_ano_anterior["Setor"].isin(setor)]
        if pais:
            df_ano_anterior = df_ano_anterior[df_ano_anterior["País"].isin(pais)]
        if filial:
            df_ano_anterior = df_ano_anterior[df_ano_anterior["Filial"].isin(filial)]

# --- CÁLCULOS DOS KPIs ---
receita_atual = df_filtrado["Receita Total (receita bruta)"].sum()
lucro_atual = df_filtrado["Lucro Líquido"].sum()
opex_atual = df_filtrado["Custo Operacional (OPEX)"].sum()
func_atual = df_filtrado["Número de Funcionários"].sum()
receita_ant = df_ano_anterior["Receita Total (receita bruta)"].sum()
lucro_ant = df_ano_anterior["Lucro Líquido"].sum()
opex_ant = df_ano_anterior["Custo Operacional (OPEX)"].sum()
func_ant = df_ano_anterior["Número de Funcionários"].sum()

# --- KPIs VISUALIZAÇÃO ---
kpi_tab1, kpi_tab2 = st.tabs(["Visão Geral (KPIs)", "Métricas de Eficiência (Rácios)"])
with kpi_tab1:
    st.subheader("Visão Geral")
    col1, col2, col3, col4 = st.columns(4)
    delta_receita = calcular_delta(receita_atual, receita_ant)
    delta_lucro = calcular_delta(lucro_atual, lucro_ant)
    delta_opex = calcular_delta(opex_atual, opex_ant)
    delta_func = calcular_delta(func_atual, func_ant)
    col1.metric("Receita Total", fmt_moeda(receita_atual), delta=f"{delta_receita:.2%}" if ano else None)
    col2.metric("Lucro Líquido", fmt_moeda(lucro_atual), delta=f"{delta_lucro:.2%}" if ano else None)
    col3.metric("Custo Operacional (OPEX)", fmt_moeda(opex_atual), delta=f"{delta_opex:.2%}" if ano else None, delta_color="inverse")
    col4.metric("Total de Funcionários", fmt_num(func_atual), delta=f"{delta_func:.2%}" if ano else None)
with kpi_tab2:
    st.subheader("Métricas de Eficiência")
    col5, col6, col7 = st.columns(3)
    if receita_atual > 0:
        margem_atual = lucro_atual / receita_atual
        margem_ant = (lucro_ant / receita_ant) if receita_ant > 0 else 0
        col5.metric("Margem Líquida", fmt_perc(margem_atual), delta=f"{(margem_atual - margem_ant) * 100:.2f} p.p." if ano else None)
    else:
        col5.metric("Margem Líquida", "N/A")
    if func_atual > 0:
        rpf_atual = receita_atual / func_atual
        rpf_ant = (receita_ant / func_ant) if func_ant > 0 else 0
        col6.metric("Receita / Funcionário", fmt_moeda(rpf_atual), delta=f"{calcular_delta(rpf_atual, rpf_ant):.2%}" if ano else None)
    else:
        col6.metric("Receita / Funcionário", "N/A")
    if func_atual > 0:
        cpf_atual = opex_atual / func_atual
        cpf_ant = (opex_ant / func_ant) if func_ant > 0 else 0
        col7.metric("Custo / Funcionário", fmt_moeda(cpf_atual), delta=f"{calcular_delta(cpf_atual, cpf_ant):.2%}" if ano else None, delta_color="inverse")
    else:
        col7.metric("Custo / Funcionário", "N/A")

# --- GRÁFICOS ---
st.divider()
st.subheader("Análises Gráficas")
tab1, tab2, tab3, tab4 = st.tabs(["Receita por Ano", "Receita por Setor", "Top #5 Empresas", "Lucro por País"])
with tab1:
    receita_ano = df_filtrado.groupby("Ano", as_index=False)["Receita Total (receita bruta)"].sum()
    fig = px.bar(receita_ano, x="Ano", y="Receita Total (receita bruta)", title="Receita Total por Ano", color="Ano", text_auto=".2s")
    fig.update_layout(xaxis_title=None, yaxis_title="Receita (R$)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with tab2:
    receita_setor = df_filtrado.groupby("Setor", as_index=False)["Receita Total (receita bruta)"].sum()
    fig = px.bar(receita_setor, x="Setor", y="Receita Total (receita bruta)", title="Receita Total por Setor", color="Setor", text_auto=".2s")
    fig.update_layout(xaxis_title=None, yaxis_title="Receita (R$)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with tab3:
    top5 = df_filtrado.groupby("Empresa")["Receita Total (receita bruta)"].sum().nlargest(5).reset_index()
    fig = px.bar(top5, y="Empresa", x="Receita Total (receita bruta)", orientation="h", title="Top 5 Empresas por Receita", color="Empresa", text_auto=".2s")
    fig.update_layout(xaxis_title="Receita (R$)", yaxis_title=None, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with tab4:
    lucro_pais = df_filtrado.groupby("País", as_index=False)["Lucro Líquido"].sum()
    fig = px.bar(lucro_pais, x="País", y="Lucro Líquido", title="Lucro Líquido por País", color="País", text_auto=".2s")
    fig.update_layout(xaxis_title=None, yaxis_title="Lucro (R$)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# --- TABELA ---
st.divider()
if st.checkbox("Mostrar Dados Brutos (Tabela)"):
    st.dataframe(df_filtrado, use_container_width=True)
