import streamlit as st
from agent.chat import GeminiChat
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import asyncio
import base64

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
    st.title("Your Travel Buddy")
    
    
    file_path = "/Users/gaelletohme/travel-assistant-chatbot/pictures/dCXxwH.jpg" 
    with open(file_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()

    page_bg = f"""
    <style>
    h1 {{
    color: black !important;
    text-shadow: none !important;
}}
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    [data-testid="stSidebar"] {{
        background: rgba(255,255,255,0.8);
    }}
    
   /*  User message (slightly stronger blue bubble) */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background: rgba(135, 206, 250, 1); 
    border-radius: 18px;
    padding: 10px 16px;
    margin-bottom: 10px;
}}

/*  Assistant message (stronger navy bubble) */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
    background: rgba(0, 51, 102, 1); 
    border-radius: 18px;
    padding: 10px 16px;
    margin-bottom: 10px;
   
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) span,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) div {{
    color: white !important;      
}}
    </style>
    """

    st.markdown(page_bg, unsafe_allow_html=True)

    if "llm" not in st.session_state:
        st.session_state.llm = GeminiChat()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render hisstory
    for msg in st.session_state.messages:

        if isinstance(msg, SystemMessage):
            continue
        with st.chat_message("assistant" if isinstance(msg, AIMessage) else "user"):
            st.markdown(msg.content)


        render_message(msg)

    # Get user input

    prompt = st.chat_input("Your message")

    if not prompt:
        return


        new_messages = st.session_state.llm.send_message(prompt)
        
        for msg in new_messages:
            if isinstance(msg, AIMessage) and getattr(msg, "text", None):
                st.session_state.messages.append(AIMessage(content=msg.text))
                with st.chat_message("assistant"):
                    st.markdown(msg.text)

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
