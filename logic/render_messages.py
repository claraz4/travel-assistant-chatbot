import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

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
        if getattr(msg, "tool_calls", None):
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