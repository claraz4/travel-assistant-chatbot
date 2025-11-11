import streamlit as st
from agent.chat import GeminiChat
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
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
        with st.chat_message("assistant" if isinstance(msg, AIMessage) else "user"):
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


asyncio.run(main())
