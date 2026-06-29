import streamlit as st
import pandas as pd
import string
from datetime import datetime
import os
import io

# Helper: Generate list of section letters
def get_sections(count):
    return list(string.ascii_uppercase[:count])

st.set_page_config(page_title="BNHS DRRM Headcount", page_icon="🚨")
st.title("🚨 BNHS Emergency Headcount")

DATA_FILE = "headcount_log.csv"

# --- 1. LOAD EXISTING DATA (For Duplicate Prevention) ---
already_submitted = []
if os.path.exists(DATA_FILE):
    df_existing = pd.read_csv(DATA_FILE)
    already_submitted = df_existing['Section_Info'].unique().tolist()

# --- 2. SELECTION LOGIC ---
division = st.radio("Select Division", ["JHS", "SHS"], index=None, horizontal=True)
teacher_name = st.text_input("Adviser Name", key="adv_name")

grade = None
section = None
section_label = ""

# JHS Logic
if division == "JHS":
    grade = st.selectbox("Grade Level", [7, 8, 9, 10], index=None)
    if grade:
        count = 15 if grade == 7 else 14
        all_sects = [f"JHS - Grade {grade} - {s}" for s in get_sections(count)]
        # Filter: Only show sections not in the CSV
        available = [s for s in all_sects if s not in already_submitted]
        section_label = st.selectbox("Select Available Section", available, index=None)

# SHS Logic
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
                all_sects = [f"SHS - Grade 12 - TVL - {s}" for s in get_sections(9)] # A-I
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
    st.write("---")
    with st.form("headcount_form"):
        col1, col2 = st.columns(2)
        with col1:
            present = st.number_input("Students Present", min_value=0, step=1)
        with col2:
            missing = st.number_input("Students Missing", min_value=0, step=1)
        
        submit = st.form_submit_button("Submit Headcount")

    if submit:
        if not teacher_name:
            st.error("Please enter your name.")
        else:
            entry = {
                'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                'Teacher': [teacher_name],
                'Level': [division],
                'Section_Info': [section_label],
                'Present': [present],
                'Missing': [missing]
            }
            df = pd.DataFrame(entry)
            header = False if os.path.exists(DATA_FILE) else True
            df.to_csv(DATA_FILE, mode='a', header=header, index=False)
            st.success(f"Report submitted for {section_label}. Refreshing...")
            st.rerun()

# --- 4. COORDINATOR DASHBOARD ---
if st.sidebar.checkbox("Coordinator: View Master List"):
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.write("### Current Headcount Status")
        st.dataframe(df)
        
        # Excel Download Logic
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Download Data as Excel",
            data=buffer.getvalue(),
            file_name="Headcount_Report.xlsx",
            mime="application/vnd.ms-excel"
        )
        
        st.write("---")
        if st.button("Start New Month (Archive Data)"):
            archive_name = f"headcount_archive_{datetime.now().strftime('%Y-%m-%d')}.csv"
            os.rename(DATA_FILE, archive_name)
            st.success(f"Data archived as {archive_name}. Ready for new entries.")
            st.rerun()
    else:
        st.write("No data recorded yet.")