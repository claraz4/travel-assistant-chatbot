import streamlit as st
from agent.chat import GeminiChat
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import asyncio

def extract_text(msg):
    if isinstance(msg.content, str):
        return msg.content
    
    if isinstance(msg.content, list):
        return "".join(
            item.get("text", "") 
            for item in msg.content 
            if isinstance(item, dict) and item.get("type") == "text"
        )
    return ""

def render_message(msg):
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)

    elif isinstance(msg, AIMessage):
        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            with st.chat_message("assistant"):
                with st.status(f"Tool call: {tool_call['name']}"):
                    st.markdown(str(tool_call["args"]))

        else:
            text = extract_text(msg)
            with st.chat_message("assistant"):
                st.markdown(text)

    elif isinstance(msg, ToolMessage):
        with st.chat_message("assistant"):
            with st.status("Tool result:"):
                st.markdown(msg.content)


async def main():
    st.title("Gemini Chat")

    if "llm" not in st.session_state:
        st.session_state.llm = GeminiChat()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render hisstory
    for msg in st.session_state.messages:
        render_message(msg)

    # Get user input
    prompt = st.chat_input("Your message")

    if not prompt:
        return

    # Render user message
    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)
    render_message(user_msg)

    # Generate response
    new_messages = st.session_state.llm.send_message(prompt)

    # Append and render new messages only
    for msg in new_messages:
        st.session_state.messages.append(msg)
        render_message(msg)


asyncio.run(main())
