import streamlit as st

def show_metrics(df):
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Records", value=f"{len(df):,}")
    with col2:
        st.metric(label="Total Columns", value=f"{len(df.columns):,}")

def show_column_selector(df):
    selected_columns = st.multiselect(
        "Select columns",
        options=df.columns.tolist(),
        default=[],
        help="Choose the columns you want to write custom query on",
        placeholder="Select columns..."
    )
    
    if len(selected_columns) == len(df.columns):
        st.write(":green[All columns are selected]")
    
    return selected_columns

def display_dataframe(df):
    st.dataframe(df, use_container_width=True, height=400)

def show_query_input(selected_columns):
    if selected_columns:
        # Show selected columns for reference
        st.markdown("### Selected Columns:")
        cols_display = ", ".join([f"`{col}`" for col in selected_columns])
        st.markdown(f"You can query about: {cols_display}")
        
        # Example queries based on selected column
        # Query input with dynamic placeholder
        query = st.text_input(
            "Write your query here...",
            key="query",
            help=f"Write your question about {', '.join(selected_columns)}",
            placeholder=f""
        )
        
        # Return the query for further processing
        return query

def show_welcome_message():
    st.markdown("""
        ### Welcome to the AI Data Extraction Dashboard!
        
        Please upload your data using one of the following methods:
        1. Upload a CSV file using the file uploader
        2. Connect to a Google Sheet by providing the URL
        
        Once your data is loaded, you'll be able to:
        - Select the primary column containing entities (e.g., companies, counties)
        - Create custom search queries using placeholders
        - View extracted information from web searches
        - Download results as CSV or update Google Sheet
    """)