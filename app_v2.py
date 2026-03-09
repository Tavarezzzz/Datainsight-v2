import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
from io import BytesIO
import warnings

warnings.filterwarnings('ignore')

# --- GENERAL CONFIG ---
st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- OPTIMIZED DATA LOADING (VECTORIZED) ---
@st.cache_data(show_spinner="Optimizing memory...", max_entries=5)
def load_and_optimize_data(file_bytes, file_name):
    try:
        buf = BytesIO(file_bytes)
        if file_name.endswith('.csv'):
            df = pd.read_csv(buf, low_memory=False)
        elif file_name.endswith('.parquet'):
            df = pd.read_parquet(buf)
        else:
            df = pd.read_excel(buf)
        
        # Numeric downcasting to save RAM
        for col in df.select_dtypes(include=['int64', 'float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer' if df[col].dtype == 'int64' else 'float')
        
        # Convert object columns with low cardinality to categories
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / max(len(df), 1) < 0.5:
                df[col] = df[col].astype('category')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# --- CSS STYLING ---
st.markdown("""
    <style>
    input, textarea, [data-baseweb="input"], [data-baseweb="textarea"] {
        border-radius: 6px !important;
        border: 1px solid rgba(100, 150, 200, 0.5) !important;
    }
    button[kind="primary"] { border-radius: 6px !important; }
    [data-testid="stMetric"] {
        padding: 15px !important;
        border-radius: 8px !important;
        background-color: rgba(255, 255, 255, 0.05);
    }
    hr { margin: 1.5rem 0 !important; }
    .user-badge {
        font-size: 0.75rem;
        font-weight: bold;
        padding: 3px 10px;
        border-radius: 4px;
        background-color: rgba(93, 173, 226, 0.2);
        color: #5dade2;
        border: 1px solid rgba(93, 173, 226, 0.4);
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "chat" not in st.session_state:
    st.session_state.chat = []
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "df_global" not in st.session_state:
    st.session_state.df_global = None

# --- LOGIN SCREEN ---
def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("Login")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Enter", use_container_width=True):
            if user == "admin" and pw == "1234":
                st.session_state.update({"logado": True, "is_admin": True, "user_name": "Admin"})
                st.rerun()
            elif user and pw:
                st.session_state.update({"logado": True, "is_admin": False, "user_name": user.capitalize()})
                st.rerun()
            else:
                st.error("Invalid username or password.")

if not st.session_state.logado:
    login_screen()
    st.stop()

# --- SIDEBAR (DYNAMIC CASCADING FILTERS) ---
with st.sidebar:
    status_label = "ADMIN" if st.session_state.is_admin else "USER"
    st.markdown(f"<span class='user-badge'>{status_label}</span>", unsafe_allow_html=True)
    
    st.header("Records Status")
    metric_placeholder = st.empty()
    st.divider()

    st.header("Data Source")
    uploaded_file = st.file_uploader("Upload CSV, Excel or Parquet", type=["csv", "xlsx", "xls", "parquet"])
    
    if uploaded_file:
        file_bytes = uploaded_file.read()
        st.session_state.df_global = load_and_optimize_data(file_bytes, uploaded_file.name)

    df_filtered = None
    if st.session_state.df_global is not None:
        st.header("Smart Filters")
        temp_df = st.session_state.df_global.copy()
        cat_cols = temp_df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        for col in cat_cols[:5]:
            options = sorted(temp_df[col].unique().tolist())
            if options:
                selected = st.multiselect(f"Filter {col}", options, key=f"filt_{col}")
                if selected:
                    temp_df = temp_df[temp_df[col].isin(selected)]
        
        df_filtered = temp_df
        metric_placeholder.metric("Filtered Records", f"{len(df_filtered):,}", f"Total: {len(st.session_state.df_global):,}")

if st.session_state.df_global is None:
    st.info("👈 Please upload a dataset in the sidebar to begin.")
    st.stop()

# --- HEADER ---
col_h1, col_h2 = st.columns([8, 1])
with col_h1:
    st.markdown(f"<h3 style='margin-bottom:-15px;color:#5dade2;'>Hello, {st.session_state.user_name}!</h3>", unsafe_allow_html=True)
    st.title("Dashboard")
with col_h2:
    if st.button("Logout", use_container_width=True):
        st.session_state.update({"logado": False, "df_global": None, "chat": []})
        st.rerun()

st.divider()

# --- IA ASSISTANT (GEMINI) ---
def ai_context(df_f):
    rows, cols = df_f.shape
    return f"Dataset has {rows} rows and {cols} columns. Active columns: {', '.join(df_f.columns.tolist())}."

with st.expander("🤖 AI Insights Assistant", expanded=False):
    query = st.text_input("Ask anything about the current filtered data:")
    if st.button("Analyze"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"{ai_context(df_filtered)}\nUser Question: {query}"
            response = model.generate_content(prompt)
            st.write(response.text)
        except: st.error("AI connection error. Check your API Key.")

# --- DYNAMIC KPIS (WITH FORMATTING) ---
st.subheader("Key Performance Indicators")

# Filter numeric columns to avoid summing Years/IDs
kpi_cols = [c for c in df_filtered.select_dtypes(include=[np.number]).columns if "year" not in c.lower() and "ano" not in c.lower()]

if kpi_cols:
    cols_kpi = st.columns(min(len(kpi_cols), 4))
    for i, col_name in enumerate(kpi_cols[:4]):
        total_val = df_filtered[col_name].sum()
        
        # BR Formatting: 1.000.000,00
        formatted_val = f"{total_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        cols_kpi[i].metric(col_name, formatted_val)
else:
    st.warning("No suitable numeric columns found for KPIs.")

# --- GRAPHICAL ANALYSIS ---
st.divider()
tab1, tab2, tab3, tab4 = st.tabs(["Analysis Hub", "Data Distribution", "Raw Data", "Export"])

with tab1:
    st.subheader("Dynamic Visualizer")
    g_col1, g_col2 = st.columns([3, 1])
    
    with g_col2:
        chart_type = st.radio("Chart Type:", ["Bar", "Pie", "Line", "Box Plot"])
        agg_func = st.selectbox("Aggregation:", ["Sum", "Mean", "Count"])
    
    with g_col1:
        # Use all numeric columns for charts (including Year)
        all_num_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df_filtered.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if all_num_cols and cat_cols:
            y_axis = st.selectbox("Numeric Value (Y):", all_num_cols, key="y_axis")
            x_axis = st.selectbox("Category (X):", cat_cols, key="x_axis")
            
            agg_map = {"Sum": "sum", "Mean": "mean", "Count": "count"}
            chart_data = df_filtered.groupby(x_axis, observed=True)[y_axis].agg(agg_map[agg_func]).reset_index().sort_values(y_axis, ascending=False).head(15)
            
            if chart_type == "Bar":
                fig = px.bar(chart_data, x=x_axis, y=y_axis, color=y_axis, text_auto='.2s', color_continuous_scale=['#08306b', '#5dade2'])
                fig.update_layout(coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)")
            elif chart_type == "Pie":
                fig = px.pie(chart_data, names=x_axis, values=y_axis, hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
            elif chart_type == "Line":
                fig = px.line(df_filtered.sort_values(x_axis), x=x_axis, y=y_axis, markers=True, color_discrete_sequence=['#5dade2'])
            elif chart_type == "Box Plot":
                fig = px.box(df_filtered, x=x_axis, y=y_axis, color=x_axis)
                
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Distribution Analysis")
    if all_num_cols:
        h_col = st.selectbox("Select column for Histogram:", all_num_cols)
        fig_h = px.histogram(df_filtered, x=h_col, marginal="violin", color_discrete_sequence=['#5dade2'], nbins=30)
        st.plotly_chart(fig_h, use_container_width=True)

with tab3:
    st.subheader("Tabular View (Top 30)")
    st.dataframe(df_filtered.head(30), use_container_width=True)

with tab4:
    st.subheader("Export Center")
    ex1, ex2 = st.columns(2)
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    ex1.download_button("Download CSV", csv, "extract.csv", "text/csv", use_container_width=True)
    
    if ex2.button("Prepare Excel", use_container_width=True):
        buf = BytesIO()
        df_filtered.to_excel(buf, index=False)
        st.download_button("Download Excel File", buf.getvalue(), "extract.xlsx", use_container_width=True)