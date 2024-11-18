import streamlit as st
from components.styles import load_css
from components.header import display_header
from components.data_loader import (
    show_data_source_selector,
    handle_file_upload,
    handle_gsheets_connection
)
from components.data_display import (
    show_metrics,
    show_column_selector,
    display_dataframe,
    show_query_input,
    show_welcome_message
)
from services.csv_handler import generate_csv, display_csv_file

from utils.state_management import initialize_session_state
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from services.data_processor import (
    extract_unique_selected_columns_data,
    process_search_queries,
    process_queries_with_delay,
    final_processing,
    behaviour_control
)
from services.llm_service import setup_agent_executor
import json



def main():
    # Load environment variables and initialize LLM components first
    load_dotenv()
    
    # Initialize LLM
    llm = ChatGroq(model_name="mixtral-8x7b-32768",
                   temperature=0.0,
                   api_key=os.environ.get("GROQ_API_KEY_1"))
    llm2 = ChatGroq(model_name="mixtral-8x7b-32768",
                   temperature=0.0,
                   api_key=os.environ.get("GROQ_API_KEY_2"))

    # Initialize search query prompt template
    search_query_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that generates highly relevant search queries to retrieve information"),
        ("human", "Based on the user's query and the provided data, generate up to 2 of the most effective search queries that would likely yield relevant results."),
        ("human", "User's query: {user_query}"),
        ("human", "Data from selected columns: {selected_columns_data}"),
        ("human", "Return the two best queries as a list."),
        ("human", "If the data is not relevant to the user's query or if data is ambiguous or if you have even 5 percent of doubt, return an empty list."),
        ("human", "use the relevant data from selected columns to generate the queries.")
    ])

    # Page configuration
    st.set_page_config(layout="wide", page_title="Inventory Dashboard")
    
    # Load CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Display header
    display_header()
    
    # Initialize session state
    initialize_session_state()
    
    # Show data source selector
    data_source = show_data_source_selector()
    
    # Handle data loading
    if data_source == "Upload File":
        st.session_state.data = handle_file_upload()
    else:
        st.session_state.data = handle_gsheets_connection()
    
    # Display data and visualizations if data is loaded
    if st.session_state.data is not None:
        df = st.session_state.data

        show_metrics(df)
        
        selected_columns = show_column_selector(df)
        # Add this line to display the uploaded CSV
        display_dataframe(df)
        
        
        if selected_columns:
            selected_columns_data = extract_unique_selected_columns_data(df, selected_columns)
            st.write(f"Selected columns data length: {len(selected_columns_data)}")
            
            if selected_columns_data:
                query = show_query_input(selected_columns)
                
                # Only proceed with processing if query is not None (Enter was pressed)
                if query:
                    # Phase 1: Generate search queries
                    with st.spinner("Generating search queries..."):
                        if not process_search_queries(selected_columns_data, llm, search_query_prompt, query):
                            st.stop()
                    
                    # Phase 2: Setup agent executor
                    st.divider()
                    with st.spinner("Setting up agent..."):
                        agent_executor = setup_agent_executor(llm)
                        if not agent_executor:
                            st.stop()
                        
                    for entity in selected_columns_data:
                        print(entity)
                    # Phase 3: Process entities
                    with st.spinner("Processing search results..."):
                        st.write("Agent executor created")
                        process_queries_with_delay(selected_columns_data, agent_executor, delay_range=(1, 3))
                    
                    st.divider()
                    # Save selected_columns_data to a file
                    # Phase 4: Final processing and CSV generation
                    with st.spinner("Generating final results..."):
                        if not final_processing(selected_columns_data, llm2, behaviour_control):
                            st.stop()
                    with open('selected_columns_data.json', 'w') as f:
                        json.dump(selected_columns_data, f, indent=4)
            else:
                st.warning("No data to process from selected columns")
        else:
            st.warning("Please select columns to process")
    else:
        show_welcome_message()


if __name__ == "__main__":
    main()
    
    
