from langchain.agents import create_agent
from tools.add_two_numbers import add_two_numbers
from tools.search_vector_db import search_vector_db
from agent.llm import get_llm
from tools.visa_requirements import visa_requirements, visa_suggestions

def get_agent():
    llm = get_llm()
    tools = [add_two_numbers, search_vector_db, visa_requirements,visa_suggestions]
    agent = create_agent(llm, tools=tools)
    return agent
