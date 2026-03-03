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
    page_title="DataInsight v2.0",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM STYLING - Dark Theme ============
st.markdown("""
    <style>
    * {
        margin: 0;
        padding: 0;
    }
    
    [data-testid="stMetric"] {
        background-color: #1a1a2e;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #00d4ff;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #ffffff;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0aec0;
        font-size: 0.9rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #00d4ff;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .metric-value {
        font-size: 2.2rem;
        color: #ffffff;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .section-title {
        color: #00d4ff;
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
        border-bottom: 2px solid #00d4ff;
        padding-bottom: 0.8rem;
    }
    
    .filter-section {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid #00d4ff;
    }
    
    .info-box {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        border-left: 4px solid #00d4ff;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# ============ SIDEBAR ============
st.sidebar.markdown("## 📊 DataInsight v2.0")
st.sidebar.markdown("---")

# Modo usuário
st.sidebar.markdown('<div class="filter-section"><h3 style="color: #00d4ff;">Modo Usuário</h3></div>', unsafe_allow_html=True)

# Upload de arquivo
uploaded_file = st.sidebar.file_uploader(
    "📁 Carregue seu arquivo CSV ou Excel",
    type=['csv', 'xlsx', 'xls'],
    help="Formatos suportados: CSV, Excel"
)

st.sidebar.markdown("---")

# Seção sobre
st.sidebar.markdown("""
    <div class="filter-section">
        <h4 style="color: #00d4ff;">ℹ️ Sobre</h4>
        <p style="font-size: 0.85rem; color: #a0aec0; margin-top: 10px;">
            DataInsight processa qualquer tipo de dado e gera análises automáticas, gráficos e relatórios em minutos.
        </p>
    </div>
""", unsafe_allow_html=True)

# ============ MAIN CONTENT ============
if uploaded_file is not None:
    try:
        # Load data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Arquivo carregado com sucesso: {uploaded_file.name}")
        
        # Get data info
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # ============ TABS ============
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "📈 Análises Gráficas", "🔍 Dados Detalhados", "💾 Exportar"])
        
        # ============ TAB 1: VISÃO GERAL ============
        with tab1:
            st.markdown('<h2 class="section-title">Visão Geral dos Dados</h2>', unsafe_allow_html=True)
            
            # KPIs principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Total de Linhas", f"{len(df):,}")
            with col2:
                st.metric("📈 Total de Colunas", f"{len(df.columns)}")
            with col3:
                completeness = 100 - (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
                st.metric("✓ Completude", f"{completeness:.1f}%")
            with col4:
                st.metric("🔄 Duplicatas", f"{df.duplicated().sum()}")
            
            # Estatísticas por tipo
            st.markdown('<h3 style="color: #00d4ff; margin-top: 2rem;">Composição dos Dados</h3>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Colunas Numéricas</div>
                        <div class="metric-value">{len(numeric_cols)}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Colunas Categóricas</div>
                        <div class="metric-value">{len(categorical_cols)}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Dados Faltantes</div>
                        <div class="metric-value">{missing_pct:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Estatísticas numéricas
            if numeric_cols:
                st.markdown('<h3 style="color: #00d4ff; margin-top: 2rem;">Estatísticas Numéricas</h3>', unsafe_allow_html=True)
                
                stats_df = df[numeric_cols].describe().round(2)
                st.dataframe(stats_df, use_container_width=True)
        
        # ============ TAB 2: ANÁLISES GRÁFICAS ============
        with tab2:
            st.markdown('<h2 class="section-title">Análises Gráficas</h2>', unsafe_allow_html=True)
            
            # Análises numéricas
            if numeric_cols:
                st.markdown('<h3 style="color: #00d4ff;">Distribuição de Variáveis Numéricas</h3>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                # Histogram
                with col1:
                    selected_numeric = st.selectbox(
                        "Selecione coluna numérica para histograma:",
                        numeric_cols,
                        key="histogram"
                    )
                    
                    fig = px.histogram(
                        df,
                        x=selected_numeric,
                        nbins=30,
                        title=f"Distribuição - {selected_numeric}",
                        color_discrete_sequence=['#00d4ff']
                    )
                    fig.update_layout(
                        height=400,
                        template="plotly_dark",
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Box plot
                with col2:
                    st.markdown("**Box Plot - Detecção de Outliers**")
                    fig = go.Figure()
                    for col in numeric_cols[:5]:
                        fig.add_trace(go.Box(y=df[col], name=col, boxmean='sd'))
                    
                    fig.update_layout(
                        title="Box Plot dos Dados",
                        height=400,
                        template="plotly_dark",
                        hovermode='y unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Correlações
                if len(numeric_cols) > 1:
                    st.markdown('<h3 style="color: #00d4ff; margin-top: 2rem;">Matriz de Correlações</h3>', unsafe_allow_html=True)
                    
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
                        height=500,
                        template="plotly_dark",
                        margin=dict(l=100, r=0, t=20, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Análises categóricas
            if categorical_cols:
                st.markdown('<h3 style="color: #00d4ff; margin-top: 2rem;">Distribuição de Categorias</h3>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                selected_cat = st.selectbox(
                    "Selecione coluna categórica:",
                    categorical_cols,
                    key="categorical"
                )
                
                top_values = df[selected_cat].value_counts().head(10)
                
                # Bar chart
                with col1:
                    fig = px.bar(
                        x=top_values.values,
                        y=top_values.index,
                        orientation='h',
                        title=f"Top 10 - {selected_cat}",
                        color_discrete_sequence=['#00d4ff']
                    )
                    fig.update_layout(height=400, template="plotly_dark", showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Pie chart
                with col2:
                    fig = px.pie(
                        values=top_values.values,
                        names=top_values.index,
                        title=f"Proporção - {selected_cat}"
                    )
                    fig.update_layout(height=400, template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Análise cruzada
            if numeric_cols and categorical_cols:
                st.markdown('<h3 style="color: #00d4ff; margin-top: 2rem;">Análise Cruzada</h3>', unsafe_allow_html=True)
                
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
                fig.update_layout(height=450, template="plotly_dark", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        # ============ TAB 3: DADOS DETALHADOS ============
        with tab3:
            st.markdown('<h2 class="section-title">Amostra dos Dados</h2>', unsafe_allow_html=True)
            
            st.dataframe(df.head(50), use_container_width=True)
            
            st.markdown('<h3 style="color: #00d4ff; margin-top: 2rem;">Tipos de Dados</h3>', unsafe_allow_html=True)
            
            type_info = pd.DataFrame({
                'Coluna': df.columns,
                'Tipo': df.dtypes,
                'Não-nulos': df.count(),
                'Nulos': df.isnull().sum()
            })
            st.dataframe(type_info, use_container_width=True)
            
            # Dados faltantes
            missing = df.isnull().sum()
            if missing.sum() > 0:
                st.markdown('<h3 style="color: #00d4ff; margin-top: 2rem;">⚠️ Dados Faltantes</h3>', unsafe_allow_html=True)
                missing_df = pd.DataFrame({
                    'Coluna': missing[missing > 0].index,
                    'Quantidade': missing[missing > 0].values,
                    'Percentual (%)': (missing[missing > 0].values / len(df) * 100).round(2)
                })
                st.dataframe(missing_df, use_container_width=True)
        
        # ============ TAB 4: EXPORTAR ============
        with tab4:
            st.markdown('<h2 class="section-title">Exportar Relatório</h2>', unsafe_allow_html=True)
            
            st.markdown("""
                <div class="info-box">
                    <h4>📥 Gere um Relatório em Excel</h4>
                    <p>O relatório incluirá seus dados originais, estatísticas descritivas e um resumo da análise.</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("📥 Gerar Relatório em Excel", use_container_width=True, key="export_btn"):
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
                            'Colunas Numéricas',
                            'Colunas Categóricas',
                            'Completude (%)',
                            'Duplicatas',
                            'Data de Análise'
                        ],
                        'Valor': [
                            len(df),
                            len(df.columns),
                            len(numeric_cols),
                            len(categorical_cols),
                            f"{100 - (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100):.2f}%",
                            df.duplicated().sum(),
                            datetime.now().strftime('%d/%m/%Y %H:%M')
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Resumo', index=False)
                
                buffer.seek(0)
                st.download_button(
                    label="⬇️ Baixar Relatório (Excel)",
                    data=buffer,
                    file_name=f"relatorio_datainsight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                st.success("✅ Relatório gerado com sucesso!")

else:
    # Landing page
    st.markdown("""
        <div style="text-align: center; margin-top: 5rem;">
            <h1 style="color: #00d4ff; font-size: 3rem;">📊 DataInsight v2.0</h1>
            <p style="color: #a0aec0; font-size: 1.2rem; margin: 2rem 0;">
                Transforme seus dados em insights automáticos
            </p>
            <hr style="border-color: #00d4ff; margin: 3rem 0;">
        </div>
        
        <div class="info-box">
            <h3>🚀 Como Usar</h3>
            <ol style="color: #ffffff; margin-left: 20px;">
                <li><strong>Carregue seu arquivo:</strong> CSV, Excel (.xlsx) ou Excel (.xls)</li>
                <li><strong>Análise automática:</strong> O sistema detectará tipos de dados automaticamente</li>
                <li><strong>Explore as análises:</strong> Veja distribuições, correlações e padrões</li>
                <li><strong>Exporte relatórios:</strong> Baixe análises em Excel para compartilhar</li>
            </ol>
        </div>
        
        <div style="margin-top: 3rem; padding: 2rem; background: linear-gradient(135deg, #0f3460 0%, #16213e 100%); border-radius: 10px; border-left: 4px solid #00d4ff;">
            <h4 style="color: #00d4ff;">✨ Recursos</h4>
            <ul style="color: #a0aec0;">
                <li>✅ Processa qualquer tipo de dado</li>
                <li>✅ Gráficos interativos automáticos</li>
                <li>✅ Estatísticas descritivas</li>
                <li>✅ Detecção de outliers</li>
                <li>✅ Matriz de correlações</li>
                <li>✅ Exportação de relatórios em Excel</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 5rem; opacity: 0.6;">
            <p style="color: #a0aec0;">Desenvolvido com ❤️ para transformar dados em decisões</p>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; opacity: 0.6; font-size: 0.85rem; color: #a0aec0;">
        <p>DataInsight v2.0 | Análise Automática de Dados para Múltiplas Empresas</p>
        <p>Built with Python, Streamlit & Plotly</p>
    </div>
""", unsafe_allow_html=True)