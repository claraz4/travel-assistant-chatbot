from langchain.agents import create_agent
from tools.add_two_numbers import add_two_numbers
from tools.search_vector_db import search_vector_db
from tools.itinerary_optimizer import itinerary_optimizer
from agent.llm import get_llm

def get_agent():
    llm = get_llm()
    tools = [add_two_numbers, search_vector_db, itinerary_optimizer]
    agent = create_agent(llm, tools=tools)
    return agent
