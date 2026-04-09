import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =========================
# CLEAN UI
# =========================
st.markdown("""
<style>
.block-container { padding-top: 1rem; padding-bottom: 1rem; }
header {visibility: hidden;}
.stApp { background-color: #f5fff9; }

h1 { color: #00A859; margin: 0px; }

.stButton>button {
    background-color: #00A859;
    color: white;
    border-radius: 8px;
    border: none;
}
.stButton>button:hover { background-color: #008f4c; }

[data-testid="stDataFrame"] {
    border: 2px solid #00A859;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FILE PATH
# =========================
file_path = r"C:\Users\phsriniv\OneDrive - Hewlett Packard Enterprise\PPCM DEMO - Documents\Book1.xlsx"

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    return pd.read_excel(file_path, sheet_name="query (11)")

df = load_data()

# =========================
# TITLE
# =========================
st.markdown("<h1>📊 EXHIBIT EMEA Dashboard</h1>", unsafe_allow_html=True)

# =========================
# DASHBOARD LINK (FOR SHARING)
# =========================
st.info("🔗 After deployment, share this dashboard link with clients (example below):")
st.code("https://your-dashboard.streamlit.app")

# =========================
# SESSION STATE
# =========================
if "search_text" not in st.session_state:
    st.session_state.search_text = ""

if "reset_flag" not in st.session_state:
    st.session_state.reset_flag = False

# =========================
# FILTER
# =========================
column = st.selectbox("Filter Column", df.columns)

values = sorted(df[column].dropna().astype(str).unique())

if st.session_state.reset_flag:
    for v in values:
        key = f"{column}_{v}"
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.search_text = ""
    st.session_state.reset_flag = False

search_text = st.text_input("Search value...", value=st.session_state.search_text)
st.session_state.search_text = search_text

display_values = [v for v in values if search_text.lower() in v.lower()] if search_text else values

selected_values = []

for val in display_values:
    key = f"{column}_{val}"

    if key not in st.session_state:
        st.session_state[key] = False

    if st.checkbox(val, key=key):
        selected_values.append(val)

filtered_df = df[df[column].astype(str).isin(selected_values)] if selected_values else df

# =========================
# ACTION BAR
# =========================
action_col1, action_col2, _ = st.columns([1, 1, 8])

with action_col1:
    form_url = "https://hpe.sharepoint.com/teams/gccdmprojects/_layouts/15/listforms.aspx?cid=MmYyYTYxZTYtMDk3OC00YzEzLTgwM2UtODAzOTcxMzUzZDA0&nav=ODQyYWVkNmUtMDI4MS00MTg2LTk3NGItYTI3NTMwMDJlNzFl"

    st.markdown(
        f"""
        <a href="{form_url}" target="_blank">
            <button style="
                background-color:#00A859;
                color:white;
                padding:10px 15px;
                border:none;
                border-radius:8px;
                font-size:14px;">
                ➕ Form
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

with action_col2:
    if st.button("Clear"):
        st.session_state.reset_flag = True
        st.rerun()

# =========================
# FULL WIDTH TABLE
# =========================
st.subheader("Filtered Data")

if not filtered_df.empty:

    temp_df = filtered_df.copy()
    temp_df["__index"] = temp_df.index

    edited_df = st.data_editor(temp_df, use_container_width=True)

    updated = False

    for i, row in edited_df.iterrows():
        original_index = int(row["__index"])

        for col in df.columns:
            if str(row[col]) != str(df.loc[original_index, col]):
                df.loc[original_index, col] = row[col]
                updated = True

    if updated:
        df.to_excel(file_path, sheet_name="query (11)", index=False)
        st.success("✅ Auto-saved")

else:
    st.warning("No data available")

# =========================
# CHART
# =========================
if not filtered_df.empty:

    numeric_cols = filtered_df.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_cols) > 0:
        st.bar_chart(filtered_df[numeric_cols[0]])