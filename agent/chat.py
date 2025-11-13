from agent.agent import get_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

system_message = SystemMessage(
    content=(

        "For every user query:\n"
        "1. If it’s about visas, visa policy, e-visa, visa-free, or visa-on-arrival, "
        "use the `visa_requirements` or `visa_suggestions` tool.\n"
        "2. Otherwise, first call the tool `search_vector_db` using the exact user query as input.\n"
        "   - If it returns relevant info, use it to answer.\n"
        "   - If it’s empty or irrelevant, use your own reasoning.\n\n"
        "Never skip these steps."

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
