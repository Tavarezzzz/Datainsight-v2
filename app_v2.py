import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
from io import BytesIO
from datetime import datetime
import warnings

# --- CONFIGURAÇÃO DA PÁGINA ---
warnings.filterwarnings('ignore')
st.set_page_config(
    page_title="Data Insight",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTADO DE SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "chat" not in st.session_state:
    st.session_state.chat = []
if "df_global" not in st.session_state:
    st.session_state.df_global = None

# --- FORMATADORES ---
fmt_moeda = lambda x: f"R$ {x:,.2f}"
fmt_num = lambda x: f"{x:,}"

# --- FUNÇÃO DE LOGIN ---
def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>Login Data Insight</h1>", unsafe_allow_html=True)
        usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        
        if st.button("Entrar", use_container_width=True):
            if usuario == "admin" and senha == "1234":
                st.session_state.logado = True
                st.session_state.is_admin = True
                st.rerun()
            elif usuario and senha:
                st.session_state.logado = True
                st.session_state.is_admin = False
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

# --- BLOQUEIO DE ACESSO ---
if not st.session_state.logado:
    tela_login()
    st.stop()

# --- FUNÇÃO DE AUXÍLIO PARA IA ---
def resumo_contexto(df_filtrado):
    receita_total = df_filtrado["Receita Total (receita bruta)"].sum()
    lucro_total = df_filtrado["Lucro Líquido"].sum()
    return f"Contexto Atual: Receita Total R$ {receita_total:,.2f}, Lucro Líquido R$ {lucro_total:,.2f}."

# ============ DASHBOARD PRINCIPAL ============

# Header e Botão Sair
col_t1, col_t2 = st.columns([8, 1])
with col_t1:
    status = "MODO ADMIN" if st.session_state.is_admin else "MODO USUÁRIO"
    st.title(f"Dashboard Financeiro - {status}")
with col_t2:
    if st.button("Sair", use_container_width=True):
        st.session_state.logado = False
        st.session_state.df_global = None
        st.rerun()

# Sidebar - Upload de Dados
st.sidebar.header("Base de Dados")
arquivo_carregado = st.sidebar.file_uploader("Suba seu CSV ou Excel", type=["csv", "xlsx"])

if arquivo_carregado:
    try:
        if arquivo_carregado.name.endswith('.csv'):
            df_input = pd.read_csv(arquivo_carregado)
        else:
            df_input = pd.read_excel(arquivo_carregado)
        st.session_state.df_global = df_input
    except Exception as e:
        st.sidebar.error(f"Erro ao ler arquivo: {e}")

# Verifica se existem dados carregados
if st.session_state.df_global is None:
    st.info("Bem-vindo! Por favor, carregue um arquivo na barra lateral para começar a análise.")
    st.stop()

df = st.session_state.df_global.copy()

# Sidebar - Filtros Dinâmicos
st.sidebar.header("Filtros")
lista_empresas = ["Todas"] + sorted(df["Empresa"].unique().tolist())
empresa_selecionada = st.sidebar.selectbox("Selecionar Empresa", lista_empresas)

df_filtrado = df.copy()
if empresa_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Empresa"] == empresa_selecionada]

# --- CHATBOT IA (ASSISTENTE) ---
with st.expander("Perguntar ao Assistente IA", expanded=False):
    pergunta = st.text_area("O que você deseja saber sobre esses dados?")
    if st.button("Enviar Pergunta"):
        if pergunta:
            try:
                # Substitua pela sua chave ou configure no Streamlit Secrets
                api_key = st.secrets.get("GEMINI_API_KEY", "SUA_CHAVE_AQUI")
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash")
                contexto = resumo_contexto(df_filtrado)
                prompt = f"Dados: {contexto}. Pergunta: {pergunta}"
                response = model.generate_content(prompt)
                st.session_state.chat.insert(0, ("IA", response.text))
                st.session_state.chat.insert(0, ("Você", pergunta))
            except Exception as e:
                st.error("Erro na API do Gemini. Verifique sua chave.")
    
    for autor, msg in st.session_state.chat:
        st.write(f"**{autor}:** {msg}")

# --- ABAS DE CONTEÚDO ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Visão Geral", "Gráficos", "Dados Brutos", "Exportar", "Previsão"])

with tab1:
    st.subheader("Indicadores Principais (KPIs)")
    c1, c2, c3 = st.columns(3)
    rec_val = df_filtrado["Receita Total (receita bruta)"].sum()
    luc_val = df_filtrado["Lucro Líquido"].sum()
    opex_val = df_filtrado["Custo Operacional (OPEX)"].sum()
    
    c1.metric("Receita Total", fmt_moeda(rec_val))
    c2.metric("Lucro Líquido", fmt_moeda(luc_val))
    c3.metric("Custos (OPEX)", fmt_moeda(opex_val))

with tab2:
    st.subheader("Análise Temporal e Setorial")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_rec = px.bar(df_filtrado, x="Ano", y="Receita Total (receita bruta)", color="Empresa", title="Receita por Ano")
        st.plotly_chart(fig_rec, use_container_width=True)
    with col_g2:
        fig_setor = px.pie(df_filtrado, names="Setor", values="Receita Total (receita bruta)", title="Distribuição por Setor")
        st.plotly_chart(fig_setor, use_container_width=True)

with tab3:
    st.dataframe(df_filtrado, use_container_width=True)

with tab4:
    st.subheader("Gerar Relatório")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Análise')
    st.download_button(
        label="Baixar Dados em Excel",
        data=output.getvalue(),
        file_name=f"relatorio_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with tab5:
    st.subheader("Projeção Estatística para o Próximo Ano")
    df_agrupado = df_filtrado.groupby("Ano")["Receita Total (receita bruta)"].sum().reset_index()
    
    if len(df_agrupado) > 1:
        x = df_agrupado["Ano"].values
        y = df_agrupado["Receita Total (receita bruta)"].values
        
        # Regressão Linear Simples
        coef = np.polyfit(x, y, 1)
        proximo_ano = int(x.max() + 1)
        previsao = coef[0] * proximo_ano + coef[1]
        
        c_pred1, c_pred2 = st.columns(2)
        c_pred1.metric(f"Projeção Receita {proximo_ano}", fmt_moeda(previsao))
        c_pred2.write("A previsão é baseada na tendência histórica (Regressão Linear).")
        
        # Gráfico de Tendência
        df_projecao = pd.concat([df_agrupado, pd.DataFrame({"Ano": [proximo_ano], "Receita Total (receita bruta)": [previsao]})])
        fig_proj = px.line(df_projecao, x="Ano", y="Receita Total (receita bruta)", title="Linha de Tendência", markers=True)
        fig_proj.add_scatter(x=[proximo_ano], y=[previsao], mode='markers', marker=dict(size=12, color='red'), name="Previsão")
        st.plotly_chart(fig_proj, use_container_width=True)
    else:
        st.warning("! Dados históricos insuficientes (mínimo 2 anos) para calcular a tendência.")

# --- FOOTER ---
st.markdown("---")
st.caption(f"Data Insight | {datetime.now().year} | Criado para Análise Multi-Empresa")