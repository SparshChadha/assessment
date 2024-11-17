import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

def load_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            try:
                return pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                return pd.read_csv(uploaded_file, encoding='latin-1')
        else:
            return pd.read_excel(uploaded_file)
    except Exception as e:
        st.sidebar.error(f":red[Error reading file: {str(e)}]")
        return None

def load_gsheets(url):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(spreadsheet=url, ttl=5)
    except Exception as e:
        st.sidebar.error(f"""
            Connection failed. Please check:
            1. The spreadsheet is shared correctly
            2. The URL is valid
            3. You have proper permissions
            
            Error: {str(e)}
        """)
        return None

def show_data_source_selector():
    with st.sidebar:
        st.markdown("### Data Source Selection")
        return st.radio("Choose Data Source", ["Upload File", "Google Sheets"])

def handle_file_upload():
    with st.sidebar:
        uploaded_file = st.file_uploader(
            label="Upload CSV/Excel File",
            type=["csv", "xlsx"],
            help="Upload your inventory data file here"
        )
        if uploaded_file is not None:
            data = load_file(uploaded_file)
            if data is not None:
                st.sidebar.success(":green[File uploaded successfully!]")
            return data
    return None

def handle_gsheets_connection():
    with st.sidebar:
        st.markdown("### Google Sheets Connection")
        url = st.text_input(
            "Enter Google Sheets URL",
            placeholder="Paste your Google Sheets URL here..."
        )
        if url:
            data = load_gsheets(url)
            if data is not None:
                st.sidebar.success("Connected to Google Sheets!")
            return data
    return None