# app.py
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

INFERENCE_CSV = "inference_table.csv"   # precomputed table
# GOOGLE_SHEET_NAME = "NEET_PG_Prediction_Logs"

# =============================
# LOAD PRECOMPUTED DATA
# =============================
@st.cache_data
def load_inference_table():
    return pd.read_csv(INFERENCE_CSV)

inference_table = load_inference_table()

# =============================
# GOOGLE SHEETS LOGGING
# =============================
def log_to_gsheet(inputs):
    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", scope
        )
        client = gspread.authorize(creds)
        sheet = client.open(GOOGLE_SHEET_NAME).sheet1
        sheet.append_row(inputs)
    except Exception as e:
        st.warning(f"Logging failed: {e}")

# =============================
# STREAMLIT UI
# =============================
st.title("NEET PG College Predictor")

with st.form("input_form"):
    rank = st.number_input("Rank", min_value=1, value=1)

    # Dropdowns for quota & category
    quota_options = sorted(inference_table["quota"].unique().tolist())
    category_options = sorted(inference_table["category"].unique().tolist())

    quota = st.selectbox("Quota", options=quota_options, index=0)
    category = st.selectbox("Candidate Category", options=category_options, index=0)

    # College & Course dropdowns
    college_options = ["ANY"] + sorted(inference_table["college"].unique().tolist())
    course_options = ["ANY"] + sorted(inference_table["course"].unique().tolist())

    selected_college = st.selectbox("College", options=college_options)
    selected_course = st.selectbox("Course", options=course_options)

    group_by = st.radio("Group results by", ["College", "Course"])

    submitted = st.form_submit_button("Predict")

if submitted:
    # log inputs
    # log_to_gsheet([str(rank), quota, category, selected_college, selected_course, group_by])

    # filter by quota & category
    df_filtered = inference_table[
        (inference_table["quota"] == quota) &
        (inference_table["category"] == category)
    ]

    if selected_college != "ANY":
        df_filtered = df_filtered[df_filtered["college"] == selected_college]
    if selected_course != "ANY":
        df_filtered = df_filtered[df_filtered["course"] == selected_course]

    # eligibility by cutoff rank
    df_filtered = df_filtered[df_filtered["cutoff_rank"] >= rank]

    if df_filtered.empty:
        st.error("No eligible colleges/courses found for the given inputs.")
    else:
        if group_by == "College":
            for clg, group in df_filtered.groupby("college"):
                st.subheader(clg)

                # sort courses by min_rank (general rule)
                group_sorted = group.sort_values("min_rank")

                # show course + rank range
                display_df = group_sorted[["course", "min_rank", "cutoff_rank"]]
                display_df.rename(columns={
                    "min_rank": "Best Rank",
                    "cutoff_rank": "Last Rank"
                }, inplace=True)

                st.table(display_df)

        else:  # group by course
            for crs, group in df_filtered.groupby("course"):
                st.subheader(crs)

                # sort colleges by min_rank
                group_sorted = group.sort_values("min_rank")

                # show college + rank range
                display_df = group_sorted[["college", "min_rank", "cutoff_rank"]]
                display_df.rename(columns={
                    "min_rank": "Best Rank",
                    "cutoff_rank": "Last Rank"
                }, inplace=True)

                st.table(display_df)
