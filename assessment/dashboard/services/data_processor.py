import streamlit as st
import ast
import time
import random
from .csv_handler import display_csv_file 
import os
import groq
import csv
from langchain.prompts import ChatPromptTemplate

behaviour_control = ChatPromptTemplate.from_messages([
    ("system", """You are a precise data extraction assistant. You must:
    - Return ONLY a single list in the format ["Type", "Name"] 
    - For population queries, return ["Population", number] (e.g. ["Population", "120000"])
    - Never include any explanatory text
    - Never include any acknowledgments
    - Never include any additional formatting
    - Remove any commas from numbers
    Example correct outputs:
    ["Restaurant", "Mixt"]
    ["Population", "120000"]"""),
    ("human", "Search queries: {search_query}"),
    ("human", "Search results: {one_value}"),
    ("human", """
        Example: 
        - Search query: Best restaurants near Salesforce headquarters
        - Search results: Here are some top-rated restaurants near Salesforce headquarters, including Mixt, a modern Mexican restaurant, and Zuni Café, a renowned Californian restaurant.
        - The best and most relevant result should be returned based on the search query. For instance, even if there are multiple options, choose the most relevant one. 
        - Return a list with two elements: 
          1. The type of place (e.g., "Restaurant", "Cafe", etc.), 
          2. The name of the place (e.g., "Mixt").
        - Example output: ["Restaurant", "Mixt"]
        
        Explanation:
        - The goal is to return **only one** answer, even if multiple options are found.
        - If multiple search results are provided, select the **most relevant** one based on the search query. This means focusing on the highest-rated, most appropriate, or most relevant place.
        - **Do not provide any additional explanation** or details about why that specific result was chosen.
        - The output must always be in the format: [<type>, <name>].
    """),
    ("human", """
        If there are many queries or results, return ONLY ONE final list in the format:
        - First element: Type of place (e.g., "Restaurant")
        - Second element: Name of the place (e.g., "Mixt")
        - Do not explain your process or provide any additional text or reasoning. Just return the list, and **nothing else**.
    """),
    ("human", """Based on the search queries and results, return a single list with exactly two elements:
    1. Type (e.g., "City", "County", "Restaurant", "Population", etc.)
    2. Name or Value (e.g., "London", "Yorkshire", "Mixt", "120000", etc.)
    
    For population data:
    - First element should be "Population"
    - Second element should be the number without commas
    
    You must ONLY return the list, nothing else."""),
    ("human", """If Search queries is 'Population of Buckinghamshire County in current year' and one_value is 'The population of Buckinghamshire County is around 555,300-560,400, with a higher female population and a higher proportion of 5 to 14 year olds compared to the England average. The population has been increasing over the years.' then return ["Population", "558300"] - note this is exactly 2 entries. When the query and results are about population data, do not add irrelevant types like 'City' - always use 'Population' as the type. so always ceck the context of the query""")
])


def extract_unique_selected_columns_data(df, selected_columns):
    """Extract unique combinations of selected columns."""
    if not selected_columns: 
        return None
        
    data = df
    selected_data = data[selected_columns].drop_duplicates().to_dict(orient='records')
    return selected_data

def process_search_queries(selected_columns_data, llm, search_query_prompt, query):
    """First phase: Generate search queries for each entity."""
    if not selected_columns_data:
        st.error("No data to process")
        return False
    # Add progress bar
    progress_bar = st.progress(0)
    total_items = len(selected_columns_data)

    for i, entity_data in enumerate(selected_columns_data):
        # Update progress bar
        progress = (i + 1) / total_items
        progress_bar.progress(progress, f"Processing {i+1} of {total_items} entities")

        max_retries = 3  # Maximum number of retries for empty search_queries
        retry_count = 0

        while retry_count < max_retries:  # Keep trying until successful or max retries reached
            try:
                # Generate the prompt
                prompt = search_query_prompt.format(
                    user_query=query,
                    selected_columns_data=entity_data
                )
                
                # Invoke the LLM to get the response
                search_query = llm.invoke(prompt).content

                try:
                    start_index = search_query.find('[')
                    end_index = search_query.rfind(']')
                    
                    # Extract the substring and strip any leading/trailing whitespace
                    queries_str = search_query[start_index:end_index+1].strip()
                    
                    # Convert the string into a Python list using eval() (since it should be a valid list format)
                    if queries_str:
                        queries_list = eval(queries_str)  # eval is safe here as the structure is predefined and controlled
                        entity_data['search_queries'] = queries_list
                        if queries_list:  # If we got valid queries, break the retry loop
                            break
                    else:
                        entity_data['search_queries'] = []
                except Exception as e:
                    # If there's an error in parsing the list, set the search_queries to an empty list
                    entity_data['search_queries'] = []

                # If search_queries is empty, increment retry counter
                if not entity_data.get('search_queries'):
                    retry_count += 1
                    st.warning(f"Empty search queries for item {i+1}, attempt {retry_count}/{max_retries}")
                    time.sleep(2)
                    continue
                
                time.sleep(2)  # Base rate limiting
                break  # Success, move to next entity

            except Exception as e:
                if "rate_limit_exceeded" in str(e).lower():
                    st.warning(f"Rate limit reached at item {i+1}/{len(selected_columns_data)}. Waiting 3 seconds...")
                    time.sleep(3)
                    continue  # Retry the same entity
                else:
                    st.error(f"Error processing query at entity {i+1}: {e}")
                    entity_data['search_queries'] = []
                    break  # Move to the next entity for non-rate-limit errors
        if retry_count == max_retries:
            st.error(f"Failed to get valid search queries for item {i+1} after {max_retries} attempts")

    
    st.write("Finished processing all entities.")
    return True

def process_queries_with_delay(entities, agent_executor, delay_range=(0, 7), max_queries=3):
    """Process queries with random delays between requests and limit per entity"""
    
    # Create progress bars
    entity_progress = st.progress(0, "Overall Progress")
    query_progress = st.empty()  # Placeholder for query progress text
    total_entities = len(entities)
    
    try:
        for entity_idx, entity in enumerate(entities):
            # Update entity progress
            entity_progress.progress(
                entity_idx / total_entities, 
                f"Processing({entity_idx + 1}/{total_entities})"
            )
            
            entity['one_value'] = []
            # Skip if search_queries is empty or None
            if not entity.get('search_queries'):
                continue
                
            # Limit the number of queries per entity
            queries = entity['search_queries'][:max_queries]  # Take only first 3 queries
            total_queries = len(queries)
            
            for query_idx, query in enumerate(queries):
                try:
                    # Update query progress
                    query_text = query if isinstance(query, str) else " ".join(str(x) for x in query)
                    query_progress.info(
                        f"Searching ({query_idx + 1}/{total_queries}): {query_text[:50]}..."
                    )
                    
                    result = agent_executor.invoke({"input": query})
                    entity['one_value'].append(result['output'])
                    time.sleep(random.uniform(*delay_range))
                    
                except Exception as e:
                    st.warning(f"Error processing query for {entity.get('County', 'Unknown')}: {e}")
                    entity['one_value'].append("Error")

        # Show completion message
        entity_progress.progress(1.0, "Processing Complete!")
    except Exception as e:
        st.error(f"Error processing queries: {e}")    
        
    finally:   # Clear progress indicators
        entity_progress.empty()
        query_progress.empty()
        
        # Show completion message
    st.success("All queries have been processed!")


def process_entities(selected_columns_data, agent_executor):
    """Third phase: Process entities with the agent"""
    if not agent_executor:
        st.error("Agent executor not initialized")
        return False
    
    try:
        process_queries_with_delay(
            selected_columns_data, 
            agent_executor,
            delay_range=(1, 3),
            max_queries=3
        )
        return True
    except Exception as e:
        st.error(f"Error processing entities: {e}")
        return False


def final_processing(selected_columns_data, llm2, behaviour_control):
    """Fourth phase: Final processing and CSV generation"""
    try:
        # Verify API key is available and valid
        api_key = os.environ.get("GROQ_API_KEY_2")
        if not api_key:
            st.error("Missing GROQ_API_KEY_2 in environment variables")
            return False
            
        for dict_element in selected_columns_data:
            while True:  # Add retry loop for rate limits
                try:
                    chain_input = {
                        "search_query": "\n".join(dict_element['search_queries']),
                        "one_value": "\n".join(dict_element['one_value'])
                    }
                    
                    chain = behaviour_control | llm2
                    response = chain.invoke(chain_input)
                    
                    response_list = ast.literal_eval(response.content)
                    dict_element[response_list[0]] = response_list[1]
                    
                    # Add delay between requests
                    time.sleep(2)
                    break  # Success - exit retry loop
                    
                except groq.RateLimitError as e:
                    print(f"Rate limit reached. Waiting for 30 seconds...")
                    time.sleep(39)  # Wait for rate limit reset
                    continue  # Retry the same element
                except Exception as e:
                    print(f"Error processing element: {e}")
                    break  # Exit retry loop on non-rate-limit errors
        
        # Collect all unique keys from all dictionaries
        all_keys = set()
        for dict_element in selected_columns_data:
            all_keys.update(dict_element.keys())
        
        # Filter out processing keys and create final columns list
        columns = [key for key in all_keys 
                  if key not in ['search_queries', 'one_value']]
        
        # Generate CSV
        with open('output.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            for dict_element in selected_columns_data:
                data_for_csv = {
                    key: (', '.join(str(v) for v in value) if isinstance(value, list) else value) 
                    for key, value in dict_element.items() 
                    if key not in ['search_queries', 'one_value']
                }
                writer.writerow(data_for_csv)
        
        st.success("CSV file has been created successfully.")
        display_csv_file("output.csv")
        return True
    except Exception as e:
        st.error(f"Error in final processing: {e}")
        return False
