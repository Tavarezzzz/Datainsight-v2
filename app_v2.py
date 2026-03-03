import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="DataInsight - Análise Automática de Dados",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM STYLING ============
st.markdown("""
    <style>
    * {
        margin: 0;
        padding: 0;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 800;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .section-title {
        color: #667eea;
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 700;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    .info-box {
        background: #e8f4f8;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown("""
    <div class="main-header">
        <h1>📊 DataInsight</h1>
        <p>Transforme seus dados em insights automáticos - Análise inteligente para qualquer dataset</p>
    </div>
""", unsafe_allow_html=True)

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    
    uploaded_file = st.file_uploader(
        "📁 Carregue seu arquivo",
        type=['csv', 'xlsx', 'xls'],
        help="Formatos suportados: CSV, Excel (.xlsx, .xls)"
    )
    
    st.markdown("---")
    st.markdown("### 💡 Sobre")
    st.info("""
    **DataInsight** é um sistema de análise automática que:
    
    ✅ Processa qualquer tipo de dado  
    ✅ Gera gráficos relevantes automaticamente  
    ✅ Calcula métricas estatísticas  
    ✅ Exporta relatórios em Excel  
    ✅ Identifica padrões e anomalias  
    """)

# ============ MAIN LOGIC ============
if uploaded_file is not None:
    # Load data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Arquivo carregado: {uploaded_file.name}")
        
        # ============ OVERVIEW SECTION ============
        st.markdown('<h2 class="section-title">📋 Visão Geral dos Dados</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total de Linhas", f"{len(df):,}")
        with col2:
            st.metric("📈 Total de Colunas", f"{len(df.columns)}")
        with col3:
            st.metric("✓ Dados Completos", f"{100 - (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100):.1f}%")
        with col4:
            st.metric("🔤 Colunas", ", ".join([str(t).split("'")[1] for t in df.dtypes.value_counts().index]))
        
        # ============ DATA SAMPLE ============
        with st.expander("👀 Ver amostra dos dados"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Primeiras linhas:**")
                st.dataframe(df.head(10), use_container_width=True)
            with col2:
                st.write("**Tipos de dados:**")
                st.dataframe(pd.DataFrame({
                    'Coluna': df.columns,
                    'Tipo': df.dtypes,
                    'Não-nulos': df.count(),
                    'Nulos': df.isnull().sum()
                }), use_container_width=True)
        
        # ============ NUMERIC ANALYSIS ============
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            st.markdown('<h2 class="section-title">📊 Análise Numérica</h2>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Estatísticas Descritivas:**")
                st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)
            
            with col2:
                st.write("**Correlações:**")
                if len(numeric_cols) > 1:
                    corr_matrix = df[numeric_cols].corr()
                    fig = go.Figure(data=go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.columns,
                        colorscale='RdBu',
                        zmid=0,
                        text=corr_matrix.values,
                        texttemplate='%{text:.2f}',
                        textfont={"size": 10}
                    ))
                    fig.update_layout(
                        height=400,
                        margin=dict(l=100, r=0, t=20, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Necessário mais de 1 coluna numérica para calcular correlações.")
        
        # ============ AUTOMATIC CHARTS ============
        st.markdown('<h2 class="section-title">📈 Gráficos Automáticos</h2>', unsafe_allow_html=True)
        
        # Numeric columns - Distribution
        if numeric_cols:
            cols = st.columns(2)
            
            # Histograms
            with cols[0]:
                st.write("**Distribuição de Variáveis Numéricas:**")
                selected_numeric = st.selectbox(
                    "Selecione coluna numérica:",
                    numeric_cols,
                    key="histogram"
                )
                
                fig = px.histogram(
                    df, 
                    x=selected_numeric,
                    nbins=30,
                    title=f"Distribuição - {selected_numeric}",
                    labels={selected_numeric: selected_numeric},
                    color_discrete_sequence=['#667eea']
                )
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Box plot
            with cols[1]:
                st.write("**Box Plot - Detecção de Outliers:**")
                fig = go.Figure()
                for col in numeric_cols[:5]:  # Limitar a 5 para não sobrecarregar
                    fig.add_trace(go.Box(y=df[col], name=col, boxmean='sd'))
                
                fig.update_layout(
                    title="Box Plot dos Dados Numéricos",
                    height=400,
                    hovermode='y unified'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # ============ CATEGORICAL ANALYSIS ============
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if categorical_cols:
            st.markdown('<h2 class="section-title">🏷️ Análise Categórica</h2>', unsafe_allow_html=True)
            
            cols = st.columns(2)
            
            with cols[0]:
                st.write("**Distribuição de Categorias:**")
                selected_cat = st.selectbox(
                    "Selecione coluna categórica:",
                    categorical_cols,
                    key="categorical"
                )
                
                top_values = df[selected_cat].value_counts().head(10)
                fig = px.bar(
                    x=top_values.values,
                    y=top_values.index,
                    orientation='h',
                    title=f"Top 10 - {selected_cat}",
                    labels={'x': 'Frequência', 'y': selected_cat},
                    color_discrete_sequence=['#764ba2']
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with cols[1]:
                st.write("**Composição de Categorias:**")
                pie_data = df[selected_cat].value_counts().head(10)
                fig = px.pie(
                    values=pie_data.values,
                    names=pie_data.index,
                    title=f"Proporção - {selected_cat}"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # ============ CROSS-ANALYSIS ============
        st.markdown('<h2 class="section-title">🔗 Análise Cruzada</h2>', unsafe_allow_html=True)
        
        if numeric_cols and categorical_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                numeric_col = st.selectbox("Selecione coluna numérica:", numeric_cols, key="cross1")
            with col2:
                cat_col = st.selectbox("Selecione coluna categórica:", categorical_cols, key="cross2")
            
            fig = px.box(
                df,
                x=cat_col,
                y=numeric_col,
                title=f"{numeric_col} por {cat_col}",
                color=cat_col,
                points="outliers"
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # ============ EXPORT SECTION ============
        st.markdown('<h2 class="section-title">💾 Exportar Relatório</h2>', unsafe_allow_html=True)
        
        if st.button("📥 Gerar Relatório em Excel", use_container_width=True):
            buffer = BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Sheet 1: Dados originais
                df.to_excel(writer, sheet_name='Dados Originais', index=False)
                
                # Sheet 2: Estatísticas
                if numeric_cols:
                    df[numeric_cols].describe().to_excel(writer, sheet_name='Estatísticas')
                
                # Sheet 3: Resumo
                summary_data = {
                    'Métrica': [
                        'Total de Linhas',
                        'Total de Colunas',
                        'Completude (%)',
                        'Data de Análise'
                    ],
                    'Valor': [
                        len(df),
                        len(df.columns),
                        f"{100 - (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100):.2f}%",
                        datetime.now().strftime('%d/%m/%Y %H:%M')
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Resumo', index=False)
            
            buffer.seek(0)
            st.download_button(
                label="⬇️ Baixar Relatório (Excel)",
                data=buffer,
                file_name=f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.success("✅ Relatório gerado com sucesso!")
    
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")

else:
    st.markdown("""
        <div class="info-box">
            <h3>🚀 Como usar o DataInsight:</h3>
            <ol>
                <li><strong>Carregue seu arquivo:</strong> CSV, Excel (.xlsx) ou Excel (.xls)</li>
                <li><strong>Análise automática:</strong> O sistema detectará tipos de dados e gerará gráficos relevantes</li>
                <li><strong>Explore os dados:</strong> Veja distribuições, correlações e padrões</li>
                <li><strong>Exporte relatórios:</strong> Baixe análises em Excel para compartilhar</li>
            </ol>
        </div>
        
        <div style="text-align: center; margin-top: 3rem; opacity: 0.6;">
            <p><strong>Versão 2.0 - Sistema de Análise Automática de Dados</strong></p>
            <p>Desenvolvido para transformar dados em insights acionáveis</p>
        </div>
    """, unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
    <div style="text-align: center; opacity: 0.7; font-size: 0.9rem;">
        <p>📊 DataInsight v2.0 | Análise automática de dados para múltiplas empresas</p>
        <p>Built with ❤️ using Python, Streamlit & Plotly</p>
    </div>
""", unsafe_allow_html=True)