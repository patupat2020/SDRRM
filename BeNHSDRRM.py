import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
import io
import string

# Helper: Generate list of section letters
def get_sections(count):
    return list(string.ascii_uppercase[:count])

st.set_page_config(page_title="BNHS DRRM Headcount", page_icon="🚨")
st.title("🚨 BNHS Emergency Headcount")

# --- 1. CONNECT TO GOOGLE SHEETS ---
def get_sheet():
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    sh = gc.open("Headcount_Database")
    return sh.sheet1

sheet = get_sheet()
data = sheet.get_all_records()
df_existing = pd.DataFrame(data)

# Filter duplicates
already_submitted = df_existing['Section_Info'].unique().tolist() if not df_existing.empty else []

# --- 2. SELECTION LOGIC ---
division = st.radio("Select Division", ["JHS", "SHS"], index=None, horizontal=True)
teacher_name = st.text_input("Adviser Name", key="adv_name")

section_label = None

if division == "JHS":
    grade = st.selectbox("Grade Level", [7, 8, 9, 10], index=None)
    if grade:
        count = 15 if grade == 7 else 14
        all_sects = [f"JHS - Grade {grade} - {s}" for s in get_sections(count)]
        available = [s for s in all_sects if s not in already_submitted]
        section_label = st.selectbox("Select Available Section", available, index=None)

elif division == "SHS":
    grade = st.selectbox("Grade Level", [11, 12], index=None)
    if grade == 11:
        track = st.radio("Track", ["TechPro", "Academics"], index=None, horizontal=True)
        if track:
            count = 10 if track == "TechPro" else 12
            all_sects = [f"SHS - Grade 11 - {track} - {s}" for s in get_sections(count)]
            available = [s for s in all_sects if s not in already_submitted]
            section_label = st.selectbox("Select Available Section", available, index=None)
    elif grade == 12:
        track = st.radio("Track", ["TVL", "ACAD"], index=None, horizontal=True)
        if track:
            if track == "TVL":
                all_sects = [f"SHS - Grade 12 - TVL - {s}" for s in get_sections(9)]
                available = [s for s in all_sects if s not in already_submitted]
                section_label = st.selectbox("Select Available Section", available, index=None)
            elif track == "ACAD":
                strand = st.selectbox("Strand", ["HUMSS", "STEM", "ABM", "SPORTS"], index=None)
                if strand:
                    strands = {"HUMSS": 5, "STEM": 3, "ABM": 3, "SPORTS": 1}
                    all_sects = [f"SHS - Grade 12 - ACAD - {strand} - {s}" for s in get_sections(strands[strand])]
                    available = [s for s in all_sects if s not in already_submitted]
                    section_label = st.selectbox("Select Available Section", available, index=None)

# --- 3. INPUT FORM ---
if section_label:
    with st.form("headcount_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👨 Male")
            m_p = st.number_input("Male Present", 0, step=1)
            m_m = st.number_input("Male Missing", 0, step=1)
        with col2:
            st.subheader("👩 Female")
            f_p = st.number_input("Female Present", 0, step=1)
            f_m = st.number_input("Female Missing", 0, step=1)
        submit = st.form_submit_button("Submit Headcount")

    if submit:
        sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), teacher_name, division, section_label, m_p, m_m, f_p, f_m])
        st.success("Submitted!")
        st.rerun()

# --- 4. DASHBOARD ---
if st.sidebar.checkbox("Coordinator: View Master List"):
    if not df_existing.empty:
        st.dataframe(df_existing)
        total = int(df_existing['Male_Missing'].sum() + df_existing['Female_Missing'].sum())
        st.metric("Total Missing Students", total)
        
        buffer = io.BytesIO()
        df_existing.to_excel(buffer, index=False)
        st.download_button("📥 Download Excel", buffer.getvalue(), "Headcount.xlsx")