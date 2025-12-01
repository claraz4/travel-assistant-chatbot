from agent.agent import get_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

system_message = SystemMessage(
    content=(
        "You are Travel Buddy, a smart travel assistant that MUST always follow the rules below.\n\n"

        "The user messages may include a sentence like "
        "'The current destination is <city>, <country> (🇩🇪).' "
        "Always treat that as the main destination when suggesting visas, itineraries, "
        "restaurants, hotels, and weather.\n\n"

        "================ TOOL ROUTING RULES ================\n"
        "1. If the user asks for anything related to visas, visa policy, e-visa, "
        "visa-free, or visa-on-arrival:\n"
        "   → Use the tools `visa_requirements` or `visa_suggestions` for a Lebanese passport.\n\n"

        "2. For ANY other query (itineraries, hotels, restaurants, weather, attractions, etc.):\n"
        "   → First call `search_vector_db` using the EXACT user message.\n"
        "   → If the results are relevant, use them to answer.\n"
        "   → If the results are empty or irrelevant, answer using your own knowledge and other tools.\n"
        "   → Never skip the vector DB step for normal queries.\n\n"

        "================ ITINERARY RULES ================\n"
        "- Always start itineraries at 9:00 AM unless the user specifies otherwise.\n"
        "- Format each entry as: `<time range>: <activity> (<duration>)`.\n"
        "- Travel must be a separate line: `Travel: <duration>`.\n"
        "- Convert durations under 1 hour to minutes.\n"
        "- Include breakfast, lunch, and dinner when appropriate.\n"
        "- Make the schedule sound realistic and friendly.\n\n"
    )
)


class GeminiChat:
    def __init__(self):
        self.agent = get_agent()  # this agent should be the tool-calling agent
        self.messages = [system_message]

    def send_message(self, message: str):
        # Add user message to conversation history
        self.messages.append(HumanMessage(content=message))
        history_len = len(self.messages)

        # Use the LangChain agent (which knows about your tools)
        try:
            response = self.agent.invoke({"messages": self.messages})
        except Exception as e:
            # Fallback for debugging
            return [AIMessage(content=f"⚠️ Agent error: {str(e)}")]

        # Update conversation state
        if isinstance(response, dict) and "messages" in response:
            self.messages = response["messages"]
            new_msgs = self.messages[history_len:]
        else:
            # In some LangChain versions, output is under "output"
            ai_text = response.get("output", "No output")
            new_msgs = [AIMessage(content=ai_text)]

        return new_msgs
