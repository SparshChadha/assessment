import pandas as pd
import streamlit as st
import csv

def generate_csv(selected_columns_data):
    """Generate CSV file from processed data."""
    columns = [key for key in selected_columns_data[0].keys() 
              if key not in ['search_queries', 'one_value']]
    
    with open('output.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for dict_element in selected_columns_data:
            data_for_csv = {
                key: (', '.join(str(v) for v in value) if isinstance(value, list) else value) 
                for key, value in dict_element.items() 
                if key not in ['search_queries', 'one_value']
            }
            writer.writerow(data_for_csv)

def display_csv_file(file_path):
    """Display the generated CSV file as a downloadable link and preview."""
    with open(file_path, 'rb') as file:
        st.download_button(
            label="Download CSV",
            data=file,
            file_name="output.csv",
            mime="text/csv"
        )
    # Show preview of the CSV
    df = pd.read_csv(file_path)
    st.dataframe(df)
