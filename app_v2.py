import hashlib
import hmac
from io import BytesIO

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="DataInsight",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
.stApp { background:#f7f8fc; color:#111827; }
.main .block-container { max-width:1500px; padding-top:1.5rem; }

section[data-testid="stSidebar"] {
    background:#fff;
    border-right:1px solid #e5e7eb;
}

.sidebar-logo {
    display:flex;
    align-items:center;
    gap:10px;
    margin-bottom:28px;
}

.logo-icon {
    width:38px;
    height:38px;
    border-radius:10px;
    background:linear-gradient(135deg,#4f46e5,#6366f1);
    color:white;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:700;
}

.logo-text {
    font-size:20px;
    font-weight:700;
    color:#111827;
}

.sidebar-section {
    color:#9ca3af;
    font-size:11px;
    font-weight:700;
    letter-spacing:.08em;
    text-transform:uppercase;
    margin:20px 0 8px;
}

.page-title {
    color:#111827;
    font-size:30px;
    font-weight:700;
    line-height:1.2;
}

.page-subtitle {
    color:#6b7280;
    font-size:14px;
}

.user-pill {
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding:7px 12px;
    background:#fff;
    border:1px solid #e5e7eb;
    border-radius:999px;
    color:#374151;
    font-size:13px;
    font-weight:600;
}

.user-dot,.status-dot {
    width:8px;
    height:8px;
    border-radius:50%;
    background:#22c55e;
}

.status-success {
    display:inline-flex;
    align-items:center;
    gap:7px;
    padding:5px 10px;
    background:#ecfdf5;
    border:1px solid #a7f3d0;
    border-radius:999px;
    color:#047857;
    font-size:12px;
    font-weight:600;
}

.kpi-card {
    min-height:120px;
    padding:20px;
    background:#fff;
    border:1px solid #e5e7eb;
    border-radius:14px;
    box-shadow:0 2px 8px rgba(15,23,42,.03);
}

.kpi-label { color:#6b7280; font-size:13px; }
.kpi-value {
    color:#111827;
    font-size:28px;
    font-weight:700;
    margin-top:7px;
}
.kpi-description { color:#9ca3af; font-size:12px; margin-top:8px; }

.section-title {
    color:#111827;
    font-size:18px;
    font-weight:700;
}
.section-description {
    color:#6b7280;
    font-size:13px;
    margin-bottom:16px;
}

div[data-testid="stMetric"] {
    background:#fff;
    border:1px solid #e5e7eb;
    border-radius:14px;
    padding:18px;
    box-shadow:0 2px 8px rgba(15,23,42,.03);
}

div[data-testid="stMetricLabel"] { color:#6b7280 !important; }
div[data-testid="stMetricValue"] { color:#111827 !important; }

.stButton > button {
    min-height:40px;
    border-radius:8px !important;
    border:1px solid #e5e7eb !important;
    font-weight:600 !important;
}

.stButton > button:hover {
    border-color:#6366f1 !important;
    color:#4f46e5 !important;
}

div[data-baseweb="select"] > div { border-radius:8px !important; }
input, textarea { border-radius:8px !important; }

.stTabs [data-baseweb="tab"] {
    color:#6b7280;
    font-weight:600;
}
.stTabs [aria-selected="true"] { color:#4f46e5 !important; }

/* Login */
.login-space { height:70px; }

.login-brand {
    max-width:540px;
    margin:auto;
    padding:36px 42px 24px;
    background:#fff;
    border:1px solid #e5e7eb;
    border-bottom:0;
    border-radius:18px 18px 0 0;
    box-shadow:0 15px 40px rgba(15,23,42,.08);
}

.login-logo {
    width:54px;
    height:54px;
    border-radius:14px;
    background:linear-gradient(135deg,#4f46e5,#6366f1);
    color:#fff;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:25px;
    margin-bottom:20px;
}

.login-title {
    color:#111827;
    font-size:28px;
    font-weight:700;
    margin-bottom:6px;
}

.login-subtitle { color:#6b7280; font-size:14px; }

.login-fields {
    max-width:540px;
    margin:auto;
    padding:0 42px 36px;
    background:#fff;
    border:1px solid #e5e7eb;
    border-top:0;
    border-radius:0 0 18px 18px;
    box-shadow:0 15px 40px rgba(15,23,42,.08);
}

.login-fields label {
    color:#374151 !important;
    font-weight:600 !important;
}

.login-fields input {
    background:#fff !important;
    color:#111827 !important;
    border:1px solid #d1d5db !important;
}

.login-button > div > button {
    background:#4f46e5 !important;
    color:#fff !important;
    border:0 !important;
}
.login-button > div > button:hover {
    background:#4338ca !important;
    color:#fff !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION
# ============================================================

defaults = {
    "logado": False,
    "is_admin": False,
    "user_name": "",
    "df_global": None,
    "df_filtered": None,
    "uploaded_name": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# AUTH
# ============================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_credentials(username: str, password: str) -> bool:
    try:
        configured_user = st.secrets["LOGIN_USERNAME"]
        configured_hash = st.secrets["LOGIN_PASSWORD_HASH"]
    except Exception:
        st.error(
            "Login configuration not found. "
            "Configure LOGIN_USERNAME and LOGIN_PASSWORD_HASH in secrets."
        )
        return False

    return (
        hmac.compare_digest(username, configured_user)
        and hmac.compare_digest(
            hash_password(password),
            configured_hash,
        )
    )


def login_screen():
    st.markdown('<div class="login-space"></div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="login-brand">
            <div class="login-logo">📊</div>
            <div class="login-title">Welcome back</div>
            <div class="login-subtitle">
                Sign in to access your DataInsight dashboard.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-fields">', unsafe_allow_html=True)

    username = st.text_input(
        "Username",
        placeholder="Enter your username",
        key="login_username",
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password",
    )

    st.markdown('<div class="login-button">', unsafe_allow_html=True)

    clicked = st.button(
        "Sign in",
        use_container_width=True,
        key="login_button",
    )

    st.markdown("</div></div>", unsafe_allow_html=True)

    if clicked:
        if verify_credentials(username, password):
            st.session_state.logado = True
            st.session_state.is_admin = True
            st.session_state.user_name = username
            st.rerun()
        else:
            st.error("Invalid username or password.")


# ============================================================
# DATA
# ============================================================

def load_data(file_bytes: bytes, filename: str) -> pd.DataFrame:
    extension = filename.lower().rsplit(".", 1)[-1]

    try:
        if extension == "csv":
            try:
                df = pd.read_csv(BytesIO(file_bytes), low_memory=False)
            except UnicodeDecodeError:
                df = pd.read_csv(
                    BytesIO(file_bytes),
                    encoding="latin1",
                    low_memory=False,
                )
        elif extension in {"xlsx", "xls"}:
            df = pd.read_excel(BytesIO(file_bytes))
        elif extension == "parquet":
            df = pd.read_parquet(BytesIO(file_bytes))
        else:
            raise ValueError("Unsupported file format.")

        df = df.dropna(axis=1, how="all")
        df.columns = [str(column).strip() for column in df.columns]

        return df

    except Exception as error:
        st.error(f"Error loading dataset: {error}")
        return pd.DataFrame()


def data_quality(df: pd.DataFrame) -> dict:
    rows = len(df)
    columns = len(df.columns)
    total_cells = max(rows * columns, 1)
    missing = int(df.isna().sum().sum())
    missing_pct = round((missing / total_cells) * 100, 2)

    return {
        "rows": rows,
        "columns": columns,
        "missing": missing,
        "missing_pct": missing_pct,
        "completeness": round(100 - missing_pct, 2),
        "duplicates": int(df.duplicated().sum()),
    }


def format_number(value) -> str:
    if isinstance(value, (float, np.floating)):
        return (
            f"{value:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
    return f"{value:,}".replace(",", ".")


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-logo">
                <div class="logo-icon">↗</div>
                <div class="logo-text">DataInsight</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<div class="sidebar-section">Workspace</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Logged as: {st.session_state.user_name}")

        st.markdown(
            '<div class="sidebar-section">Data Source</div>',
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Upload dataset",
            type=["csv", "xlsx", "xls", "parquet"],
            help="Supported formats: CSV, Excel and Parquet.",
        )

        if uploaded is not None:
            if st.session_state.uploaded_name != uploaded.name:
                df = load_data(uploaded.getvalue(), uploaded.name)

                if not df.empty:
                    st.session_state.df_global = df
                    st.session_state.df_filtered = df.copy()
                    st.session_state.uploaded_name = uploaded.name
                    st.success("Dataset loaded successfully.")

        if st.session_state.df_global is not None:
            st.markdown(
                '<div class="sidebar-section">Filters</div>',
                unsafe_allow_html=True,
            )

            temp = st.session_state.df_global.copy()

            categorical = (
                temp.select_dtypes(
                    include=["object", "category", "string"]
                ).columns.tolist()
            )

            for column in categorical[:5]:
                options = temp[column].dropna().unique().tolist()

                if not options:
                    continue

                options = sorted(options, key=lambda x: str(x))

                selected = st.multiselect(
                    column,
                    options,
                    key=f"filter_{column}",
                )

                if selected:
                    temp = temp[temp[column].isin(selected)]

            st.session_state.df_filtered = temp

            st.markdown(
                '<div class="sidebar-section">Dataset</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"📄 {st.session_state.uploaded_name}")
            st.caption(f"Rows: {len(temp):,}")
            st.caption(f"Columns: {len(temp.columns):,}")

        st.divider()

        if st.button("Logout", use_container_width=True, key="logout"):
            st.session_state.clear()
            st.rerun()


# ============================================================
# COMPONENTS
# ============================================================

def render_header():
    left, right = st.columns([7, 2])

    with left:
        st.markdown(
            '<div class="page-title">Overview</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="page-subtitle">'
            "Monitor, analyze and explore your data."
            "</div>",
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div style="text-align:right;margin-top:8px;">
                <span class="user-pill">
                    <span class="user-dot"></span>
                    {st.session_state.user_name}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_kpis(df):
    q = data_quality(df)

    cards = [
        ("Total Records", format_number(q["rows"]), "Rows in dataset"),
        ("Columns", format_number(q["columns"]), "Available fields"),
        ("Completeness", f'{q["completeness"]}%', "Data without missing values"),
        ("Duplicates", format_number(q["duplicates"]), "Duplicated records"),
    ]

    columns = st.columns(4)

    for column, card in zip(columns, cards):
        with column:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{card[0]}</div>
                    <div class="kpi-value">{card[1]}</div>
                    <div class="kpi-description">{card[2]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_overview(df):
    st.markdown(
        '<div class="section-title">Dataset Overview</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-description">'
        "Quick summary of the current dataset."
        "</div>",
        unsafe_allow_html=True,
    )

    numeric = df.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric:
        st.info("No numeric columns are available for the overview.")
        return

    left, right = st.columns(2)

    with left:
        column = st.selectbox(
            "Select metric",
            numeric,
            key="overview_metric",
        )

        fig = px.histogram(df, x=column, nbins=30)
        fig.update_layout(template="plotly_white", height=350)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        q = data_quality(df)

        quality_df = pd.DataFrame({
            "Metric": ["Completeness", "Missing Data", "Duplicate Records"],
            "Value": [
                q["completeness"],
                q["missing_pct"],
                q["duplicates"] / max(q["rows"], 1) * 100,
            ],
        })

        fig = px.bar(
            quality_df,
            x="Metric",
            y="Value",
            text="Value",
        )
        fig.update_layout(
            template="plotly_white",
            height=350,
            yaxis_title="Percentage",
            xaxis_title="",
        )
        st.plotly_chart(fig, use_container_width=True)


def render_quality(df):
    q = data_quality(df)

    st.markdown(
        '<div class="section-title">Data Quality</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-description">'
        "Overview of dataset completeness and integrity."
        "</div>",
        unsafe_allow_html=True,
    )

    a, b, c, d = st.columns(4)
    a.metric("Records", format_number(q["rows"]))
    b.metric("Columns", format_number(q["columns"]))
    c.metric("Missing Values", f'{q["missing_pct"]}%')
    d.metric("Completeness", f'{q["completeness"]}%')

    st.markdown("### Missing Values by Column")

    missing = df.isna().sum().reset_index()
    missing.columns = ["Column", "Missing"]
    missing = missing[missing["Missing"] > 0].sort_values(
        "Missing",
        ascending=False,
    )

    if missing.empty:
        st.success("No missing values were found.")
        return

    fig = px.bar(
        missing,
        x="Missing",
        y="Column",
        orientation="h",
        text_auto=True,
    )
    fig.update_layout(
        template="plotly_white",
        height=max(300, len(missing) * 35),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_analysis(df):
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical = df.select_dtypes(
        include=["object", "category", "string"]
    ).columns.tolist()

    st.markdown(
        '<div class="section-title">Dynamic Analysis</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-description">'
        "Build visualizations dynamically from your dataset."
        "</div>",
        unsafe_allow_html=True,
    )

    if not numeric:
        st.info("No numeric columns are available.")
        return

    c1, c2, c3 = st.columns(3)

    with c1:
        y_axis = st.selectbox("Numeric column", numeric, key="analysis_y")

    with c2:
        chart_type = st.selectbox(
            "Chart type",
            ["Bar", "Line", "Pie", "Histogram", "Box Plot"],
            key="analysis_chart",
        )

    with c3:
        aggregation = st.selectbox(
            "Aggregation",
            ["Sum", "Mean", "Count"],
            key="analysis_aggregation",
        )

    if chart_type == "Histogram":
        fig = px.histogram(df, x=y_axis, nbins=30)

    else:
        if not categorical:
            st.warning("A categorical column is required.")
            return

        x_axis = st.selectbox(
            "Category",
            categorical,
            key="analysis_x",
        )

        agg_map = {
            "Sum": "sum",
            "Mean": "mean",
            "Count": "count",
        }

        chart_data = (
            df.groupby(x_axis, observed=True)[y_axis]
            .agg(agg_map[aggregation])
            .reset_index()
            .sort_values(y_axis, ascending=False)
            .head(20)
        )

        if chart_type == "Bar":
            fig = px.bar(
                chart_data,
                x=x_axis,
                y=y_axis,
                text_auto=".2s",
            )
        elif chart_type == "Line":
            fig = px.line(
                chart_data,
                x=x_axis,
                y=y_axis,
                markers=True,
            )
        elif chart_type == "Pie":
            fig = px.pie(
                chart_data,
                names=x_axis,
                values=y_axis,
                hole=0.45,
            )
        else:
            fig = px.box(
                df,
                x=x_axis,
                y=y_axis,
            )

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_explorer(df):
    st.markdown(
        '<div class="section-title">Data Explorer</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-description">'
        "Explore the records selected by your filters."
        "</div>",
        unsafe_allow_html=True,
    )

    st.dataframe(
        df.head(100),
        use_container_width=True,
        height=500,
    )


def render_ai(df):
    st.markdown(
        '<div class="section-title">AI Insights Assistant</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-description">'
        "Ask questions about the current filtered dataset."
        "</div>",
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "Your question",
        placeholder="Example: Which columns contain the most missing values?",
        height=100,
        key="ai_question",
    )

    if st.button(
        "Generate Insight",
        type="primary",
        key="ai_button",
    ):
        if not question.strip():
            st.warning("Enter a question first.")
            return

        try:
            import google.generativeai as genai

            genai.configure(
                api_key=st.secrets["GEMINI_API_KEY"]
            )

            model = genai.GenerativeModel(
                "gemini-1.5-flash"
            )

            columns = ", ".join(df.columns.astype(str))

            prompt = f"""
You are a data analyst.

Dataset:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Available columns: {columns}

Question:
{question}

Answer clearly and concisely.
Do not invent dataset values.
"""

            response = model.generate_content(prompt)

            st.markdown("### AI Response")
            st.write(response.text)

        except Exception as error:
            st.error("Could not connect to the AI service.")
            st.caption(f"Technical detail: {error}")


def render_export(df):
    st.markdown(
        '<div class="section-title">Export Center</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-description">'
        "Download the currently filtered dataset."
        "</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    csv_data = df.to_csv(index=False).encode("utf-8")

    with left:
        st.download_button(
            "Download CSV",
            csv_data,
            "datainsight_export.csv",
            "text/csv",
            use_container_width=True,
            key="download_csv",
        )

    with right:
        buffer = BytesIO()
        df.to_excel(buffer, index=False)

        st.download_button(
            "Download Excel",
            buffer.getvalue(),
            "datainsight_export.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_excel",
        )


# ============================================================
# RUN APP
# ============================================================

if not st.session_state.logado:
    login_screen()
    st.stop()

render_sidebar()

if st.session_state.df_global is None:
    render_header()

    st.markdown("""
        <div style="
            margin-top:25px;
            padding:70px 30px;
            background:#fff;
            border:1px solid #e5e7eb;
            border-radius:16px;
            text-align:center;
            box-shadow:0 2px 8px rgba(15,23,42,.03);
        ">
            <div style="font-size:48px;">📊</div>
            <h2 style="color:#111827;">Welcome to DataInsight</h2>
            <p style="color:#6b7280;">
                Upload a CSV, Excel or Parquet dataset
                using the sidebar to start analyzing your data.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.stop()

df = st.session_state.df_filtered

if df is None:
    df = st.session_state.df_global.copy()
    st.session_state.df_filtered = df

render_header()

st.markdown(
    f"""
    <span class="status-success">
        <span class="status-dot"></span>
        Dataset loaded
    </span>
    <span style="margin-left:10px;color:#6b7280;font-size:13px;">
        {len(df):,} records currently selected
    </span>
    """,
    unsafe_allow_html=True,
)

st.markdown("")
render_kpis(df)
st.markdown("")

tabs = st.tabs([
    "Overview",
    "Data Quality",
    "Analysis",
    "Data Explorer",
    "AI Assistant",
    "Export",
])

with tabs[0]:
    render_overview(df)

with tabs[1]:
    render_quality(df)

with tabs[2]:
    render_analysis(df)

with tabs[3]:
    render_explorer(df)

with tabs[4]:
    render_ai(df)

with tabs[5]:
    render_export(df)
