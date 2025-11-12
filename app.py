import streamlit as st
from agent.chat import GeminiChat
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
import asyncio

async def main():
    st.title("Gemini Chat")

    if "llm" not in st.session_state:
        st.session_state.llm = GeminiChat()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        if isinstance(msg, SystemMessage):
            continue
        if isinstance(msg, AIMessage):
            with st.chat_message("assistant" if isinstance(msg, AIMessage) else "user"):
                st.markdown(msg.text)
        # Handle AI message without content (tool call)
        elif isinstance(msg, AIMessage) and not msg.content:
            with st.chat_message("assistant"):
                # Extract tool name and arguments from the tool call
                tool_name = msg.tool_calls[0]['name']
                tool_args = str(msg.tool_calls[0]['args'])
                # Display tool call details with status indicator
                with st.status(f"Tool call: {tool_name}"):
                    st.markdown(tool_args)
        # Handle tool execution result message
        elif isinstance(msg, ToolMessage):
            with st.chat_message("assistant"):
                # Display tool execution result with status indicator
                with st.status("Tool result: "):
                    st.markdown(msg.content)
        # Handle user message
        elif isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)


    prompt = st.chat_input("Your message")

    if prompt:
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        new_messages = st.session_state.llm.send_message(prompt)
        
        for msg in new_messages:
            if isinstance(msg, AIMessage) and msg.text:
                st.session_state.messages.append(AIMessage(content=msg.text))
                with st.chat_message("assistant"):
                    st.markdown(msg.text)
            elif isinstance(msg, AIMessage) and not msg.content:
                # Handle AI message that contains a tool call
                with st.chat_message("assistant"):
                    # Extract tool name and arguments from the tool call
                    tool_name = msg.tool_calls[0]['name']
                    tool_args = str(msg.tool_calls[0]['args'])
                    # Display tool call details with status indicator
                    with st.status(f"Tool call: {tool_name}"):
                        st.markdown(tool_args)
            elif isinstance(msg, ToolMessage):
                # Display the result returned from tool execution
                with st.chat_message("assistant"):
                    with st.status("Tool result: "):
                        st.markdown(msg.content)
            elif isinstance(msg, HumanMessage):
                # Display user's message
                with st.chat_message("user"):
                    st.markdown(msg.content)


asyncio.run(main())
