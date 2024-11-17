from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, Tool, create_xml_agent
from langchain.agents.output_parsers import XMLAgentOutputParser
from langchain_community.tools import DuckDuckGoSearchResults
from langchain import hub
import streamlit as st
import time
import os


def initialize_llm():
    """Initialize LLM instances"""
    llm1 = ChatGroq(
        model_name="mixtral-8x7b-32768",
        temperature=0.0,
        api_key=os.environ.get("GROQ_API_KEY_1")
    )
    llm2 = ChatGroq(
        model_name="mixtral-8x7b-32768",
        temperature=0.0,
        api_key=os.environ.get("GROQ_API_KEY_2")
    )
    return llm1, llm2

def get_search_query_prompt():
    """Initialize search query prompt template"""
    return ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that generates highly relevant search queries to retrieve information"),
        ("human", "Based on the user's query and the provided data, generate up to 2 of the most effective search queries that would likely yield relevant results."),
        ("human", "User's query: {user_query}"),
        ("human", "Data from selected columns: {selected_columns_data}"),
        ("human", "Return the two best queries as a list."),
        ("human", "If the data is not relevant to the user's query or if data is ambiguous or if you have even 5 percent of doubt, return an empty list."),
        ("human", "use the relevant data from selected columns to generate the queries.")
    ])

def convert_intermediate_steps(intermediate_steps):
    log = ""
    for action, observation in intermediate_steps:
        log += (
            f"<tool>{action.tool}</tool>"
            f"<tool_input>{action.tool_input}</tool_input>"
            f"<observation>{observation}</observation>"
        )
    return log

def convert_tool(tools):
    return "\n".join([f"{tool.name} : {tool.description}" for tool in tools])

def setup_agent_executor(llm):
    """Second phase: Set up the agent executor"""
    try:
        prompt_hub = hub.pull("hwchase17/xml-agent-convo")
        
        def search(query: str) -> str:
            """search about things with duckduckgo engine"""
            _search = DuckDuckGoSearchResults()
            return _search.run(query)
        
        # Properly define the tool
        search_tool = Tool(
            name="search",
            func=search,
            description="search about things with duckduckgo engine"
        )
        
        tool_list = [search_tool]

        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: convert_intermediate_steps(x["intermediate_steps"]),
                "tools": lambda x: convert_tool(tool_list)
            }
            | prompt_hub
            | llm.bind(stop=["</tool_input>", "</final_answer>"])
            | XMLAgentOutputParser()
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tool_list,
            verbose=True,
            handle_parsing_errors=True
        )
    except Exception as e:
        st.error(f"Error setting up agent executor: {e}")
        return None


# ... Move convert_intermediate_steps, convert_tool, setup_agent_executor here ...