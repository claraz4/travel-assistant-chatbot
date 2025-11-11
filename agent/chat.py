from agent.agent import get_agent
from langchain_core.messages import HumanMessage, SystemMessage

system_message = SystemMessage(
    content=(
        "For every user query, you MUST first call the tool 'search_vector_db' "
        "using the exact user query as input.\n\n"
        
        "After retrieving the search results:\n"
        "1. If the vector database returns relevant information, USE IT to answer the user.\n"
        "2. If the vector database returns empty or irrelevant results, THEN answer "
        "the user using your own reasoning and general knowledge.\n\n"
        
        "Always begin by calling 'search_vector_db'. Never skip this step."
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

