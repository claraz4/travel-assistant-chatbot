from langchain.agents import create_agent

from tools.add_two_numbers import add_two_numbers
from tools.search_vector_db import search_vector_db
from tools.itinerary_optimizer import itinerary_optimizer
from tools.visa_requirements import visa_requirements, visa_suggestions
from tools.city_weather import get_city_monthly_weather
from tools.hotel_matcher import hotel_matcher
from tools.restaurant_matcher import restaurant_matcher

from agent.llm import get_llm


def get_agent():
    llm = get_llm()

    tools = [
        add_two_numbers,
        search_vector_db,
        itinerary_optimizer,
        visa_requirements,
        visa_suggestions,
        get_city_monthly_weather,
        hotel_matcher,
        restaurant_matcher,
    ]

    agent = create_agent(llm, tools=tools)
    return agent
