import streamlit as st

# Debugging: Print keys to the console
st.write("Current secrets keys loaded:", st.secrets.keys())

# If the app crashes, comment out the line below to let it run
# sheet = get_sheet()

import pandas as pd
import gspread
from datetime import datetime
import io
import string

st.set_page_config(page_title="BeNHS DRRM Headcount", page_icon="🚨")
st.title("🚨 BeNHS Emergency Headcount")

# --- 1. CONNECT TO GOOGLE SHEETS ---
@st.cache_resource
# Make sure your function definition is followed by an indented block
def get_sheet():
    # Everything below must have an extra indent (4 spaces or 1 tab)
    credentials = dict(st.secrets["gcp_service_account"])
    gc = gspread.service_account_from_dict(credentials)
    
    # Ensure all your subsequent sheet logic is also indented
    sheet = gc.open("Your_Sheet_Name").sheet1
    return sheet

# The code that calls the function should NOT be indented
sheet = get_sheet()
    data = sheet.get_all_records()
    df_existing = pd.DataFrame(data)
    already_submitted = df_existing['Section_Info'].unique().tolist() if not df_existing.empty else []
except Exception as e:
    st.error(f"Error connecting to Google Sheets: {e}")
    st.stop()

# --- 2. SELECTION LOGIC ---
division = st.radio("Select Division", ["JHS", "SHS"], index=None, horizontal=True)
teacher_name = st.text_input("Adviser Name", key="adv_name")

section_label = None

# ... [Insert your section selection logic here, ensuring section_label is defined] ...

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
        
        if st.form_submit_button("Submit Headcount"):
            sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), teacher_name, division, section_label, m_p, m_m, f_p, f_m])
            st.success("Submitted successfully!")
            st.rerun()

# --- 4. COORDINATOR DASHBOARD ---
if st.sidebar.checkbox("Coordinator: View Master List"):
    if not df_existing.empty:
        st.dataframe(df_existing)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_existing.to_excel(writer, index=False)
        st.download_button("📥 Download Excel", buffer.getvalue(), "Headcount_Report.xlsx")
    else:
        st.write("No data found.")
