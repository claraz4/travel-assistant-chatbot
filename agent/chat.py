from agent.agent import get_agent
from langchain_core.messages import HumanMessage, SystemMessage

system_message = SystemMessage(
    content=(
        "You are a travel assistant.\n\n"

        "1 TOOL USE POLICY:\n"
        "- For every user query, you MUST first call the tool `search_vector_db` "
        "using the exact user query as input.\n"
        "- If the results are relevant, use them to answer.\n"
        "- If they are empty or irrelevant, use your general knowledge.\n"
        "- Never skip the `search_vector_db` call.\n\n"

        "2 ITINERARY FORMATTING RULES:\n"
        "- Always start itineraries at 9:00 AM unless the user specifies otherwise.\n"
        "- Show each activity as a new line in the form:\n"
        "  `<time range>: <activity> (<duration>)`\n"
        "- Add a separate line for travel, labeled clearly as `Travel: <duration>`.\n"
        "- If a duration is less than 1 hour, show it in minutes.\n"
        "- Use natural language to make the schedule sound friendly and realistic.\n"
        "- Do not put travel time in parentheses.\n"
        "- Account the ideal time for breakfast, lunch, and dinner if applicable.\n\n"
    )
)

class GeminiChat:
    def __init__(self):
        self.agent = get_agent()
        self.messages = [system_message]

    def send_message(self, message: str):
        self.messages.append(HumanMessage(content=message))
        history_len = len(self.messages)

        self.messages = self.agent.invoke({"messages": self.messages})["messages"]
        return self.messages[history_len:]

